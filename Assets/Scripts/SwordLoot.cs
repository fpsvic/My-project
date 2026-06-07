using UnityEngine;

public class SwordLoot : MonoBehaviour
{
    [SerializeField] string swordName = "Iron Sword";
    [SerializeField] float damage = 2f;
    [SerializeField] float range = 2.4f;
    [SerializeField] float attackCooldown = 0.4f;

    public string SwordName => swordName;
    public float Damage => damage;
    public float Range => range;
    public float AttackCooldown => attackCooldown;

    public void Configure(string name, float swordDamage, float swordRange, float cooldown, Color color)
    {
        swordName = name;
        damage = swordDamage;
        range = swordRange;
        attackCooldown = cooldown;

        var renderer = GetComponent<Renderer>();
        if (renderer != null)
            renderer.material.color = color;
    }

    public bool IsBetterThan(float currentDamage)
    {
        return damage > currentDamage + 0.01f;
    }

    void OnTriggerEnter(Collider other)
    {
        if (!other.CompareTag("Player"))
            return;

        var weapon = other.GetComponent<PlayerWeapon>();
        if (weapon == null)
            weapon = other.gameObject.AddComponent<PlayerWeapon>();

        if (!weapon.TryEquip(this))
            return;

        Destroy(gameObject);
    }
}
