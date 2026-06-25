using System.Collections.Generic;
using UnityEngine;

namespace BladeBattle
{
    /// <summary>Briefly tints all renderers white when the object is hit, then restores them.</summary>
    public class HitFlash : MonoBehaviour
    {
        readonly List<Renderer> _renderers = new List<Renderer>();
        readonly List<Color> _baseColors = new List<Color>();
        float _timer;
        const float Duration = 0.12f;
        static readonly int BaseColorId = Shader.PropertyToID("_BaseColor");
        static readonly int ColorId = Shader.PropertyToID("_Color");

        public void Init()
        {
            foreach (var r in GetComponentsInChildren<Renderer>())
            {
                if (r.material == null) continue;
                _renderers.Add(r);
                _baseColors.Add(GetColor(r.material));
            }
        }

        Color GetColor(Material m)
        {
            if (m.HasProperty(BaseColorId)) return m.GetColor(BaseColorId);
            if (m.HasProperty(ColorId)) return m.GetColor(ColorId);
            return Color.white;
        }

        void SetColor(Material m, Color c)
        {
            if (m.HasProperty(BaseColorId)) m.SetColor(BaseColorId, c);
            if (m.HasProperty(ColorId)) m.SetColor(ColorId, c);
        }

        public void Flash()
        {
            if (_renderers.Count == 0) Init();
            _timer = Duration;
            for (int i = 0; i < _renderers.Count; i++)
                if (_renderers[i] != null) SetColor(_renderers[i].material, Color.white);
        }

        void Update()
        {
            if (_timer <= 0f) return;
            _timer -= Time.deltaTime;
            float t = Mathf.Clamp01(_timer / Duration);
            for (int i = 0; i < _renderers.Count; i++)
            {
                if (_renderers[i] == null) continue;
                SetColor(_renderers[i].material, Color.Lerp(_baseColors[i], Color.white, t));
            }
        }
    }
}
