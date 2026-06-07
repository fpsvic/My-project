using System.Collections.Generic;
using UnityEngine;

public class StormSystem : MonoBehaviour
{
    [SerializeField] float stormChance = 0.1f;
    [SerializeField] float stormCheckInterval = 60f;
    [SerializeField] float stormDuration = 40f;
    [SerializeField] float lightningStrikeInterval = 2.5f;
    [SerializeField] float exposedStrikeChance = 0.05f;
    [SerializeField] int lightningDamage = 2;

    Light directionalLight;
    Color normalAmbient;
    Color stormAmbient = new Color(0.08f, 0.1f, 0.16f);
    float normalLightIntensity = 2f;
    float stormLightIntensity = 0.15f;
    Color normalFogColor;
    Color stormFogColor = new Color(0.05f, 0.06f, 0.12f);
    float checkTimer;
    float stormTimer;
    float lightningTimer;
    bool stormActive;

    public bool IsStormActive => stormActive;

    void Start()
    {
        directionalLight = FindDirectionalLight();
        normalAmbient = RenderSettings.ambientLight;
        normalFogColor = RenderSettings.fogColor;

        if (directionalLight != null)
            normalLightIntensity = directionalLight.intensity;

        checkTimer = 5f;
        TryRollStorm();
    }

    void Update()
    {
        if (stormActive)
        {
            stormTimer -= Time.deltaTime;
            lightningTimer -= Time.deltaTime;

            if (lightningTimer <= 0f)
            {
                lightningTimer = lightningStrikeInterval;
                StrikeLightning();
            }

            if (stormTimer <= 0f)
                EndStorm();

            return;
        }

        checkTimer -= Time.deltaTime;
        if (checkTimer <= 0f)
        {
            checkTimer = stormCheckInterval;
            TryRollStorm();
        }
    }

    void TryRollStorm()
    {
        if (stormActive)
            return;

        if (Random.value < stormChance)
            StartStorm();
    }

    void StartStorm()
    {
        stormActive = true;
        stormTimer = stormDuration;
        lightningTimer = 1f;

        RenderSettings.ambientLight = stormAmbient;
        RenderSettings.fog = true;
        RenderSettings.fogColor = stormFogColor;
        RenderSettings.fogDensity = 0.03f;

        if (directionalLight != null)
            directionalLight.intensity = stormLightIntensity;
    }

    void EndStorm()
    {
        stormActive = false;
        checkTimer = stormCheckInterval;

        RenderSettings.ambientLight = normalAmbient;
        RenderSettings.fogColor = normalFogColor;
        RenderSettings.fogDensity = 0f;
        RenderSettings.fog = false;

        if (directionalLight != null)
            directionalLight.intensity = normalLightIntensity;
    }

    void StrikeLightning()
    {
        if (directionalLight != null)
        {
            directionalLight.intensity = 2.8f;
            Invoke(nameof(DimLightAfterFlash), 0.12f);
        }

        foreach (var target in GetExposedTargets())
        {
            if (Random.value > exposedStrikeChance)
                continue;

            ApplyLightningDamage(target);
        }
    }

    void DimLightAfterFlash()
    {
        if (directionalLight != null && stormActive)
            directionalLight.intensity = stormLightIntensity;
    }

    static IEnumerable<GameObject> GetExposedTargets()
    {
        var player = GameObject.FindGameObjectWithTag("Player");
        if (player != null && !BuildingShelter.IsSheltered(player.transform.position))
            yield return player;

        var enemies = FindObjectsByType<ArenaEnemy>(FindObjectsSortMode.None);
        foreach (var enemy in enemies)
        {
            if (!BuildingShelter.IsSheltered(enemy.transform.position))
                yield return enemy.gameObject;
        }
    }

    void ApplyLightningDamage(GameObject target)
    {
        var playerHealth = target.GetComponent<PlayerHealth>();
        if (playerHealth != null)
        {
            playerHealth.TakeDamage(lightningDamage);
            return;
        }

        var enemy = target.GetComponent<ArenaEnemy>();
        enemy?.TakeDamage(lightningDamage, false);
    }

    static Light FindDirectionalLight()
    {
        var lights = FindObjectsByType<Light>(FindObjectsSortMode.None);
        foreach (var light in lights)
        {
            if (light.type == LightType.Directional)
                return light;
        }

        return null;
    }
}
