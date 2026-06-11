-- Blade Arena live-tunable game data.
-- Edit values, save, and changes apply instantly while the game runs (auto-reload ~0.35s).
-- Manual reload: F5

return {
  player = {
    max_health = 5,
    move_speed = 5.5,
    river_move_speed = 3.2,
    jump_velocity = 6.5,
    gravity = 22.0,
    starter_weapon = "rusty_blade",
  },

  enemies = {
    count = 10,
    health = 2.0,
    speed = 2.5,
    attack_damage = 1,
    attack_cooldown = 1.2,
    aggro_range = 45.0,
    attack_range = 1.4,
  },

  storm = {
    check_interval = 60.0,
    start_chance_permille = 100,
    duration = 40.0,
    lightning_interval = 2.5,
    strike_chance_permille = 50,
    strike_damage = 2,
  },

  -- tree_mode: "evergreen" (pine/spruce whorls) or "deciduous" (round crowns)
  world = {
    tree_mode = "evergreen",
  },

  -- Tweak any value below, save the file, and the running game updates in ~0.35s.
  -- Example: change storm_blade damage from 4.5 to 45 — no recompile needed.
  weapons = {
    rusty_blade = {
      name = "Rusty Blade",
      damage = 1.0,
      range = 2.2,
      cooldown = 0.45,
      color = { r = 140, g = 140, b = 153 },
    },
    iron_sword = {
      name = "Iron Sword",
      damage = 2.0,
      range = 2.5,
      cooldown = 0.38,
      color = { r = 184, g = 115, b = 51 },
    },
    steel_sword = {
      name = "Steel Sword",
      damage = 3.0,
      range = 2.8,
      cooldown = 0.32,
      color = { r = 199, g = 209, b = 230 },
    },
    storm_blade = {
      name = "Storm Blade",
      damage = 4.5,
      range = 3.2,
      cooldown = 0.28,
      color = { r = 115, g = 191, b = 255 },
    },
  },

  loot_cabins = {
    { weapon = "iron_sword", x = -70, z = 55, cabin_color = { r = 130, g = 105, b = 85 } },
    { weapon = "steel_sword", x = 85, z = -60, cabin_color = { r = 105, g = 125, b = 100 } },
    { weapon = "storm_blade", x = -45, z = -95, cabin_color = { r = 95, g = 105, b = 135 } },
  },

  combos = {
    stonestep = {
      cooldown = 4.0,
      dash_distance = 2.8,
      dash_speed = 16.0,
      shield_duration = 0.45,
    },
    apex_parry = {
      cooldown = 5.0,
      parry_window = 0.5,
      damage_scale = 2.5,
      aoe_radius = 2.2,
    },
    velocity_strike = {
      cooldown = 3.0,
      dash_distance = 4.5,
      dash_speed = 22.0,
      damage_scale = 2.2,
      range_scale = 1.35,
    },
    shatter_step = {
      cooldown = 5.0,
      dash_distance = 3.2,
      dash_speed = 20.0,
      damage_scale = 1.6,
      aoe_radius = 2.8,
    },
    dash_sever = {
      cooldown = 4.0,
      dash_distance = 5.5,
      dash_speed = 24.0,
      damage_scale = 1.7,
    },
  },
}
