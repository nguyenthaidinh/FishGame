# src/world/spawner.py
import os
import json
import random

from src.entities.prey import PreyFish
from src.entities.shy_prey_fish import ShyPreyFish
from src.entities.ai_fish import PredatorFish


# =========================
# Helpers
# =========================
def _project_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _load_fish_enemies():
    path = os.path.join(_project_root(), "data", "fish_enemies.json")
    if not os.path.exists(path):
        print("⚠ fish_enemies.json not found:", path)
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f) or {}


def _weighted_choice(items):
    total = sum(max(0, int(it.get("weight", 1))) for it in items)
    r = random.uniform(0, total)
    s = 0
    for it in items:
        s += max(0, int(it.get("weight", 1)))
        if r <= s:
            return it
    return items[-1]


# =========================
# Spawner (MATCH PREY.PY)
# =========================
class Spawner:
    def __init__(self, world_w, world_h):
        self.world_w = world_w
        self.world_h = world_h

        self.timer = 0.0
        self.base_interval = 0.75

        self.enemies_cfg = _load_fish_enemies()

    def _spawn_pos_near_camera(self, camera):
        margin = 220
        x = random.randint(
            max(80, int(camera.offset.x) - margin),
            min(self.world_w - 80, int(camera.offset.x + camera.sw) + margin),
        )
        y = random.randint(
            max(80, int(camera.offset.y) - margin),
            min(self.world_h - 80, int(camera.offset.y + camera.sh) + margin),
        )
        return x, y

    def update(self, dt, player_points, preys, predators, camera, map_id=1):
        self.timer += dt

        interval = max(0.55, self.base_interval - min(0.25, player_points / 1800.0))
        if self.timer < interval:
            return
        self.timer = 0.0  # ⭐ mỗi lần spawn 1 con

        enemies = self.enemies_cfg.get(f"map{int(map_id)}", [])
        if not enemies:
            return

        pp = int(player_points)
        small_count = sum(1 for p in preys if p.points <= 5)

        # ===== build pool theo điểm =====
        pool = []
        for e in enemies:
            pts = int(e.get("points", 5))

            # chặn spam cá 5
            if pts <= 5 and small_count >= 8:
                continue

            if pp < 50 and pts <= 8:
                pool.append(e)
            elif pp < 120 and pts <= 30:
                pool.append(e)
            elif pp < 220 and pts <= 80:
                pool.append(e)
            elif pp >= 220:
                pool.append(e)

        if not pool:
            return

        enemy = _weighted_choice(pool)

        x, y = self._spawn_pos_near_camera(camera)

        fish_folder = enemy["path"]
        points = int(enemy.get("points", 10))
        speed = float(enemy.get("speed", 120))
        ai = enemy.get("ai", "wander")
        role = enemy.get("role", "prey")

        # ===== predator =====
        if role == "predator" or ai == "predator":
            if len(predators) >= 6 + pp // 120:
                return

            predators.append(
                PredatorFish(
                    pos=(x, y),
                    fish_folder=fish_folder,
                    points=points,
                )
            )
            return

        # ===== prey =====
        if ai == "shy":
            preys.append(
                ShyPreyFish(
                    pos=(x, y),
                    fish_folder=fish_folder,
                    points=points,
                    speed=speed,
                )
            )
        else:
            preys.append(
                PreyFish(
                    pos=(x, y),
                    fish_folder=fish_folder,
                    points=points,
                    speed=speed,
                    ai=ai,
                )
            )
