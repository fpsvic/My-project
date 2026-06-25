using UnityEngine;

namespace BladeBattle
{
    /// <summary>
    /// Simple melee enemy: chases the player, attacks on contact, takes knockback,
    /// and reports its death to the GameManager.
    /// </summary>
    [RequireComponent(typeof(CharacterController))]
    [RequireComponent(typeof(Health))]
    public class EnemyAI : MonoBehaviour
    {
        public float moveSpeed = 3.6f;
        public float attackRange = 2.2f;
        public float attackDamage = 12f;
        public float attackCooldown = 1.1f;
        public float turnSpeed = 8f;

        Transform _target;
        CharacterController _cc;
        Health _health;
        Transform _weapon;
        Quaternion _weaponRest;

        Vector3 _velocityY;
        Vector3 _knockback;
        float _attackTimer;
        float _attackAnim;
        bool _dead;

        public void Init(Transform player, float hp, float speed, float damage)
        {
            _target = player;
            moveSpeed = speed;
            attackDamage = damage;
            _cc = GetComponent<CharacterController>();
            _health = GetComponent<Health>();
            _health.Configure(hp, false);
            _health.OnDeath += OnDeath;
            _weapon = transform.Find("WeaponPivot");
            if (_weapon != null) _weaponRest = _weapon.localRotation;
            var flash = GetComponent<HitFlash>();
            if (flash != null) flash.Init();
        }

        public void ApplyKnockback(Vector3 force)
        {
            _knockback += force;
        }

        void OnDeath(GameObject killer)
        {
            if (_dead) return;
            _dead = true;
            GameManager.Instance?.OnEnemyKilled(transform.position);
            // Collapse and fade out.
            Destroy(gameObject, 0.05f);
        }

        void Update()
        {
            if (_dead || _target == null || _cc == null) return;

            Vector3 to = _target.position - transform.position;
            to.y = 0f;
            float dist = to.magnitude;
            Vector3 dir = dist > 0.001f ? to / dist : Vector3.zero;

            // Face the player.
            if (dir.sqrMagnitude > 0.001f)
            {
                Quaternion look = Quaternion.LookRotation(dir, Vector3.up);
                transform.rotation = Quaternion.Slerp(transform.rotation, look, turnSpeed * Time.deltaTime);
            }

            // Move toward the player until in attack range.
            Vector3 horizontal = Vector3.zero;
            if (dist > attackRange * 0.9f)
                horizontal = dir * moveSpeed;
            else
                TryAttack(dist);

            // Gravity.
            if (_cc.isGrounded && _velocityY.y < 0f) _velocityY.y = -2f;
            _velocityY.y += -22f * Time.deltaTime;

            // Knockback decays quickly.
            _knockback = Vector3.Lerp(_knockback, Vector3.zero, 10f * Time.deltaTime);

            Vector3 motion = horizontal + _knockback + Vector3.up * _velocityY.y;
            _cc.Move(motion * Time.deltaTime);

            AnimateWeapon();

            if (transform.position.y < -30f) Destroy(gameObject);
        }

        void TryAttack(float dist)
        {
            _attackTimer -= Time.deltaTime;
            if (_attackTimer > 0f) return;
            if (dist > attackRange) return;

            _attackTimer = attackCooldown;
            _attackAnim = 1f;
            var hp = _target.GetComponent<Health>();
            if (hp != null) hp.TakeDamage(attackDamage, gameObject);
        }

        void AnimateWeapon()
        {
            if (_weapon == null) return;
            if (_attackAnim > 0f) _attackAnim -= Time.deltaTime * 4f;
            float a = Mathf.Clamp01(_attackAnim);
            _weapon.localRotation = _weaponRest * Quaternion.Euler(-Mathf.Sin(a * Mathf.PI) * 80f, 0f, 0f);
        }
    }
}
