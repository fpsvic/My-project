using UnityEngine;

public class ArenaEnemy : MonoBehaviour
{
    [SerializeField] float moveSpeed = 2.5f;
    [SerializeField] float attackRange = 1.4f;
    [SerializeField] float detectionRange = 18f;
    [SerializeField] float attackCooldown = 1.2f;
    [SerializeField] float maxHealth = 2f;
    [SerializeField] float contactDamage = 1f;
    [SerializeField] float playerTargetWeight = 1.15f;

    Transform currentTarget;
    float health;
    float attackTimer;

    void Start()
    {
        health = maxHealth;
        PickTarget();
    }

    void Update()
    {
        if (health <= 0f)
            return;

        if (currentTarget == null || !currentTarget.gameObject.activeInHierarchy)
            PickTarget();

        if (currentTarget == null)
            return;

        Vector3 toTarget = currentTarget.position - transform.position;
        toTarget.y = 0f;
        float distance = toTarget.magnitude;

        if (distance > attackRange)
        {
            transform.position += toTarget.normalized * (moveSpeed * Time.deltaTime);
            if (toTarget.sqrMagnitude > 0.01f)
                transform.rotation = Quaternion.LookRotation(toTarget);
            return;
        }

        attackTimer -= Time.deltaTime;
        if (attackTimer > 0f)
            return;

        attackTimer = attackCooldown;
        AttackTarget(currentTarget);
    }

    void PickTarget()
    {
        currentTarget = null;
        float bestScore = float.MaxValue;

        var player = GameObject.FindGameObjectWithTag("Player");
        if (player != null)
        {
            float distance = Vector3.Distance(transform.position, player.transform.position);
            if (distance <= detectionRange)
            {
                bestScore = distance / playerTargetWeight;
                currentTarget = player.transform;
            }
        }

        var enemies = FindObjectsByType<ArenaEnemy>(FindObjectsSortMode.None);
        foreach (var enemy in enemies)
        {
            if (enemy == this)
                continue;

            float distance = Vector3.Distance(transform.position, enemy.transform.position);
            if (distance > detectionRange || distance >= bestScore)
                continue;

            bestScore = distance;
            currentTarget = enemy.transform;
        }
    }

    void AttackTarget(Transform target)
    {
        var playerHealth = target.GetComponent<PlayerHealth>();
        if (playerHealth != null)
        {
            playerHealth.TakeDamage(Mathf.RoundToInt(contactDamage));
            return;
        }

        var enemy = target.GetComponent<ArenaEnemy>();
        if (enemy != null)
            enemy.TakeDamage(contactDamage, false);
    }

    public void TakeDamage(float amount, bool awardPlayer)
    {
        health -= amount;
        if (health > 0f)
            return;

        if (awardPlayer)
            BladeArenaGame.Instance?.OnEnemyDefeated();

        Destroy(gameObject);
    }
}
