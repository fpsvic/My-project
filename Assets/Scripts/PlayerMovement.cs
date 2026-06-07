using UnityEngine;
using UnityEngine.InputSystem;

[RequireComponent(typeof(CharacterController))]
public class PlayerMovement : MonoBehaviour
{
    [SerializeField] float moveSpeed = 4f;
    [SerializeField] float rotationSpeed = 12f;

    CharacterController controller;
    Camera mainCamera;

    void Awake()
    {
        controller = GetComponent<CharacterController>();
        mainCamera = Camera.main;
    }

    void Update()
    {
        Vector2 input = ReadMoveInput();
        if (input.sqrMagnitude > 1f)
            input.Normalize();

        Vector3 move = new Vector3(input.x, 0f, input.y);
        if (mainCamera != null)
        {
            Vector3 forward = mainCamera.transform.forward;
            forward.y = 0f;
            forward.Normalize();

            Vector3 right = mainCamera.transform.right;
            right.y = 0f;
            right.Normalize();

            move = forward * move.z + right * input.x;
        }

        controller.Move(move * moveSpeed * Time.deltaTime);

        if (move.sqrMagnitude > 0.001f)
        {
            Quaternion targetRotation = Quaternion.LookRotation(move);
            transform.rotation = Quaternion.Slerp(
                transform.rotation,
                targetRotation,
                rotationSpeed * Time.deltaTime);
        }
    }

    static Vector2 ReadMoveInput()
    {
        if (Keyboard.current == null)
            return Vector2.zero;

        float x = 0f;
        float y = 0f;

        if (Keyboard.current.aKey.isPressed || Keyboard.current.leftArrowKey.isPressed)
            x -= 1f;
        if (Keyboard.current.dKey.isPressed || Keyboard.current.rightArrowKey.isPressed)
            x += 1f;
        if (Keyboard.current.sKey.isPressed || Keyboard.current.downArrowKey.isPressed)
            y -= 1f;
        if (Keyboard.current.wKey.isPressed || Keyboard.current.upArrowKey.isPressed)
            y += 1f;

        return new Vector2(x, y);
    }
}
