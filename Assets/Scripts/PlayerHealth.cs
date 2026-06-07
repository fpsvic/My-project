using UnityEngine;

public class PlayerHealth : MonoBehaviour
{
    [SerializeField] int maxHealth = 5;

    public int CurrentHealth { get; private set; }
    public bool IsDead => CurrentHealth <= 0;

    void Awake()
    {
        CurrentHealth = maxHealth;
    }

    public void TakeDamage(int amount)
    {
        if (IsDead)
            return;

        CurrentHealth = Mathf.Max(0, CurrentHealth - amount);
        if (IsDead)
            BladeArenaGame.Instance?.OnPlayerDefeated();
    }

    public void ResetHealth()
    {
        CurrentHealth = maxHealth;
    }
}
