using System.Collections.Generic;
using UnityEngine;
using UnityEngine.InputSystem;

namespace BladeBattle
{
    /// <summary>
    /// Blade melee combat: left-click swings the sword in an arc and deals damage to
    /// enemies in a frontal cone. Chained clicks build a combo for bonus damage.
    /// </summary>
    public class PlayerCombat : MonoBehaviour
    {
        public Transform bladePivot;   // visual sword pivot to animate
        public float damage = 34f;
        public float range = 2.6f;
        public float coneDegrees = 130f;
        public float swingDuration = 0.32f;
        public float comboWindow = 0.9f;

        float _swingTimer;
        bool _swinging;
        bool _didHit;
        int _combo;
        float _lastSwingTime = -10f;
        Quaternion _bladeRest;
        readonly HashSet<Health> _hitThisSwing = new HashSet<Health>();

        public int Combo => _combo;
        public System.Action<int> OnCombo;
        public System.Action OnSwing;

        public void Init(Transform blade)
        {
            bladePivot = blade;
            if (bladePivot != null) _bladeRest = bladePivot.localRotation;
        }

        void Update()
        {
            var mouse = Mouse.current;
            bool attackPressed = mouse != null && mouse.leftButton.wasPressedThisFrame;
            // Allow keyboard fallback (J / Enter) too.
            var kb = Keyboard.current;
            if (kb != null && (kb.jKey.wasPressedThisFrame || kb.enterKey.wasPressedThisFrame))
                attackPressed = true;

            if (attackPressed && !_swinging && Cursor.lockState == CursorLockMode.Locked)
                StartSwing();

            if (_swinging) TickSwing();
            else if (bladePivot != null)
                bladePivot.localRotation = Quaternion.Slerp(bladePivot.localRotation, _bladeRest, 12f * Time.deltaTime);

            // Combo decays if you wait too long.
            if (_combo > 0 && Time.time - _lastSwingTime > comboWindow)
            {
                _combo = 0;
                OnCombo?.Invoke(_combo);
            }
        }

        void StartSwing()
        {
            _swinging = true;
            _didHit = false;
            _swingTimer = 0f;
            _hitThisSwing.Clear();

            if (Time.time - _lastSwingTime <= comboWindow) _combo++;
            else _combo = 1;
            _lastSwingTime = Time.time;
            OnCombo?.Invoke(_combo);
            OnSwing?.Invoke();
        }

        void TickSwing()
        {
            _swingTimer += Time.deltaTime;
            float t = Mathf.Clamp01(_swingTimer / swingDuration);

            // Animate the blade through an arc (alternate side each combo step).
            if (bladePivot != null)
            {
                float dir = (_combo % 2 == 0) ? -1f : 1f;
                float arc = Mathf.Sin(t * Mathf.PI);             // 0->1->0
                float swing = Mathf.Lerp(110f * dir, -110f * dir, t);
                bladePivot.localRotation = _bladeRest *
                    Quaternion.Euler(-arc * 70f, 0f, swing);
            }

            // Deal damage at the mid-point of the swing.
            if (!_didHit && t >= 0.35f)
            {
                _didHit = true;
                DealDamage();
            }

            if (t >= 1f) _swinging = false;
        }

        void DealDamage()
        {
            float bonus = 1f + Mathf.Min(_combo - 1, 4) * 0.12f;   // up to +48%
            Collider[] hits = Physics.OverlapSphere(transform.position + Vector3.up * 1f, range);
            bool any = false;
            foreach (var c in hits)
            {
                var hp = c.GetComponentInParent<Health>();
                if (hp == null || hp == GetComponent<Health>() || hp.IsPlayer) continue;
                if (_hitThisSwing.Contains(hp)) continue;

                Vector3 to = c.transform.position - transform.position;
                to.y = 0f;
                if (to.sqrMagnitude > range * range) continue;
                if (Vector3.Angle(transform.forward, to) > coneDegrees * 0.5f) continue;

                _hitThisSwing.Add(hp);
                hp.TakeDamage(damage * bonus, gameObject);
                var flash = hp.GetComponent<HitFlash>();
                if (flash != null) flash.Flash();

                // Knockback if the enemy supports it.
                var ai = hp.GetComponent<EnemyAI>();
                if (ai != null) ai.ApplyKnockback(to.normalized * 4f);
                any = true;
            }
            if (any) DamagePopup.SpawnAt(transform.position + transform.forward * 1.5f + Vector3.up * 2f,
                                        _combo > 1 ? $"x{_combo}!" : "HIT");
        }
    }
}
