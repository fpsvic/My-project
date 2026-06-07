using UnityEngine;
using UnityEngine.InputSystem;

public class MeleeAttack : MonoBehaviour
{
    [SerializeField] float range = 2.2f;
    [SerializeField] float damage = 1f;
    [SerializeField] float cooldown = 0.45f;

    float cooldownTimer;

    void Update()
    {
        cooldownTimer -= Time.deltaTime;
        if (cooldownTimer > 0f)
            return;

        if (Keyboard.current == null || !Keyboard.current.spaceKey.wasPressedThisFrame)
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
                enemy.TakeDamage(damage);
        }
    }
}
