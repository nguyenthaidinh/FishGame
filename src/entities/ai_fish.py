# src/entities/ai_fish.py
import random
import pygame
from src.entities.animated_sprite import AnimatedSprite


class PredatorFish:
    """
    Cá săn mồi (AI độc lập):
    - scale theo points (cá càng điểm cao càng to)
    - phát hiện player theo aggro_radius (tăng theo points)
    - chase mượt (có slowdown khi sát mục tiêu)
    - wander khi không thấy player
    """

    def __init__(self, pos, fish_folder, points=80):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(0, 0)

        self.points = int(points)
        self.alive = True

        # =========================
        # SCALE + HITBOX theo points
        # =========================
        p = max(1, min(320, self.points))

        # scale: ~1.05 -> ~2.10
        self.scale = 1.05 + (p / 320.0) * 1.05
        self.scale = max(0.95, min(self.scale, 2.20))

        # hit radius tăng theo scale (để collision hợp lý)
        self.hit_radius = 18.0 * self.scale

        # =========================
        # SPEED theo points (cap)
        # =========================
        # cá to nhanh hơn, nhưng không vượt quá ngưỡng
        self.speed = 150.0 + (p / 320.0) * 170.0   # ~150 -> ~320
        self.speed = max(140.0, min(self.speed, 330.0))

        # =========================
        # AGGRO theo points
        # =========================
        self.aggro_radius = 360.0 + min(900.0, p * 2.4)   # ~390 -> ~1128
        self.aggro_radius = max(360.0, min(self.aggro_radius, 1200.0))

        # chase tuning
        self._turn_smooth = 0.18  # càng cao càng “mềm”

        # wander
        self._wander_t = 0.0
        self._wander_cd = random.uniform(0.8, 1.6)
        self._wander_dir = self._rand_dir()

        # sprite
        self.sprite = AnimatedSprite(
            [f"{fish_folder}/swim_01.png", f"{fish_folder}/swim_02.png"],
            fps=6
        )

    def _rand_dir(self):
        v = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        if v.length_squared() > 0.01:
            v = v.normalize()
        else:
            v = pygame.Vector2(1, 0)
        return v

    def rect(self):
        r = self.hit_radius
        return pygame.Rect(
            int(self.pos.x - r),
            int(self.pos.y - r),
            int(r * 2),
            int(r * 2),
        )

    def update(self, dt, world_w, world_h, players):
        if not self.alive:
            return

        # =========================
        # find nearest player
        # =========================
        target, best_d2 = None, 10**18
        for p in players or []:
            d2 = (p.pos - self.pos).length_squared()
            if d2 < best_d2:
                best_d2 = d2
                target = p

        # =========================
        # CHASE nếu trong aggro
        # =========================
        if target and best_d2 <= self.aggro_radius ** 2:
            v = target.pos - self.pos
            dist = v.length()

            if dist > 1:
                dirv = v / dist

                # slowdown khi sát mục tiêu (đỡ rung)
                slow = min(1.0, dist / 150.0)

                desired = dirv * self.speed * slow
                self.vel += (desired - self.vel) * min(1.0, dt * 6.0)
        else:
            # =========================
            # WANDER
            # =========================
            self._wander_t += dt
            if self._wander_t >= self._wander_cd:
                self._wander_t = 0.0
                self._wander_cd = random.uniform(0.8, 1.6)
                self._wander_dir = self._rand_dir()

            desired = self._wander_dir * (self.speed * 0.55)
            self.vel += (desired - self.vel) * min(1.0, dt * 3.0)

        # clamp velocity
        if self.vel.length_squared() > 1:
            maxv = self.speed
            if self.vel.length() > maxv:
                self.vel = self.vel.normalize() * maxv

        # flip
        if self.vel.x != 0:
            self.sprite.flip_x = self.vel.x < 0

        # move
        self.pos += self.vel * dt
        self.pos.x = max(0, min(world_w, self.pos.x))
        self.pos.y = max(0, min(world_h, self.pos.y))

        self.sprite.update(dt)

    def draw(self, screen, camera, font):
        if not self.alive:
            return

        img = self.sprite.get_image(scale=self.scale)
        rect = img.get_rect(center=camera.world_to_screen(self.pos))
        screen.blit(img, rect)

        if font:
            p = camera.world_to_screen(self.pos)
            label = str(self.points)
            txt = font.render(label, True, (255, 255, 255))
            out = font.render(label, True, (0, 0, 0))
            y = int(p.y - rect.height // 2 - 12)
            screen.blit(out, out.get_rect(center=(int(p.x) + 1, y + 1)))
            screen.blit(txt, txt.get_rect(center=(int(p.x), y)))
