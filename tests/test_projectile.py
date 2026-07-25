import pytest
from pygame.math import Vector2

from gameplay.combat.enemy import Enemy
from gameplay.combat.projectile import Bomb, Explosion
from towers import TowerFactory

PLANE_TYPE = 4
MAP_WIDTH = 3008
WAYPOINTS = [Vector2(0, 0), Vector2(500, 0)]


def make_plane(tower_config, assets):
    return TowerFactory.create(PLANE_TYPE, 0, 0, tower_config, assets, audio=None, map_width=MAP_WIDTH)


def test_bomb_inherits_damage_and_radius_from_the_dropping_tower(tower_config, assets):
    plane = make_plane(tower_config, assets)
    bomb = Bomb(plane, Vector2(5, 0))

    assert bomb.damage == plane.damage
    assert bomb.radius == plane.range


def test_bomb_moves_by_velocity_and_decelerates_via_drag(tower_config, assets, ctx, fake_ticks):
    plane = make_plane(tower_config, assets)
    start_pos = Vector2(plane.position)
    velocity = Vector2(10, 0)
    bomb = Bomb(plane, velocity)

    fake_ticks["t"] = 1
    bomb.update(ctx)

    assert bomb.position == start_pos + velocity
    assert bomb._velocity == velocity * Bomb.DRAG


def test_bomb_detonates_into_an_explosion_after_fall_duration(tower_config, assets, ctx, fake_ticks):
    plane = make_plane(tower_config, assets)
    plane.bullets = []
    bomb = Bomb(plane, Vector2(5, 0))
    plane.bullets.append(bomb)

    fake_ticks["t"] = Bomb.FALL_DURATION_MS - 1
    bomb.update(ctx)
    assert bomb in plane.bullets  # not yet

    fake_ticks["t"] = Bomb.FALL_DURATION_MS
    bomb.update(ctx)

    assert bomb not in plane.bullets
    assert len(plane.bullets) == 1
    assert isinstance(plane.bullets[0], Explosion)


def test_bomb_fall_duration_scales_with_game_speed(tower_config, assets, ctx, fake_ticks):
    plane = make_plane(tower_config, assets)
    plane.bullets = []
    bomb = Bomb(plane, Vector2(5, 0))
    plane.bullets.append(bomb)
    ctx.speed = 2

    # Real elapsed time is half FALL_DURATION_MS, but update() multiplies by
    # ctx.speed -- at 2x game speed that's already enough to detonate.
    fake_ticks["t"] = Bomb.FALL_DURATION_MS // 2
    bomb.update(ctx)

    assert bomb not in plane.bullets


def test_explosion_damages_enemies_inside_radius_but_not_outside(tower_config, assets, ctx):
    plane = make_plane(tower_config, assets)
    plane.bullets = []
    center = Vector2(1000, 1000)

    inside  = Enemy(1, 1, level=1, waypoints=WAYPOINTS, assets=assets)
    outside = Enemy(2, 1, level=1, waypoints=WAYPOINTS, assets=assets)
    inside.position  = center + Vector2(plane.range - 1, 0)
    outside.position = center + Vector2(plane.range + 50, 0)
    ctx.enemies.extend([inside, outside])

    explosion = Explosion(center, plane, damage=plane.damage, radius=plane.range)
    plane.bullets.append(explosion)

    explosion.update(ctx)

    assert inside.hp == inside.maxHP - plane.damage
    assert outside.hp == outside.maxHP


def test_explosion_only_deals_damage_once_across_multiple_updates(tower_config, assets, ctx, fake_ticks):
    plane = make_plane(tower_config, assets)
    plane.bullets = []
    center = Vector2(1000, 1000)

    victim = Enemy(1, 1, level=1, waypoints=WAYPOINTS, assets=assets)
    victim.position = Vector2(center)
    ctx.enemies.append(victim)

    explosion = Explosion(center, plane, damage=plane.damage, radius=plane.range)
    plane.bullets.append(explosion)

    fake_ticks["t"] = 0
    explosion.update(ctx)
    fake_ticks["t"] = Explosion.FRAME_DURATION_MS
    explosion.update(ctx)

    assert victim.hp == victim.maxHP - plane.damage  # not hit twice


def test_explosion_removes_itself_once_all_frames_have_played(tower_config, assets, ctx, fake_ticks):
    plane = make_plane(tower_config, assets)
    plane.bullets = []
    explosion = Explosion(Vector2(0, 0), plane, damage=plane.damage, radius=plane.range)
    plane.bullets.append(explosion)

    fake_ticks["t"] = Explosion.FRAME_DURATION_MS * (Explosion.TOTAL_FRAMES - 1)
    explosion.update(ctx)
    assert explosion in plane.bullets  # last frame still playing

    fake_ticks["t"] = Explosion.FRAME_DURATION_MS * Explosion.TOTAL_FRAMES
    explosion.update(ctx)
    assert explosion not in plane.bullets
