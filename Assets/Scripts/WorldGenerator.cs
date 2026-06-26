using UnityEngine;
using UnityEngine.Tilemaps;

public class WorldGenerator : MonoBehaviour
{
    [Header("Tilemap")]
    [SerializeField] Tilemap groundTilemap;
    [SerializeField] Tilemap collisionTilemap;

    [Header("Tiles")]
    [SerializeField] TileBase waterTile;
    [SerializeField] TileBase sandTile;
    [SerializeField] TileBase grassTile;
    [SerializeField] TileBase forestTile;
    [SerializeField] TileBase mountainTile;

    [Header("World Settings")]
    [SerializeField] int width = 80;
    [SerializeField] int height = 60;
    [SerializeField] float scale = 0.08f;
    [SerializeField] int seed = 42;

    void Start() => GenerateWorld();

    void GenerateWorld()
    {
        Random.InitState(seed);
        float offsetX = Random.Range(0f, 9999f);
        float offsetY = Random.Range(0f, 9999f);

        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                float cx = (x / (float)width  - 0.5f) * 2f;
                float cy = (y / (float)height - 0.5f) * 2f;
                float dist = Mathf.Sqrt(cx * cx + cy * cy);

                float h = Mathf.PerlinNoise((x + offsetX) * scale, (y + offsetY) * scale);
                h -= dist * 0.45f;

                var pos = new Vector3Int(x - width / 2, y - height / 2, 0);
                TileBase tile = SelectTile(h);
                groundTilemap.SetTile(pos, tile);

                if (h < 0.1f || h > 0.72f)
                    collisionTilemap.SetTile(pos, tile);
            }
        }
    }

    TileBase SelectTile(float h)
    {
        if (h < 0.1f)  return waterTile;
        if (h < 0.2f)  return sandTile;
        if (h < 0.6f)  return grassTile;
        if (h < 0.72f) return forestTile;
        return mountainTile;
    }
}
