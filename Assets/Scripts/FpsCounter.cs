using UnityEngine;

public class FpsCounter : MonoBehaviour
{
    float smoothedDeltaTime;

    void Update()
    {
        smoothedDeltaTime += (Time.unscaledDeltaTime - smoothedDeltaTime) * 0.1f;
    }

    void OnGUI()
    {
        float fps = 1f / Mathf.Max(smoothedDeltaTime, 0.0001f);
        var style = new GUIStyle(GUI.skin.label)
        {
            alignment = TextAnchor.UpperRight,
            fontSize = 14,
            fontStyle = FontStyle.Bold
        };
        style.normal.textColor = Color.white;

        const float width = 120f;
        const float height = 24f;
        float x = Screen.width - width - 12f;
        GUI.Label(new Rect(x, 10f, width, height), Mathf.RoundToInt(fps) + " FPS", style);
    }
}
