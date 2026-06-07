#if UNITY_EDITOR
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

[InitializeOnLoad]
public static class PlayerGameplaySetup
{
    const string SetupDoneKey = "PlayerGameplaySetup.done";
    const string PlayerName = "Human Figure";
    const string GroundName = "Ground";

    static PlayerGameplaySetup()
    {
        EditorApplication.delayCall += EnsureGameplaySetup;
    }

    static void EnsureGameplaySetup()
    {
        if (EditorPrefs.GetBool(SetupDoneKey, false))
            return;

        var scene = SceneManager.GetActiveScene();
        if (!scene.IsValid() || scene.path != "Assets/Scenes/SampleScene.unity")
            return;

        var player = GameObject.Find(PlayerName);
        if (player == null)
            return;

        EnsureGround();
        EnsurePlayerComponents(player);
        EnsureCameraFollow(player.transform);

        EditorSceneManager.MarkSceneDirty(scene);
        EditorSceneManager.SaveScene(scene);
        EditorPrefs.SetBool(SetupDoneKey, true);
    }

    static void EnsureGround()
    {
        if (GameObject.Find(GroundName) != null)
            return;

        var ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
        ground.name = GroundName;
        ground.transform.position = Vector3.zero;
        ground.transform.localScale = new Vector3(3f, 1f, 3f);
    }

    static void EnsurePlayerComponents(GameObject player)
    {
        if (player.GetComponent<CharacterController>() == null)
        {
            var controller = player.AddComponent<CharacterController>();
            controller.height = 1.8f;
            controller.radius = 0.3f;
            controller.center = new Vector3(0f, 0.9f, 0f);
        }

        if (player.GetComponent<PlayerMovement>() == null)
            player.AddComponent<PlayerMovement>();

        player.tag = "Player";
    }

    static void EnsureCameraFollow(Transform target)
    {
        var camera = Camera.main;
        if (camera == null)
            return;

        var follow = camera.GetComponent<CameraFollow>();
        if (follow == null)
            follow = camera.gameObject.AddComponent<CameraFollow>();

        var serialized = new SerializedObject(follow);
        serialized.FindProperty("target").objectReferenceValue = target;
        serialized.ApplyModifiedPropertiesWithoutUndo();
    }
}
#endif
