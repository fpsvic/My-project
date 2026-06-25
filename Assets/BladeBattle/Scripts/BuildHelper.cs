using UnityEngine;

namespace BladeBattle
{
    /// <summary>
    /// Static utilities for building the game world out of primitives at runtime,
    /// so the whole game works on Play with no manual scene wiring or imported art.
    /// </summary>
    public static class BuildHelper
    {
        static Shader _litShader;

        /// <summary>Pick the URP Lit shader if available, otherwise fall back to the built-in default.</summary>
        public static Shader LitShader
        {
            get
            {
                if (_litShader == null)
                {
                    _litShader = Shader.Find("Universal Render Pipeline/Lit");
                    if (_litShader == null) _litShader = Shader.Find("Standard");
                    if (_litShader == null) _litShader = Shader.Find("Sprites/Default");
                }
                return _litShader;
            }
        }

        public static Material MakeMaterial(Color color, float smoothness = 0.2f, float metallic = 0f)
        {
            var m = new Material(LitShader);
            // URP Lit uses _BaseColor; built-in uses _Color. Set both to be safe.
            if (m.HasProperty("_BaseColor")) m.SetColor("_BaseColor", color);
            if (m.HasProperty("_Color")) m.SetColor("_Color", color);
            if (m.HasProperty("_Smoothness")) m.SetFloat("_Smoothness", smoothness);
            if (m.HasProperty("_Glossiness")) m.SetFloat("_Glossiness", smoothness);
            if (m.HasProperty("_Metallic")) m.SetFloat("_Metallic", metallic);
            return m;
        }

        public static Material MakeEmissive(Color color, float intensity = 2f)
        {
            var m = MakeMaterial(color);
            if (m.HasProperty("_EmissionColor"))
            {
                m.EnableKeyword("_EMISSION");
                m.SetColor("_EmissionColor", color * intensity);
            }
            return m;
        }

        /// <summary>Create a primitive with no default collider noise, parented and positioned.</summary>
        public static GameObject Block(string name, PrimitiveType type, Transform parent,
                                       Vector3 localPos, Vector3 scale, Material mat, bool collider = true)
        {
            var go = GameObject.CreatePrimitive(type);
            go.name = name;
            if (!collider)
            {
                var col = go.GetComponent<Collider>();
                if (col != null) Object.Destroy(col);
            }
            if (parent != null) go.transform.SetParent(parent, false);
            go.transform.localPosition = localPos;
            go.transform.localScale = scale;
            var r = go.GetComponent<Renderer>();
            if (r != null && mat != null) r.sharedMaterial = mat;
            return go;
        }

        public static Color HSV(float h, float s, float v) => Color.HSVToRGB(h, s, v);
    }
}
