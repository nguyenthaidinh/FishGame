import random
import pygame
from src.entities.prey import Prey 

class ShyPrey(Prey):
    """
    Cá mồi nhút nhát: gặp player thì chạy trốn 1 đoạn.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.flee_radius = 360
        self.flee_boost = 1.55      # chạy nhanh hơn
        self.flee_time = 0.0        # chạy trốn trong 1 khoảng ngắn

    def update(self, dt, world_w, world_h, players=None):
        # nếu có player và ở gần -> kích hoạt flee
        if players:
            nearest_d2 = 10**18
            nearest = None
            for p in players:
                d2 = (p.pos - self.pos).length_squared()
                if d2 < nearest_d2:
                    nearest_d2 = d2
                    nearest = p

            if nearest and nearest_d2 <= self.flee_radius ** 2:
                self.flee_time = 0.35  # chạy trốn 0.35s

                # hướng trốn ngược lại player
                v = self.pos - nearest.pos
                if v.length_squared() > 1:
                    v = v.normalize()
                    self.vel = v  # Prey thường có vel
                    self.speed_mul = self.flee_boost  # nếu Prey không có thì bỏ dòng này

        # fallback: gọi update gốc
        # ⚠️ Nếu Prey của Lio không có speed_mul, thì chỉ cần tạm tăng self.speed trong flee_time
        if self.flee_time > 0:
            self.flee_time -= dt
            # nếu Prey có self.speed:
            try:
                base = getattr(self, "_base_speed", None)
                if base is None:
                    self._base_speed = self.speed
                self.speed = self._base_speed * self.flee_boost
            except Exception:
                pass
        else:
            try:
                if hasattr(self, "_base_speed"):
                    self.speed = self._base_speed
            except Exception:
                pass

        super().update(dt, world_w, world_h)
