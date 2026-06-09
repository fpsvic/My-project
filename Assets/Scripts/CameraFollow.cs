using UnityEngine;
using UnityEngine.InputSystem;

/// <summary>First-person camera: sits at the character's eyes, mouse controls look.</summary>
public class CameraFollow : MonoBehaviour
{
    [SerializeField] Transform target;
    [SerializeField] float eyeHeight = 1.65f;
    [SerializeField] float mouseSensitivity = 0.12f;

    float pitch;

    void Start()
    {
        if (target == null)
        {
            var player = GameObject.FindWithTag("Player");
            if (player == null)
                player = GameObject.Find("Player");
            if (player != null)
                target = player.transform;
        }

        Cursor.lockState = CursorLockMode.Locked;
        Cursor.visible = false;

        if (target != null)
        {
            foreach (var renderer in target.GetComponentsInChildren<Renderer>())
                renderer.enabled = false;
        }
    }

    void LateUpdate()
    {
        if (target == null)
            return;

        if (Mouse.current != null)
        {
            Vector2 delta = Mouse.current.delta.ReadValue();
            target.Rotate(0f, delta.x * mouseSensitivity, 0f, Space.World);
            pitch = Mathf.Clamp(pitch - delta.y * mouseSensitivity, -85f, 85f);
        }

        transform.position = target.position + Vector3.up * eyeHeight;
        transform.rotation = Quaternion.Euler(pitch, target.eulerAngles.y, 0f);
    }
}
