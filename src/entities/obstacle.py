import random
import math
import pygame
from src.entities.entity import Entity

ASSET_DIR = "assets/ui/items"

class Obstacle(Entity):
    """Obstacle that damages player on touch."""
    def __init__(self, pos, ob_id: int, direction=1, speed=140):
        super().__init__(pos)
        self.kind = f"ob{int(ob_id)}"
        self.direction = direction  # 1: top->down, -1: bottom->up
        self.speed = float(speed)

        self.radius = 22
        self._t = random.random() * 10.0

    def rect(self):
        r = self.radius
        return pygame.Rect(self.pos.x - r, self.pos.y - r, r * 2, r * 2)

    def asset_path(self):
        # obstacles1.png ... obstacles6.png
        idx = int(self.kind[-1])
        return f"{ASSET_DIR}/obstacles{idx}.png"

    def update(self, dt, world_w, world_h, **kwargs):
        self._t += dt
        self.pos.y += self.speed * dt * self.direction

        # out of world -> remove
        if self.pos.y < -120 or self.pos.y > world_h + 120:
            self.alive = False

    def draw(self, screen, camera, assets, **kwargs):
        p = camera.world_to_screen(self.pos)
        y = p.y + (math.sin(self._t * 4.0) * 3.0)

        img = assets.image(self.asset_path())
        scale = 0.55
        w = max(2, int(img.get_width() * scale))
        h = max(2, int(img.get_height() * scale))
        surf = pygame.transform.smoothscale(img, (w, h))
        screen.blit(surf, surf.get_rect(center=(int(p.x), int(y))))
