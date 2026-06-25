using UnityEngine;

namespace BladeBattle
{
    /// <summary>Floating world-space text that rises, faces the camera, and fades out.</summary>
    public class DamagePopup : MonoBehaviour
    {
        TextMesh _text;
        float _life = 0.8f;
        float _age;
        Color _color = Color.white;

        public static void SpawnAt(Vector3 position, string message, Color? color = null)
        {
            var go = new GameObject("DamagePopup");
            go.transform.position = position;
            var p = go.AddComponent<DamagePopup>();
            p._text = go.AddComponent<TextMesh>();
            p._text.text = message;
            p._text.fontSize = 64;
            p._text.characterSize = 0.06f;
            p._text.anchor = TextAnchor.MiddleCenter;
            p._text.alignment = TextAlignment.Center;
            p._color = color ?? new Color(1f, 0.85f, 0.2f);
            p._text.color = p._color;
        }

        void Update()
        {
            _age += Time.deltaTime;
            transform.position += Vector3.up * 1.5f * Time.deltaTime;
            if (Camera.main != null)
                transform.rotation = Camera.main.transform.rotation;

            float t = Mathf.Clamp01(_age / _life);
            Color c = _color;
            c.a = 1f - t;
            if (_text != null) _text.color = c;
            transform.localScale = Vector3.one * (1f + t * 0.5f);

            if (_age >= _life) Destroy(gameObject);
        }
    }
}
