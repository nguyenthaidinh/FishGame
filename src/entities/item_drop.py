import random
from src.entities.obstacle import Obstacle
from src.entities.powerup import PowerUp

class DropSpawner:
    """Spawn obstacles + powerups falling (or rising) randomly."""
    def __init__(self, world_w, world_h):
        self.world_w = world_w
        self.world_h = world_h
        self.t = 0.0

    def update(self, dt, drops, map_id=1, avg_points=5):
        self.t += dt

        base_interval = 6.8 if map_id == 1 else 6.0 if map_id == 2 else 5.2
        interval = max(3.8, base_interval - (avg_points / 600.0))

        if self.t < interval:
            return
        self.t = 0.0

        # hướng rơi: 50/50
        direction = 1 if random.random() < 0.5 else -1
        y = -60 if direction == 1 else self.world_h + 60
        x = random.randint(80, self.world_w - 80)

        # --- weights theo yêu cầu ---
        # obstacles thường xuyên
        # shield2 nhiều, shield1 ít hơn, shield3 ít nhất
        # heart cực hiếm
        # x2 trung bình
        kinds = [
            "ob1","ob2","ob3","ob4","ob5","ob6",
            "shield2","shield1","shield3",
            "x2",
            "heart"
        ]
        weights = [
            12,12,10,10,9,9,
            5, 3, 2,
            4,
            1
        ]
        kind = random.choices(kinds, weights=weights, k=1)[0]

        speed = 140 if map_id == 1 else 160 if map_id == 2 else 180

        if kind.startswith("ob"):
            ob_id = int(kind[-1])
            drops.append(Obstacle((x, y), ob_id=ob_id, direction=direction, speed=speed))
        else:
            drops.append(PowerUp((x, y), kind=kind, direction=direction, speed=speed))
