using UnityEngine;
using UnityEngine.InputSystem;

[RequireComponent(typeof(CharacterController))]
public class PlayerMovement : MonoBehaviour
{
    [SerializeField] float moveSpeed = 5f;
    [SerializeField] float rotationSpeed = 14f;
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
                Quaternion targetRotation = Quaternion.LookRotation(toDestination);
                transform.rotation = Quaternion.Slerp(
                    transform.rotation,
                    targetRotation,
                    rotationSpeed * Time.deltaTime);
            }
        }

        Vector3 motion = horizontal;
        motion.y = verticalVelocity;
        controller.Move(motion * Time.deltaTime);
    }
}
