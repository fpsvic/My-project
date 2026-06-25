using UnityEngine;
using UnityEngine.UI;

namespace BladeBattle
{
    /// <summary>
    /// Builds the entire on-screen UI (health bar, wave/score/combo readouts, crosshair,
    /// banners and the game-over panel) from code at runtime — no prefab needed.
    /// </summary>
    public class HUD : MonoBehaviour
    {
        Canvas _canvas;
        Image _healthFill;
        Text _healthText, _waveText, _scoreText, _comboText, _bannerText, _hintText;
        GameObject _gameOverPanel;
        Text _gameOverText;
        float _bannerTimer;

        public void Build()
        {
            var canvasGo = new GameObject("HUDCanvas");
            canvasGo.transform.SetParent(transform, false);
            _canvas = canvasGo.AddComponent<Canvas>();
            _canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            var scaler = canvasGo.AddComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1920, 1080);
            canvasGo.AddComponent<GraphicRaycaster>();

            // --- Health bar (bottom-left) ---
            var barBg = Panel("HealthBarBg", new Vector2(0, 0), new Vector2(0, 0),
                new Vector2(40, 40), new Vector2(440, 78), new Color(0, 0, 0, 0.55f));
            var fillGo = new GameObject("Fill");
            fillGo.transform.SetParent(barBg.transform, false);
            _healthFill = fillGo.AddComponent<Image>();
            _healthFill.color = new Color(0.25f, 0.85f, 0.35f);
            var fr = _healthFill.rectTransform;
            fr.anchorMin = new Vector2(0, 0); fr.anchorMax = new Vector2(1, 1);
            fr.offsetMin = new Vector2(6, 6); fr.offsetMax = new Vector2(-6, -6);
            fr.pivot = new Vector2(0, 0.5f);
            _healthText = Label(barBg.transform, "HealthText", "100 / 100", 30, TextAnchor.MiddleCenter);
            Stretch(_healthText.rectTransform);

            // --- Wave & score (top-left) ---
            _waveText = Label(_canvas.transform, "WaveText", "WAVE 1", 44, TextAnchor.UpperLeft);
            Anchor(_waveText.rectTransform, new Vector2(0, 1), new Vector2(40, -40), new Vector2(600, 60));
            _scoreText = Label(_canvas.transform, "ScoreText", "SCORE 0", 30, TextAnchor.UpperLeft);
            Anchor(_scoreText.rectTransform, new Vector2(0, 1), new Vector2(40, -100), new Vector2(600, 50));

            // --- Combo (right of center) ---
            _comboText = Label(_canvas.transform, "ComboText", "", 60, TextAnchor.MiddleRight);
            _comboText.color = new Color(1f, 0.8f, 0.2f);
            Anchor(_comboText.rectTransform, new Vector2(1, 0.5f), new Vector2(-60, -40), new Vector2(400, 100));

            // --- Crosshair (center) ---
            var cross = Panel("Crosshair", new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f),
                Vector2.zero, new Vector2(8, 8), new Color(1, 1, 1, 0.8f));

            // --- Banner (center, transient) ---
            _bannerText = Label(_canvas.transform, "Banner", "", 90, TextAnchor.MiddleCenter);
            _bannerText.color = new Color(1f, 0.9f, 0.4f);
            Anchor(_bannerText.rectTransform, new Vector2(0.5f, 0.6f), Vector2.zero, new Vector2(1400, 200));

            // --- Controls hint (bottom-right) ---
            _hintText = Label(_canvas.transform, "Hint",
                "WASD move   SHIFT sprint   SPACE jump   LMB / J slash   ESC cursor", 24, TextAnchor.LowerRight);
            _hintText.color = new Color(1, 1, 1, 0.6f);
            Anchor(_hintText.rectTransform, new Vector2(1, 0), new Vector2(-30, 30), new Vector2(1000, 40));

            // --- Game over panel ---
            _gameOverPanel = Panel("GameOver", new Vector2(0, 0), new Vector2(1, 1),
                Vector2.zero, Vector2.zero, new Color(0, 0, 0, 0.78f));
            Stretch(_gameOverPanel.GetComponent<RectTransform>());
            _gameOverText = Label(_gameOverPanel.transform, "GOText", "GAME OVER", 100, TextAnchor.MiddleCenter);
            Anchor(_gameOverText.rectTransform, new Vector2(0.5f, 0.5f), new Vector2(0, 40), new Vector2(1600, 300));
            var restart = Label(_gameOverPanel.transform, "Restart", "Press  R  to fight again", 40, TextAnchor.MiddleCenter);
            Anchor(restart.rectTransform, new Vector2(0.5f, 0.5f), new Vector2(0, -120), new Vector2(1200, 100));
            _gameOverPanel.SetActive(false);
        }

        public void SetHealth(float current, float max)
        {
            if (_healthFill != null)
            {
                float pct = max > 0 ? current / max : 0;
                _healthFill.rectTransform.anchorMax = new Vector2(Mathf.Clamp01(pct), 1);
                _healthFill.color = Color.Lerp(new Color(0.9f, 0.2f, 0.2f), new Color(0.25f, 0.85f, 0.35f), pct);
            }
            if (_healthText != null) _healthText.text = $"{Mathf.CeilToInt(current)} / {Mathf.CeilToInt(max)}";
        }

        public void SetWave(int wave) { if (_waveText != null) _waveText.text = $"WAVE {wave}"; }
        public void SetScore(int score) { if (_scoreText != null) _scoreText.text = $"SCORE {score}"; }

        public void SetCombo(int combo)
        {
            if (_comboText == null) return;
            _comboText.text = combo > 1 ? $"COMBO x{combo}" : "";
        }

        public void ShowBanner(string text, float duration = 2.2f)
        {
            if (_bannerText == null) return;
            _bannerText.text = text;
            _bannerTimer = duration;
        }

        public void ShowGameOver(int wave, int score)
        {
            if (_gameOverPanel == null) return;
            _gameOverPanel.SetActive(true);
            _gameOverText.text = $"GAME OVER\n<size=44>Reached Wave {wave}   •   Score {score}</size>";
        }

        public void HideGameOver() { if (_gameOverPanel != null) _gameOverPanel.SetActive(false); }

        void Update()
        {
            if (_bannerTimer > 0f)
            {
                _bannerTimer -= Time.deltaTime;
                if (_bannerTimer <= 0f && _bannerText != null) _bannerText.text = "";
            }
        }

        // ---------- UI construction helpers ----------
        GameObject Panel(string name, Vector2 aMin, Vector2 aMax, Vector2 anchoredPos, Vector2 size, Color color)
        {
            var go = new GameObject(name);
            go.transform.SetParent(_canvas.transform, false);
            var img = go.AddComponent<Image>();
            img.color = color;
            var rt = img.rectTransform;
            rt.anchorMin = aMin; rt.anchorMax = aMax;
            rt.pivot = new Vector2(aMin.x == aMax.x ? aMin.x : 0.5f, aMin.y == aMax.y ? aMin.y : 0.5f);
            if (size != Vector2.zero) rt.sizeDelta = size;
            rt.anchoredPosition = anchoredPos;
            return go;
        }

        Text Label(Transform parent, string name, string text, int size, TextAnchor anchor)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            var t = go.AddComponent<Text>();
            t.text = text;
            t.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            if (t.font == null) t.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            t.fontSize = size;
            t.alignment = anchor;
            t.color = Color.white;
            t.horizontalOverflow = HorizontalWrapMode.Overflow;
            t.verticalOverflow = VerticalWrapMode.Overflow;
            t.supportRichText = true;
            var outline = go.AddComponent<Outline>();
            outline.effectColor = new Color(0, 0, 0, 0.85f);
            outline.effectDistance = new Vector2(2, -2);
            return t;
        }

        void Anchor(RectTransform rt, Vector2 anchor, Vector2 pos, Vector2 size)
        {
            rt.anchorMin = anchor; rt.anchorMax = anchor; rt.pivot = anchor;
            rt.anchoredPosition = pos; rt.sizeDelta = size;
        }

        void Stretch(RectTransform rt)
        {
            rt.anchorMin = Vector2.zero; rt.anchorMax = Vector2.one;
            rt.offsetMin = Vector2.zero; rt.offsetMax = Vector2.zero;
        }
    }
}
