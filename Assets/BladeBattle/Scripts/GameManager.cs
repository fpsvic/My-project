using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.SceneManagement;

namespace BladeBattle
{
    /// <summary>
    /// Drives the match: spawns escalating waves of enemies, tracks score, handles
    /// player death / restart, and keeps the HUD in sync.
    /// </summary>
    public class GameManager : MonoBehaviour
    {
        public static GameManager Instance { get; private set; }

        public HUD hud;
        public EnemySpawner spawner;
        public Health playerHealth;
        public Transform player;

        int _wave;
        int _score;
        int _aliveEnemies;
        bool _spawning;
        bool _gameOver;
        readonly List<float> _waveQueue = new List<float>();

        public void Configure(HUD hud, EnemySpawner spawner, Health playerHealth, Transform player)
        {
            Instance = this;
            this.hud = hud;
            this.spawner = spawner;
            this.playerHealth = playerHealth;
            this.player = player;

            playerHealth.OnChanged += (c, m) => hud.SetHealth(c, m);
            playerHealth.OnDeath += _ => GameOver();
            hud.SetHealth(playerHealth.Current, playerHealth.Max);
            hud.SetScore(0);

            StartCoroutine(IntroThenStart());
        }

        IEnumerator IntroThenStart()
        {
            hud.ShowBanner("BLADE BATTLE", 2.5f);
            yield return new WaitForSeconds(2.6f);
            StartNextWave();
        }

        void StartNextWave()
        {
            _wave++;
            hud.SetWave(_wave);
            hud.ShowBanner($"WAVE {_wave}", 1.6f);
            StartCoroutine(SpawnWave(_wave));
        }

        IEnumerator SpawnWave(int wave)
        {
            _spawning = true;
            int count = 3 + wave * 2;                       // grows each wave
            float hp = 50f + wave * 12f;
            float speed = Mathf.Min(3.2f + wave * 0.18f, 7f);
            float damage = 8f + wave * 1.5f;

            for (int i = 0; i < count; i++)
            {
                if (_gameOver) yield break;
                float scale = Random.Range(0.9f, 1.25f);
                // Occasional bigger "brute".
                if (wave >= 3 && Random.value < 0.18f) { scale = 1.7f; }
                var e = spawner.SpawnOne(hp * (scale > 1.4f ? 2.2f : 1f), speed, damage, scale);
                _aliveEnemies++;
                yield return new WaitForSeconds(Mathf.Max(0.35f, 0.9f - wave * 0.04f));
            }
            _spawning = false;
        }

        public void OnEnemyKilled(Vector3 position)
        {
            _aliveEnemies = Mathf.Max(0, _aliveEnemies - 1);
            _score += 100 + _wave * 10;
            hud.SetScore(_score);
            DamagePopup.SpawnAt(position + Vector3.up * 2.5f, "+", new Color(0.4f, 1f, 0.5f));

            // Small heal reward.
            if (playerHealth != null) playerHealth.Heal(4f);

            if (!_spawning && _aliveEnemies <= 0 && !_gameOver)
                StartCoroutine(NextWaveDelay());
        }

        IEnumerator NextWaveDelay()
        {
            hud.ShowBanner("WAVE CLEARED!", 1.8f);
            yield return new WaitForSeconds(2.4f);
            if (!_gameOver) StartNextWave();
        }

        void GameOver()
        {
            if (_gameOver) return;
            _gameOver = true;
            hud.ShowGameOver(_wave, _score);
            Cursor.lockState = CursorLockMode.None;
            Cursor.visible = true;
        }

        void Update()
        {
            var kb = Keyboard.current;
            if (kb == null) return;

            // Toggle cursor lock (so you can click out / back in).
            if (kb.escapeKey.wasPressedThisFrame && !_gameOver)
            {
                Cursor.lockState = Cursor.lockState == CursorLockMode.Locked
                    ? CursorLockMode.None : CursorLockMode.Locked;
                Cursor.visible = Cursor.lockState != CursorLockMode.Locked;
            }

            if (_gameOver && kb.rKey.wasPressedThisFrame)
                SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex);
        }
    }
}
