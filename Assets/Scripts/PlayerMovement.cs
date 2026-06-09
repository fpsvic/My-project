using UnityEngine;
using UnityEngine.InputSystem;

[RequireComponent(typeof(CharacterController))]
public class PlayerMovement : MonoBehaviour
{
    [SerializeField] float moveSpeed = 5f;
    [SerializeField] float jumpForce = 6f;
    [SerializeField] float gravity = -20f;
    [SerializeField] float stopDistance = 0.2f;
    [SerializeField] LayerMask groundMask = ~0;

    CharacterController controller;
    Camera mainCamera;
    Vector3 destination;
    bool hasDestination;
    float verticalVelocity;
    bool jumpRequested;

    void Awake()
    {
        controller = GetComponent<CharacterController>();
        mainCamera = Camera.main;
        destination = transform.position;
    }

    void Update()
    {
        HandleClickMove();
        HandleJumpInput();
        MoveCharacter();
    }

    void HandleClickMove()
    {
        if (Mouse.current == null || mainCamera == null)
            return;

        if (!Mouse.current.rightButton.wasPressedThisFrame)
            return;

        Ray ray = mainCamera.ScreenPointToRay(Mouse.current.position.ReadValue());
        if (!Physics.Raycast(ray, out RaycastHit hit, 200f, groundMask, QueryTriggerInteraction.Ignore))
            return;

        destination = hit.point;
        hasDestination = true;
    }

    void HandleJumpInput()
    {
        if (Keyboard.current != null && Keyboard.current.spaceKey.wasPressedThisFrame)
            jumpRequested = true;
    }

    void MoveCharacter()
    {
        bool grounded = controller.isGrounded;
        if (grounded && verticalVelocity < 0f)
            verticalVelocity = -2f;

        if (jumpRequested && grounded)
            verticalVelocity = jumpForce;

        jumpRequested = false;
        verticalVelocity += gravity * Time.deltaTime;

        Vector3 horizontal = Vector3.zero;

        if (Keyboard.current != null)
        {
            float mx = 0f;
            float mz = 0f;
            if (Keyboard.current.wKey.isPressed) mz += 1f;
            if (Keyboard.current.sKey.isPressed) mz -= 1f;
            if (Keyboard.current.aKey.isPressed) mx -= 1f;
            if (Keyboard.current.dKey.isPressed) mx += 1f;
            if (Mathf.Abs(mx) > 0.01f || Mathf.Abs(mz) > 0.01f)
            {
                hasDestination = false;
                Vector3 forward = mainCamera.transform.forward;
                forward.y = 0f;
                forward.Normalize();
                Vector3 right = mainCamera.transform.right;
                right.y = 0f;
                right.Normalize();
                horizontal = (forward * mz + right * mx).normalized * moveSpeed;
            }
        }

        if (hasDestination)
        {
            Vector3 toDestination = destination - transform.position;
            toDestination.y = 0f;

            if (toDestination.magnitude <= stopDistance)
            {
                hasDestination = false;
            }
            else
            {
                horizontal = toDestination.normalized * moveSpeed;
            }
        }

        Vector3 motion = horizontal;
        motion.y = verticalVelocity;
        controller.Move(motion * Time.deltaTime);
    }
}
