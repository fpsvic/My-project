package game;

import java.awt.Color;

public enum TileType {
    DEEP_WATER   (new Color(0x1a4a7a), "Deep Ocean",      false),
    SHALLOW_WATER(new Color(0x2a6fba), "Coastal Waters",  false),
    SAND         (new Color(0xd4b483), "Beach",           true),
    GRASS        (new Color(0x4a8f3f), "Grassland",       true),
    DARK_GRASS   (new Color(0x2d6b2a), "Plains",          true),
    FOREST       (new Color(0x1a4d1a), "Forest",          true),
    MOUNTAIN     (new Color(0x7a6a5a), "Mountains",       false),
    SNOW         (new Color(0xe8e8f0), "Snowy Peaks",     false),
    PATH         (new Color(0xb8a878), "Road",            true),
    WALL         (new Color(0x8a7060), "Building",        false),
    FLOOR        (new Color(0xc8b090), "Inside",          true),
    DOOR         (new Color(0x7a5020), "Doorway",         true);

    public final Color color;
    public final String zoneName;
    public final boolean walkable;

    TileType(Color color, String zoneName, boolean walkable) {
        this.color    = color;
        this.zoneName = zoneName;
        this.walkable = walkable;
    }
}
