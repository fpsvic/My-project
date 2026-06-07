using UnityEngine;
using UnityEngine.InputSystem;

public class MeleeAttack : MonoBehaviour
{
    [SerializeField] float range = 2.2f;
    [SerializeField] float damage = 1f;
    [SerializeField] float cooldown = 0.45f;

    string weaponName = "Rusty Blade";
    float cooldownTimer;

    public string WeaponName => weaponName;
    public float Damage => damage;

    public void ApplyWeaponStats(float newDamage, float newRange, float newCooldown, string newWeaponName)
    {
        damage = newDamage;
        range = newRange;
        cooldown = newCooldown;
        weaponName = newWeaponName;
    }

    void Update()
    {
        cooldownTimer -= Time.deltaTime;
        if (cooldownTimer > 0f)
            return;

        if (Keyboard.current == null || !Keyboard.current.aKey.wasPressedThisFrame)
            return;

        cooldownTimer = cooldown;
        PerformAttack();
    }

    void PerformAttack()
    {
        Vector3 center = transform.position + transform.forward * (range * 0.5f) + Vector3.up;
        var hits = Physics.OverlapSphere(center, range * 0.55f);
        foreach (var hit in hits)
        {
            if (hit.transform == transform || hit.transform.IsChildOf(transform))
                continue;

            var enemy = hit.GetComponentInParent<ArenaEnemy>();
            if (enemy != null)
                enemy.TakeDamage(damage, true);
        }
    }
}
