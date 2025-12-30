# src/world/spawner.py
import random
from src.entities.prey import PreyFish, ShyPreyFish


class Spawner:
    def __init__(self, world_w, world_h, prey_values):
        self.world_w = world_w
        self.world_h = world_h
        self.prey_values = list(prey_values)

        self.timer = 0.0
        self.base_interval = 0.45

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

            # ưu tiên cá nhỏ
            w *= max(0.6, 20.0 / (v + 5))
            weights.append(w)

        return random.choices(self.prey_values, weights=weights, k=1)[0]

    def _radius_by_value(self, v: int) -> int:
        if v <= 5:
            return 8
        elif v <= 15:
            return 10
        elif v <= 30:
            return 12
        elif v <= 50:
            return 14
        return 16

    # =========================
    # Shy prey probability
    # =========================
    def _should_spawn_shy(self, map_id: int, player_points: int) -> bool:
        """
        Tỉ lệ cá nhỏ trốn chạy:
        Map 1: ~10%
        Map 2: ~14%
        Map 3: ~18%
        Có tăng nhẹ theo điểm, cap 25%
        """
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

        x = random.randint(
            max(80, left),
            min(self.world_w - 80, right)
        )
        y = random.randint(
            max(80, top),
            min(self.world_h - 80, bottom)
        )

        return x, y

    # =========================
    # Update
    # =========================
    def update(self, dt, player_points, prey_list, camera, map_id=1):
        self.timer += dt

        # spawn nhanh dần theo điểm
        interval = max(
            0.22,
            self.base_interval - min(0.18, player_points / 1200.0)
        )

        while self.timer >= interval:
            self.timer -= interval

            v = self._weighted_value(player_points)
            radius = self._radius_by_value(v)

            x, y = self._spawn_pos_near_camera(camera)

            # chỉ 1 phần cá nhỏ mới là shy
            if (
                self._should_spawn_shy(map_id, player_points)
                and v <= max(15, int(player_points * 0.8))
            ):
                prey_list.append(
                    ShyPreyFish(
                        (x, y),
                        points=v,
                        radius=radius,
                        fish_folder=None,
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
                    )
                )
