using UnityEngine;

public class PlayerWeapon : MonoBehaviour
{
    [SerializeField] string currentWeaponName = "Rusty Blade";
    [SerializeField] float currentDamage = 1f;

    Transform swordVisual;
    MeleeAttack meleeAttack;

    public string CurrentWeaponName => currentWeaponName;
    public float CurrentDamage => currentDamage;

    void Awake()
    {
        meleeAttack = GetComponent<MeleeAttack>();
        CreateDefaultVisual();
    }

    public bool TryEquip(SwordLoot loot)
    {
        if (loot == null || !loot.IsBetterThan(currentDamage))
            return false;

        currentWeaponName = loot.SwordName;
        currentDamage = loot.Damage;

        if (meleeAttack != null)
            meleeAttack.ApplyWeaponStats(loot.Damage, loot.Range, loot.AttackCooldown, loot.SwordName);

        UpdateVisual(loot.SwordName, GetColorForLoot(loot));
        BladeArenaGame.Instance?.OnWeaponEquipped(currentWeaponName);
        return true;
    }

    void CreateDefaultVisual()
    {
        if (swordVisual != null)
            return;

        swordVisual = CreateSwordMesh("Equipped Sword", new Color(0.55f, 0.55f, 0.6f), 0.85f);
        swordVisual.SetParent(transform, false);
        swordVisual.localPosition = new Vector3(0.35f, 1.1f, 0.25f);
        swordVisual.localRotation = Quaternion.Euler(10f, -20f, 90f);
    }

    void UpdateVisual(string weaponName, Color color)
    {
        if (swordVisual != null)
            Destroy(swordVisual.gameObject);

        float length = weaponName.Contains("Storm") ? 1.2f : weaponName.Contains("Steel") ? 1.05f : 0.95f;
        swordVisual = CreateSwordMesh("Equipped Sword", color, length);
        swordVisual.SetParent(transform, false);
        swordVisual.localPosition = new Vector3(0.35f, 1.1f, 0.25f);
        swordVisual.localRotation = Quaternion.Euler(10f, -20f, 90f);
    }

    static Transform CreateSwordMesh(string name, Color color, float length)
    {
        var blade = GameObject.CreatePrimitive(PrimitiveType.Cube);
        blade.name = name;
        blade.transform.localScale = new Vector3(0.08f, length, 0.18f);

        var collider = blade.GetComponent<Collider>();
        if (collider != null)
            Destroy(collider);

        var renderer = blade.GetComponent<Renderer>();
        if (renderer != null)
            renderer.material.color = color;

        return blade.transform;
    }

    static Color GetColorForLoot(SwordLoot loot)
    {
        if (loot.SwordName.Contains("Storm"))
            return new Color(0.45f, 0.75f, 1f);
        if (loot.SwordName.Contains("Steel"))
            return new Color(0.78f, 0.82f, 0.9f);
        return new Color(0.72f, 0.45f, 0.2f);
    }
}
