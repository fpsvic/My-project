using System;
using UnityEngine;

namespace BladeBattle
{
    /// <summary>Generic health/damage component used by the player and enemies.</summary>
    public class Health : MonoBehaviour
    {
        [SerializeField] float maxHealth = 100f;
        public float Max => maxHealth;
        public float Current { get; private set; }
        public bool IsDead { get; private set; }

        /// <summary>(current, max)</summary>
        public event Action<float, float> OnChanged;
        public event Action<GameObject> OnDeath;   // passes the killer if known
        public event Action<float> OnDamaged;       // amount

        public bool IsPlayer;

        public void Configure(float max, bool isPlayer = false)
        {
            maxHealth = max;
            IsPlayer = isPlayer;
            Current = maxHealth;
            IsDead = false;
            OnChanged?.Invoke(Current, maxHealth);
        }

        void Awake()
        {
            if (Current <= 0 && !IsDead) Current = maxHealth;
        }

        public void TakeDamage(float amount, GameObject source = null)
        {
            if (IsDead || amount <= 0) return;
            Current = Mathf.Max(0f, Current - amount);
            OnDamaged?.Invoke(amount);
            OnChanged?.Invoke(Current, maxHealth);
            if (Current <= 0f)
            {
                IsDead = true;
                OnDeath?.Invoke(source);
            }
        }

        public void Heal(float amount)
        {
            if (IsDead) return;
            Current = Mathf.Min(maxHealth, Current + amount);
            OnChanged?.Invoke(Current, maxHealth);
        }
    }
}
