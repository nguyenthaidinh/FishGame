# src/world/spawner.py
import os, json, random
from src.entities.prey import PreyFish, ShyPreyFish

def _project_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def _load_fish_enemies():
    root = _project_root()
    path = os.path.join(root, "data", "fish_enemies.json")
    if not os.path.exists(path):
        print("⚠ fish_enemies.json not found:", path)
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f) or {}
    except Exception as e:
        print("⚠ fish_enemies.json read error:", e)
        return {}

class Spawner:
    def __init__(self, world_w, world_h, prey_values):
        self.world_w = world_w
        self.world_h = world_h
        self.prey_values = list(prey_values)

        self.timer = 0.0
        self.base_interval = 0.45

        # ✅ load config 1 lần
        self.enemies_cfg = _load_fish_enemies()

    # =========================
    # Spawn value logic
    # =========================
    def _weighted_value(self, player_points: int) -> int:
        weights = []
        for v in self.prey_values:
            if v <= max(2, int(player_points * 0.8)):
                w = 8.0
            elif v <= player_points:
                w = 4.0
            elif v <= int(player_points * 1.3):
                w = 1.6
            else:
                w = 0.35
            w *= max(0.6, 20.0 / (v + 5))
            weights.append(w)
        return random.choices(self.prey_values, weights=weights, k=1)[0]

    def _radius_by_value(self, v: int) -> int:
        if v <= 5: return 8
        if v <= 15: return 10
        if v <= 30: return 12
        if v <= 50: return 14
        return 16

    # =========================
    # Shy prey probability
    # =========================
    def _should_spawn_shy(self, map_id: int, player_points: int) -> bool:
        base = 0.10 if map_id == 1 else 0.14 if map_id == 2 else 0.18
        bonus = min(0.06, player_points / 2000.0)
        return random.random() < min(0.25, base + bonus)

    # =========================
    # Spawn position near camera
    # =========================
    def _spawn_pos_near_camera(self, camera):
        margin = 220
        left = int(camera.offset.x) - margin
        right = int(camera.offset.x + camera.sw) + margin
        top = int(camera.offset.y) - margin
        bottom = int(camera.offset.y + camera.sh) + margin

        x = random.randint(max(80, left), min(self.world_w - 80, right))
        y = random.randint(max(80, top), min(self.world_h - 80, bottom))
        return x, y

    # =========================
    # ✅ pick enemy sprite folder from JSON
    # =========================
    def _pick_enemy_folder(self, map_id: int, value_points: int):
        key = f"map{int(map_id)}"
        arr = self.enemies_cfg.get(key, [])
        if not arr:
            return None

        # rule đơn giản: điểm nhỏ -> chọn cá size nhỏ
        # (Lio có thể nâng cấp mapping sau)
        candidates = []
        for e in arr:
            size = int(e.get("size", 20))
            # value_points càng lớn -> cho phép size lớn hơn
            # điểm 2..100 -> size 12..42
            allow = 12 + min(30, value_points * 0.35)
            if size <= allow:
                candidates.append(e)

        if not candidates:
            candidates = arr

        chosen = random.choice(candidates)
        return chosen.get("path")  # chính là fish_folder

    # =========================
    # Update
    # =========================
    def update(self, dt, player_points, prey_list, camera, map_id=1):
        self.timer += dt
        interval = max(0.22, self.base_interval - min(0.18, player_points / 1200.0))

        while self.timer >= interval:
            self.timer -= interval

            v = self._weighted_value(player_points)
            radius = self._radius_by_value(v)
            x, y = self._spawn_pos_near_camera(camera)

            fish_folder = self._pick_enemy_folder(map_id, v)

            if self._should_spawn_shy(map_id, player_points) and v <= max(15, int(player_points * 0.8)):
                prey_list.append(
                    ShyPreyFish(
                        (x, y),
                        points=v,
                        radius=radius,
                        fish_folder=fish_folder,  # ✅ có sprite
                        flee_radius=260.0,
                        flee_boost=2.2,
                    )
                )
            else:
                prey_list.append(
                    PreyFish(
                        (x, y),
                        points=v,
                        radius=radius,
                        fish_folder=fish_folder,  # ✅ có sprite
                    )
                )
