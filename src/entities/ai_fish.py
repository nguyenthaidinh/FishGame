import random
import pygame
from src.entities.animated_sprite import AnimatedSprite

class PredatorFish:
    def __init__(self, pos, fish_folder, points=80):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(0, 0)

        self.points = int(points)   # điểm của predator = “kích thước/độ nguy hiểm”
        self.alive = True

        self.speed = 140 + min(240, self.points) * 0.55
        self.scale = 1.2 + min(1.0, self.points / 200.0)

        self.aggro_radius = 560
        self.hit_radius = 20

        # wander
        self._wander_t = 0.0
        self._wander_cd = random.uniform(0.8, 1.8)
        self._wander_dir = self._rand_dir()

        self.sprite = AnimatedSprite(
            [f"{fish_folder}/swim_01.png", f"{fish_folder}/swim_02.png"],
            fps=6
        )

    def _rand_dir(self):
        v = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        if v.length_squared() > 0.01:
            v = v.normalize()
        return v

    def rect(self):
        r = self.hit_radius * self.scale
        return pygame.Rect(self.pos.x - r, self.pos.y - r, r * 2, r * 2)

    def update(self, dt, world_w, world_h, players):
        if not self.alive:
            return

        # nearest player
        target, best_d2 = None, 10**18
        for p in players:
            d2 = (p.pos - self.pos).length_squared()
            if d2 < best_d2:
                best_d2 = d2
                target = p

        if target and best_d2 <= self.aggro_radius ** 2:
            # chase
            v = target.pos - self.pos
            if v.length_squared() > 1:
                v = v.normalize()
            self.vel = v
        else:
            # wander
            self._wander_t += dt
            if self._wander_t >= self._wander_cd:
                self._wander_t = 0.0
                self._wander_cd = random.uniform(0.8, 1.8)
                self._wander_dir = self._rand_dir()
            self.vel = self._wander_dir

        if self.vel.x != 0:
            self.sprite.flip_x = self.vel.x < 0

        self.pos += self.vel * self.speed * dt
        self.pos.x = max(0, min(world_w, self.pos.x))
        self.pos.y = max(0, min(world_h, self.pos.y))

        self.sprite.update(dt)

    def draw(self, screen, camera, font):
        if not self.alive:
            return
        img = self.sprite.get_image(scale=self.scale)
        rect = img.get_rect(center=camera.world_to_screen(self.pos))
        screen.blit(img, rect)

        # points above head
        p = camera.world_to_screen(self.pos)
        label = str(self.points)
        txt = font.render(label, True, (255, 255, 255))
        out = font.render(label, True, (0, 0, 0))
        y = int(p.y - rect.height // 2 - 12)
        screen.blit(out, out.get_rect(center=(int(p.x)+1, y+1)))
        screen.blit(txt, txt.get_rect(center=(int(p.x), y)))
