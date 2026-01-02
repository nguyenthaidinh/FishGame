# src/world/spawner.py
import os, json, random
from src.entities.prey import PreyFish, ShyPreyFish


# =========================
# Helpers
# =========================
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


# =========================
# Spawner (NEW – CHUẨN)
# =========================
class Spawner:
    def __init__(self, world_w, world_h):
        self.world_w = world_w
        self.world_h = world_h

        self.timer = 0.0
        self.base_interval = 0.45

        # load JSON 1 lần
        self.enemies_cfg = _load_fish_enemies()

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
    # Shy prey probability
    # =========================
    def _should_spawn_shy(self, map_id: int, player_points: int) -> bool:
        base = 0.10 if map_id == 1 else 0.14 if map_id == 2 else 0.18
        bonus = min(0.06, player_points / 2000.0)
        return random.random() < min(0.25, base + bonus)

    # =========================
    # Update (JSON-DRIVEN)
    # =========================
    def update(self, dt, player_points, prey_list, camera, map_id=1):
        self.timer += dt
        interval = max(0.22, self.base_interval - min(0.18, player_points / 1200.0))

        enemies = self.enemies_cfg.get(f"map{int(map_id)}", [])
        if not enemies:
            return

        while self.timer >= interval:
            self.timer -= interval

            # chọn 1 loại cá từ JSON
            enemy = random.choice(enemies)

            points = int(enemy.get("points", 5))
            size = int(enemy.get("size", 16))
            fish_folder = enemy.get("path")

            # radius logic → hitbox + scale
            radius = int(size * 0.25)

            x, y = self._spawn_pos_near_camera(camera)

            # cá nhút nhát chỉ áp dụng cho cá KHÔNG ăn player
            if (
                self._should_spawn_shy(map_id, player_points)
                and not enemy.get("can_eat_player", False)
            ):
                prey_list.append(
                    ShyPreyFish(
                        (x, y),
                        points=points,
                        radius=radius,
                        fish_folder=fish_folder,
                        flee_radius=260.0,
                        flee_boost=2.2,
                    )
                )
            else:
                prey_list.append(
                    PreyFish(
                        (x, y),
                        points=points,
                        radius=radius,
                        fish_folder=fish_folder,
                    )
                )
