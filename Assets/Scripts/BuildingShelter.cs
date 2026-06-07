using UnityEngine;

[RequireComponent(typeof(Collider))]
public class BuildingShelter : MonoBehaviour
{
    Collider shelterCollider;

    void Awake()
    {
        shelterCollider = GetComponent<Collider>();
        shelterCollider.isTrigger = true;
    }

    public static bool IsSheltered(Vector3 worldPosition)
    {
        Vector3 samplePoint = worldPosition + Vector3.up * 0.75f;
        var overlaps = Physics.OverlapSphere(samplePoint, 0.8f, ~0, QueryTriggerInteraction.Collide);
        foreach (var overlap in overlaps)
        {
            if (overlap.GetComponent<BuildingShelter>() != null)
                return true;
        }

        return false;
    }
}
