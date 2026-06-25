using UnityEngine;
using UnityEngine.InputSystem;

namespace BladeBattle
{
    /// <summary>
    /// Orbiting third-person follow camera driven by mouse look, with a spring-arm
    /// that pulls in when an obstacle is between the camera and the player.
    /// </summary>
    public class ThirdPersonCamera : MonoBehaviour
    {
        public Transform target;
        public float distance = 6.5f;
        public float height = 1.6f;
        public float sensitivity = 0.12f;
        public float minPitch = -25f;
        public float maxPitch = 70f;

        float _yaw;
        float _pitch = 15f;
        Camera _cam;

        public Vector3 PlanarForward
        {
            get { Vector3 f = transform.forward; f.y = 0; return f.normalized; }
        }
        public Vector3 PlanarRight
        {
            get { Vector3 r = transform.right; r.y = 0; return r.normalized; }
        }

        public void Init(Transform t)
        {
            target = t;
            _cam = GetComponent<Camera>();
            Vector3 e = transform.eulerAngles;
            _yaw = e.y;
        }

        void LateUpdate()
        {
            if (target == null) return;

            var mouse = Mouse.current;
            if (mouse != null && Cursor.lockState == CursorLockMode.Locked)
            {
                Vector2 delta = mouse.delta.ReadValue();
                _yaw += delta.x * sensitivity;
                _pitch -= delta.y * sensitivity;
                _pitch = Mathf.Clamp(_pitch, minPitch, maxPitch);
            }

            Quaternion rot = Quaternion.Euler(_pitch, _yaw, 0f);
            Vector3 focus = target.position + Vector3.up * height;
            Vector3 desired = focus - rot * Vector3.forward * distance;

            // Spring-arm: don't clip through walls/ground.
            float dist = distance;
            if (Physics.SphereCast(focus, 0.3f, (desired - focus).normalized,
                                   out RaycastHit hit, distance, ~0, QueryTriggerInteraction.Ignore))
            {
                if (!hit.collider.CompareTag("Player"))
                    dist = Mathf.Clamp(hit.distance - 0.2f, 1.2f, distance);
            }
            desired = focus - rot * Vector3.forward * dist;

            transform.position = Vector3.Lerp(transform.position, desired, 1f - Mathf.Exp(-18f * Time.deltaTime));
            transform.rotation = rot;
        }
    }
}
