# src/entities/shy_prey_fish.py
import random
import pygame
from typing import Optional

from src.entities.prey import PreyFish


class ShyPreyFish(PreyFish):
    """
    Cá nhút nhát:
    - player tới gần thì chạy trốn
    """

    def __init__(
        self,
        pos,
        fish_folder: Optional[str] = None,
        points: int = 20,
        speed: float = 130.0,
        flee_radius: float = 260.0,
        flee_boost: float = 2.2,
        fps: int = 8,
    ):
        super().__init__(
            pos=pos,
            fish_folder=fish_folder,
            points=points,
            speed=speed,
            ai="wander",
            fps=fps,
        )

        self.flee_radius = float(flee_radius)
        self.flee_boost = float(flee_boost)

        self._wander_t = random.random() * 10.0

    def update(self, dt, world_w, world_h, players=None, **kwargs):
        flee_dir = None

        if players:
            nearest = min(players, key=lambda p: (p.pos - self.pos).length_squared())
            d2 = (nearest.pos - self.pos).length_squared()

            if d2 <= self.flee_radius ** 2:
                v = self.pos - nearest.pos
                if v.length_squared() > 1:
                    flee_dir = v.normalize()

        if flee_dir is not None:
            target = flee_dir * (self.base_speed * self.flee_boost)
            self.vel += (target - self.vel) * min(1.0, dt * 7.0)
            if self.vel.length_squared() > 1:
                self.vel = self.vel.normalize() * (self.base_speed * self.flee_boost)
        else:
            # wander nhẹ
            self._wander_t += dt
            if self._wander_t > 1.1:
                self._wander_t = 0.0
                self.vel = self.vel.rotate_rad(random.uniform(-0.65, 0.65))
            if self.vel.length_squared() > 1:
                self.vel = self.vel.normalize() * self.base_speed

        super().update(dt, world_w, world_h)
