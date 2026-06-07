#if UNITY_EDITOR
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

[InitializeOnLoad]
public static class HumanFigureSceneSetup
{
    const string ModelPath = "Assets/Models/HumanFigure.glb";
    const string ScenePath = "Assets/Scenes/SampleScene.unity";
    const string InstanceName = "Player";
    const string ModelPathName = "Human Figure";
    const string SetupDoneKey = "HumanFigureSceneSetup.done";

    static HumanFigureSceneSetup()
    {
        EditorApplication.delayCall += TryPlaceModel;
    }

    static void TryPlaceModel()
    {
        if (EditorPrefs.GetBool(SetupDoneKey, false))
            return;

        var model = AssetDatabase.LoadAssetAtPath<GameObject>(ModelPath);
        if (model == null)
            return;

        var scene = EditorSceneManager.OpenScene(ScenePath);
        foreach (var root in scene.GetRootGameObjects())
        {
            if (root.name == InstanceName || root.name == ModelPathName)
            {
                if (root.name != InstanceName)
                    root.name = InstanceName;
                EditorPrefs.SetBool(SetupDoneKey, true);
                return;
            }
        }

        var instance = (GameObject)PrefabUtility.InstantiatePrefab(model);
        instance.name = InstanceName;
        instance.tag = "Player";
        instance.transform.SetPositionAndRotation(Vector3.zero, Quaternion.identity);

        EditorSceneManager.MarkSceneDirty(scene);
        EditorSceneManager.SaveScene(scene);
        EditorPrefs.SetBool(SetupDoneKey, true);
    }
}
#endif
