# src/entities/prey.py
import random
import pygame
from typing import Optional

from src.entities.entity import Entity
from src.entities.animated_sprite import AnimatedSprite


class PreyFish(Entity):
    """
    Cá mồi:
    - size/scale phụ thuộc points (điểm thấp nhỏ, điểm cao to)
    - speed lấy từ JSON
    - ai: wander | dart
    """

    def __init__(
        self,
        pos,
        fish_folder: Optional[str] = None,
        points: int = 10,
        speed: float = 120.0,
        ai: str = "wander",
        fps: int = 8,
    ):
        super().__init__(pos)

        self.points = int(points)
        self.ai = (ai or "wander").lower()

        # ===== SCALE THEO POINTS =====
        # clamp để không quá to / quá bé
        p = max(1, min(320, self.points))
        self.scale = 0.55 + (p / 320.0) * 1.10     # ~0.55 -> ~1.65
        self.scale = max(0.45, min(self.scale, 1.75))

        # ===== HIT RADIUS THEO SCALE =====
        # base hit radius cho cá nhỏ
        base_r = 18.0
        self.hit_radius = base_r * self.scale

        # ===== SPEED (JSON) + TINH CHỈNH NHẸ =====
        # cá to hơi nhanh hơn chút, nhưng không tăng quá nhiều
        self.base_speed = float(speed) + (p / 320.0) * 25.0

        # ===== WANDER / DART STATE =====
        self._turn_t = 0.0
        self._turn_cd = random.uniform(0.9, 1.6)

        # dart: burst ngắn
        self._dart_t = 0.0
        self._dart_cd = random.uniform(1.2, 2.4)
        self._dart_time = 0.0

        # ===== INIT VELOCITY =====
        ang = random.random() * 6.283
        self.vel = pygame.Vector2(1, 0).rotate_rad(ang) * self.base_speed

        # ===== SPRITE =====
        self.sprite: Optional[AnimatedSprite] = None
        self.flip_x = False

        if fish_folder:
            self.sprite = AnimatedSprite(
                [f"{fish_folder}/swim_01.png", f"{fish_folder}/swim_02.png"],
                fps=fps,
            )

        # ===== LABEL CACHE =====
        self._label_value = None
        self._label_surf = None
        self._label_outline = None

    # =========================
    # HITBOX
    # =========================
    def rect(self) -> pygame.Rect:
        r = self.hit_radius
        return pygame.Rect(
            int(self.pos.x - r),
            int(self.pos.y - r),
            int(r * 2),
            int(r * 2),
        )

    # =========================
    # HELPERS
    # =========================
    def _rand_dir(self) -> pygame.Vector2:
        v = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        if v.length_squared() > 0.001:
            v = v.normalize()
        else:
            v = pygame.Vector2(1, 0)
        return v

    def _bounce_bounds(self, world_w, world_h):
        pad = 40
        if self.pos.x < pad:
            self.pos.x = pad
            self.vel.x *= -1
        elif self.pos.x > world_w - pad:
            self.pos.x = world_w - pad
            self.vel.x *= -1

        if self.pos.y < pad:
            self.pos.y = pad
            self.vel.y *= -1
        elif self.pos.y > world_h - pad:
            self.pos.y = world_h - pad
            self.vel.y *= -1

    # =========================
    # AI MOVE
    # =========================
    def _update_wander(self, dt):
        self._turn_t += dt
        if self._turn_t >= self._turn_cd:
            self._turn_t = 0.0
            self._turn_cd = random.uniform(0.9, 1.6)

            # đổi hướng nhẹ
            dirv = self._rand_dir()
            target = dirv * self.base_speed
            self.vel += (target - self.vel) * 0.35

        # giữ speed ổn định
        if self.vel.length_squared() > 1:
            self.vel = self.vel.normalize() * self.base_speed

    def _update_dart(self, dt):
        # nền: vẫn wander nhưng turn nhanh hơn
        self._turn_t += dt
        if self._turn_t >= 0.55:
            self._turn_t = 0.0
            dirv = self._rand_dir()
            target = dirv * self.base_speed
            self.vel += (target - self.vel) * 0.55

        # burst ngắn
        self._dart_t += dt
        if self._dart_time > 0.0:
            self._dart_time -= dt
        else:
            if self._dart_t >= self._dart_cd:
                self._dart_t = 0.0
                self._dart_cd = random.uniform(1.2, 2.4)
                self._dart_time = random.uniform(0.18, 0.32)

        boost = 1.0
        if self._dart_time > 0.0:
            boost = 1.65  # dart mạnh

        if self.vel.length_squared() > 1:
            self.vel = self.vel.normalize() * (self.base_speed * boost)

    # =========================
    # UPDATE
    # =========================
    def update(self, dt, world_w, world_h, **kwargs):
        if self.ai == "dart":
            self._update_dart(dt)
        else:
            self._update_wander(dt)

        self.pos += self.vel * dt
        self._bounce_bounds(world_w, world_h)

        if self.vel.x < 0:
            self.flip_x = True
        elif self.vel.x > 0:
            self.flip_x = False

        if self.sprite:
            self.sprite.flip_x = self.flip_x
            self.sprite.update(dt)

    # =========================
    # LABEL
    # =========================
    def _ensure_label(self, font):
        if self._label_value == self.points and self._label_surf is not None:
            return
        self._label_value = self.points
        s = str(self.points)
        self._label_surf = font.render(s, True, (245, 250, 255))
        self._label_outline = font.render(s, True, (0, 0, 0))

    # =========================
    # DRAW
    # =========================
    def draw(self, screen, camera, assets=None, font=None, **kwargs):
        p = camera.world_to_screen(self.pos)

        if self.sprite:
            img = self.sprite.get_image(scale=self.scale)
            rect = img.get_rect(center=(int(p.x), int(p.y)))
            screen.blit(img, rect)
            r_for_label = rect.height // 2
        else:
            # fallback
            pygame.draw.circle(screen, (255, 170, 90), (int(p.x), int(p.y)), int(self.hit_radius))
            pygame.draw.circle(screen, (0, 0, 0), (int(p.x), int(p.y)), int(self.hit_radius), 2)
            r_for_label = int(self.hit_radius)

        if font:
            self._ensure_label(font)
            tx = int(p.x)
            ty = int(p.y - r_for_label - 12)

            screen.blit(self._label_outline, self._label_outline.get_rect(center=(tx + 1, ty + 1)))
            screen.blit(self._label_surf, self._label_surf.get_rect(center=(tx, ty)))
