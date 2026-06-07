using UnityEngine;

public class ArenaEnemy : MonoBehaviour
{
    [SerializeField] float moveSpeed = 2.5f;
    [SerializeField] float attackRange = 1.4f;
    [SerializeField] float attackCooldown = 1.2f;
    [SerializeField] int maxHealth = 2;
    [SerializeField] int contactDamage = 1;

    Transform player;
    float health;
    float attackTimer;

    void Start()
    {
        health = maxHealth;
        var playerObject = GameObject.FindGameObjectWithTag("Player");
        if (playerObject != null)
            player = playerObject.transform;
    }

    void Update()
    {
        if (player == null || health <= 0f)
            return;

        Vector3 toPlayer = player.position - transform.position;
        toPlayer.y = 0f;
        float distance = toPlayer.magnitude;

        if (distance > attackRange)
        {
            transform.position += toPlayer.normalized * (moveSpeed * Time.deltaTime);
            if (toPlayer.sqrMagnitude > 0.01f)
                transform.rotation = Quaternion.LookRotation(toPlayer);
            return;
        }

        attackTimer -= Time.deltaTime;
        if (attackTimer > 0f)
            return;

        attackTimer = attackCooldown;
        var playerHealth = player.GetComponent<PlayerHealth>();
        playerHealth?.TakeDamage(contactDamage);
    }

    public void TakeDamage(float amount)
    {
        health -= amount;
        if (health <= 0f)
        {
            BladeArenaGame.Instance?.OnEnemyDefeated();
            Destroy(gameObject);
        }
    }
}
