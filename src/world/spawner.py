# src/world/spawner.py
import os
import json
import random

from src.entities.prey import PreyFish
from src.entities.shy_prey_fish import ShyPreyFish
from src.entities.ai_fish import PredatorFish


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
    if not items:
        return None
    total = 0
    for it in items:
        w = int(it.get("weight", 1))
        if w > 0:
            total += w
    if total <= 0:
        return items[-1]

    r = random.uniform(0, total)
    s = 0
    for it in items:
        w = int(it.get("weight", 1))
        if w <= 0:
            continue
        s += w
        if r <= s:
            return it
    return items[-1]


class Spawner:
    def __init__(self, world_w, world_h):
        self.world_w = world_w
        self.world_h = world_h

        self.prey_timer = 0.0
        self.pred_timer = 0.0

        # PREY: đủ mồi, nhưng hạn chế prey "to"
        self.prey_base_interval = 0.64
        self.prey_min_interval  = 0.48

        # PREDATOR: xuất hiện đều để tạo áp lực
        self.pred_base_interval = 1.10
        self.pred_min_interval  = 0.78

        self.enemies_cfg = _load_fish_enemies()

    def _spawn_pos_outside_view(self, camera):
        margin = 260
        side = random.choice(["left", "right", "top", "bottom"])

        view_l = int(camera.offset.x)
        view_r = int(camera.offset.x + camera.sw)
        view_t = int(camera.offset.y)
        view_b = int(camera.offset.y + camera.sh)

        if side == "left":
            x = max(60, view_l - margin)
            y = random.randint(max(60, view_t - 120), min(self.world_h - 60, view_b + 120))
        elif side == "right":
            x = min(self.world_w - 60, view_r + margin)
            y = random.randint(max(60, view_t - 120), min(self.world_h - 60, view_b + 120))
        elif side == "top":
            x = random.randint(max(60, view_l - 120), min(self.world_w - 60, view_r + 120))
            y = max(60, view_t - margin)
        else:
            x = random.randint(max(60, view_l - 120), min(self.world_w - 60, view_r + 120))
            y = min(self.world_h - 60, view_b + margin)

        return x, y

    def _build_pool(self, enemies, pp, preys, want_predator: bool):
        small_count = sum(1 for p in preys if getattr(p, "points", 0) <= 5)

        pool = []
        for e in enemies:
            pts = int(e.get("points", 5))
            mn = int(e.get("min_pp", 0))
            mx = int(e.get("max_pp", 999999))
            ai = e.get("ai", "wander")
            role = e.get("role", "prey")
            is_pred = (role == "predator" or ai == "predator")

            if want_predator and (not is_pred):
                continue
            if (not want_predator) and is_pred:
                continue

            if not (mn <= pp <= mx):
                continue

            # ===== PREY CONTROL =====
            if (not want_predator):
                # chặn spam cá 5 nhưng vẫn đủ mồi
                if pts <= 5:
                    limit = 10 if pp < 80 else (8 if pp < 160 else 6)
                    if small_count >= limit:
                        continue

            # ===== weight tuning (không sửa JSON) =====
            w = int(e.get("weight", 1))

            if not want_predator:
                # ---- PREY ----
                # giảm cá 5 khi pp tăng
                if pts <= 5 and pp >= 60:
                    w = max(1, int(w * 0.70))

                # cá 8-30: mồi chính (ăn vui nhưng không phình quá nhanh)
                if 8 <= pts <= 30:
                    w = int(w * 1.45)

                # ✅ nerf mạnh prey 40-90 (đây là thứ làm player phình quá nhanh)
                if 40 <= pts <= 90:
                    if pp < 180:
                        w = max(1, int(w * 0.25))   # giảm mạnh
                    elif pp < 300:
                        w = max(1, int(w * 0.55))
                    else:
                        w = int(w * 0.95)

                # ✅ nếu pp còn thấp, cấm prey quá cao (ăn phát to liền)
                if pp < 120 and pts >= 60:
                    continue

            else:
                # ---- PREDATOR ----
                # predator mid (60-110) là nguy hiểm nhất -> buff
                if 60 <= pts <= 110:
                    w = int(w * 1.80)
                else:
                    w = int(w * 1.25)

                # giảm predator quá nhỏ (30-55) kẻo thành mồi sớm
                if pts <= 55 and pp >= 120:
                    w = max(1, int(w * 0.70))

                # đừng để predator quá khủng ở đầu game
                if pts >= 140 and pp < 200:
                    w = max(1, int(w * 0.45))

            e2 = dict(e)
            e2["weight"] = w
            pool.append(e2)

        return pool

    def update(self, dt, player_points, preys, predators, camera, map_id=1):
        enemies = self.enemies_cfg.get(f"map{int(map_id)}", [])
        if not enemies:
            return

        pp = int(player_points)

        # =========================
        # 1) SPAWN PREY
        # =========================
        self.prey_timer += dt
        prey_interval = max(self.prey_min_interval, self.prey_base_interval - min(0.08, pp / 4200.0))

        if self.prey_timer >= prey_interval:
            self.prey_timer = 0.0
            pool = self._build_pool(enemies, pp, preys, want_predator=False)
            if pool:
                enemy = _weighted_choice(pool)
                if enemy:
                    x, y = self._spawn_pos_outside_view(camera)

                    fish_folder = enemy["path"]
                    points = int(enemy.get("points", 10))
                    speed = float(enemy.get("speed", 120))
                    ai = enemy.get("ai", "wander")

                    if ai == "shy":
                        preys.append(ShyPreyFish((x, y), fish_folder, points, speed))
                    else:
                        preys.append(PreyFish((x, y), fish_folder, points, speed, ai))

        # =========================
        # 2) SPAWN PREDATOR
        # =========================
        self.pred_timer += dt

        # ✅ tăng áp lực khi pp cao, nhưng không quá gắt
        danger_boost = min(0.18, pp / 1100.0)
        pred_interval = max(self.pred_min_interval, self.pred_base_interval - danger_boost)

        if self.pred_timer >= pred_interval:
            self.pred_timer = 0.0

            # cap predator: đủ để chết được nhưng không “loạn”
            max_pred = 2 + pp // 160
            max_pred = min(max_pred, 8)

            if len(predators) >= max_pred:
                return

            pool = self._build_pool(enemies, pp, preys, want_predator=True)
            if pool:
                enemy = _weighted_choice(pool)
                if enemy:
                    x, y = self._spawn_pos_outside_view(camera)
                    predators.append(
                        PredatorFish(
                            pos=(x, y),
                            fish_folder=enemy["path"],
                            points=int(enemy.get("points", 80)),
                        )
                    )
