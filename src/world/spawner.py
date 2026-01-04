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


# =========================
# Spawner
# =========================
class Spawner:
    def __init__(self, world_w, world_h):
        self.world_w = world_w
        self.world_h = world_h

        # 2 nhịp spawn
        self.prey_timer = 0.0
        self.pred_timer = 0.0

        # PREY: đủ mồi để chơi "đã"
        self.prey_base_interval = 0.62
        self.prey_min_interval  = 0.46

        # PREDATOR: có áp lực nhưng không spam
        self.pred_base_interval = 1.15
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

    def _is_pred(self, e):
        ai = e.get("ai", "wander")
        role = e.get("role", "prey")
        return (role == "predator" or ai == "predator")

    def _build_pool(self, enemies, pp, preys, want_predator: bool):
        small_count = sum(1 for p in preys if getattr(p, "points", 0) <= 5)

        pool = []
        for e in enemies:
            pts = int(e.get("points", 5))
            mn = int(e.get("min_pp", 0))
            mx = int(e.get("max_pp", 999999))
            is_pred = self._is_pred(e)

            # đúng loại
            if want_predator and (not is_pred):
                continue
            if (not want_predator) and is_pred:
                continue

            # theo khoảng pp
            if not (mn <= pp <= mx):
                continue

            # chặn spam cá 5 (để vẫn có mồi nhưng không loạn)
            if (not want_predator) and pts <= 5:
                limit = 11 if pp < 60 else (8 if pp < 140 else 6)
                if small_count >= limit:
                    continue

            # ===== cân tỉ lệ (không sửa JSON) =====
            w = int(e.get("weight", 1))

            if not want_predator:
                # PREY
                if pts <= 5 and pp >= 60:
                    w = max(1, int(w * 0.75))
                if 8 <= pts <= 30:
                    w = int(w * 1.35)

                # nerf prey 40-90 early để tránh phình quá nhanh
                if 40 <= pts <= 90:
                    if pp < 120:
                        w = max(1, int(w * 0.55))
                    elif pp < 220:
                        w = max(1, int(w * 0.75))
                    else:
                        w = int(w * 1.05)

            else:
                # PREDATOR: xuất hiện đều hơn chút
                w = int(w * 1.25)

                # predator quá khủng giai đoạn sớm -> giảm
                if pts >= 120 and pp < 160:
                    w = max(1, int(w * 0.60))

            e2 = dict(e)
            e2["weight"] = max(1, int(w))
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
        prey_interval = max(self.prey_min_interval, self.prey_base_interval - min(0.10, pp / 3600.0))

        if self.prey_timer >= prey_interval:
            self.prey_timer = 0.0

            pool = self._build_pool(enemies, pp, preys, want_predator=False)
            enemy = _weighted_choice(pool)
            if enemy:
                x, y = self._spawn_pos_outside_view(camera)

                fish_folder = enemy["path"]
                points = int(enemy.get("points", 10))
                speed = float(enemy.get("speed", 120))
                ai = enemy.get("ai", "wander")

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

        # =========================
        # 2) SPAWN PREDATOR
        # =========================
        self.pred_timer += dt

        # danger boost: pp càng cao predator càng ra nhanh (kịch tính)
        danger_boost = min(0.25, pp / 900.0)     # cap
        pred_interval = max(self.pred_min_interval, self.pred_base_interval - danger_boost)

        if self.pred_timer >= pred_interval:
            self.pred_timer = 0.0

            # cap predator cơ bản
            max_pred = 2 + pp // 180
            max_pred = min(max_pred, 7)

            # pool predator
            pool = self._build_pool(enemies, pp, preys, want_predator=True)
            enemy = _weighted_choice(pool)
            if not enemy:
                return

            pts = int(enemy.get("points", 80))
            is_boss = bool(enemy.get("boss", False)) or (pts >= 500)

            # Boss hiếm: cho phép "vượt cap" thêm 1 con (để có lúc cực kịch tính)
            # nhưng chỉ khi spawn đúng boss
            if len(predators) >= max_pred:
                if not is_boss or len(predators) >= (max_pred + 1):
                    return

            x, y = self._spawn_pos_outside_view(camera)
            predators.append(
                PredatorFish(
                    pos=(x, y),
                    fish_folder=enemy["path"],
                    points=pts,
                )
            )
