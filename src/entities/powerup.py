import random
import math             
import pygame
from src.entities.entity import Entity

ASSET_DIR = "assets/ui/items"

class PowerUp(Entity):
    """
    kind:
      - "shield1","shield2","shield3"
      - "x2"
      - "heart"
    """
    def __init__(self, pos, kind, direction=1, speed=140):
        super().__init__(pos)
        self.kind = kind
        self.direction = direction
        self.speed = float(speed)

        self.radius = 22
        self._t = random.random() * 10.0

    def rect(self):
        r = self.radius
        return pygame.Rect(self.pos.x - r, self.pos.y - r, r * 2, r * 2)

    def asset_path(self):
        if self.kind == "shield1":
            return f"{ASSET_DIR}/thuong1.png"
        if self.kind == "shield2":
            return f"{ASSET_DIR}/thuong2.png"
        if self.kind == "shield3":
            return f"{ASSET_DIR}/thuong3.png"
        if self.kind == "x2":
            return f"{ASSET_DIR}/x2diem.png"
        if self.kind == "heart":
            return f"{ASSET_DIR}/thuong.png"
        return None

    def update(self, dt, world_w, world_h, **kwargs):
        self._t += dt
        self.pos.y += self.speed * dt * self.direction

        if self.pos.y < -120 or self.pos.y > world_h + 120:
            self.alive = False

    def draw(self, screen, camera, assets, **kwargs):
        p = camera.world_to_screen(self.pos)

        y = p.y + (math.sin(self._t * 4.0) * 3.0)

        path = self.asset_path()
        if not path:
            return

        img = assets.image(path)
        scale = 0.55
        w = max(2, int(img.get_width() * scale))
        h = max(2, int(img.get_height() * scale))
        surf = pygame.transform.smoothscale(img, (w, h))
        screen.blit(surf, surf.get_rect(center=(int(p.x), int(y))))
