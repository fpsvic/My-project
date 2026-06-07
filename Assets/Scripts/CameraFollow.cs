using UnityEngine;

public class CameraFollow : MonoBehaviour
{
    [SerializeField] Transform target;
    [SerializeField] Vector3 offset = new Vector3(0f, 2.5f, -5f);
    [SerializeField] float smoothSpeed = 8f;
    [SerializeField] Vector3 lookAtOffset = new Vector3(0f, 1.2f, 0f);

    void Start()
    {
        if (target == null)
        {
            var player = GameObject.Find("Human Figure");
            if (player != null)
                target = player.transform;
        }
    }

    void LateUpdate()
    {
        if (target == null)
            return;

        Vector3 desiredPosition = target.position + offset;
        transform.position = Vector3.Lerp(
            transform.position,
            desiredPosition,
            smoothSpeed * Time.deltaTime);

        transform.LookAt(target.position + lookAtOffset);
    }
}
