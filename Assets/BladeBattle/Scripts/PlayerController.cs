using UnityEngine;
using UnityEngine.InputSystem;

namespace BladeBattle
{
    /// <summary>
    /// Third-person character movement: WASD relative to camera, sprint, jump, gravity.
    /// Uses a CharacterController and the new Input System (polled directly so no
    /// .inputactions wiring is required).
    /// </summary>
    [RequireComponent(typeof(CharacterController))]
    public class PlayerController : MonoBehaviour
    {
        public float walkSpeed = 6f;
        public float sprintSpeed = 10f;
        public float rotationSpeed = 14f;
        public float jumpHeight = 2.2f;
        public float gravity = -22f;

        CharacterController _cc;
        ThirdPersonCamera _cam;
        Vector3 _velocity;
        public bool Sprinting { get; private set; }
        public bool Moving { get; private set; }
        public Vector3 PlanarVelocity { get; private set; }

        public void Init(ThirdPersonCamera cam)
        {
            _cam = cam;
        }

        void Awake()
        {
            _cc = GetComponent<CharacterController>();
        }

        void Update()
        {
            var kb = Keyboard.current;
            if (kb == null) return;

            // --- Read movement input ---
            Vector2 input = Vector2.zero;
            if (kb.wKey.isPressed || kb.upArrowKey.isPressed) input.y += 1f;
            if (kb.sKey.isPressed || kb.downArrowKey.isPressed) input.y -= 1f;
            if (kb.dKey.isPressed || kb.rightArrowKey.isPressed) input.x += 1f;
            if (kb.aKey.isPressed || kb.leftArrowKey.isPressed) input.x -= 1f;
            input = Vector2.ClampMagnitude(input, 1f);

            Sprinting = kb.leftShiftKey.isPressed && input.y > 0.1f;
            float speed = Sprinting ? sprintSpeed : walkSpeed;

            // Camera-relative direction
            Vector3 fwd = Vector3.forward, right = Vector3.right;
            if (_cam != null)
            {
                fwd = _cam.PlanarForward;
                right = _cam.PlanarRight;
            }
            Vector3 move = (fwd * input.y + right * input.x);
            Moving = move.sqrMagnitude > 0.001f;

            // Rotate toward movement direction
            if (Moving)
            {
                Quaternion target = Quaternion.LookRotation(move, Vector3.up);
                transform.rotation = Quaternion.Slerp(transform.rotation, target, rotationSpeed * Time.deltaTime);
            }

            // --- Gravity & jump ---
            if (_cc.isGrounded && _velocity.y < 0f)
                _velocity.y = -2f;

            if (_cc.isGrounded && kb.spaceKey.wasPressedThisFrame)
                _velocity.y = Mathf.Sqrt(jumpHeight * -2f * gravity);

            _velocity.y += gravity * Time.deltaTime;

            Vector3 horizontal = move * speed;
            PlanarVelocity = horizontal;
            Vector3 motion = horizontal + Vector3.up * _velocity.y;
            _cc.Move(motion * Time.deltaTime);

            // Safety: respawn if we fall off the world
            if (transform.position.y < -25f)
            {
                _velocity = Vector3.zero;
                _cc.enabled = false;
                transform.position = new Vector3(0f, 2f, 0f);
                _cc.enabled = true;
            }
        }
    }
}
