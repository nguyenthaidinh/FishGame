# src/entities/prey.py
import random
import pygame
from typing import Optional

from src.entities.entity import Entity
from src.entities.animated_sprite import AnimatedSprite


class PreyFish(Entity):
    """
    Cá mồi cơ bản:
    - Kích thước (scale + hitbox) lấy từ JSON (size)
    - radius dùng cho va chạm
    - scale dùng cho hiển thị (tuyến tính theo radius)
    """

    def __init__(
        self,
        pos,
        points: int,
        radius: int,
        fish_folder: Optional[str] = None,
        speed_range=(35, 90),
        fps=8,
    ):
        super().__init__(pos)

        # ===== DATA FROM JSON =====
        self.points = int(points)
        self.radius = int(radius)

        # ===== SCALE TUYẾN TÍNH THEO RADIUS (CHUẨN) =====
        # Quy ước:
        # - radius ~ size * 0.35 (Spawner)
        # - BASE_RADIUS là radius chuẩn của cá nhỏ (map dễ)
        BASE_RADIUS = 16.0
        BASE_SCALE = 0.40

        self.scale = (self.radius / BASE_RADIUS) * BASE_SCALE
        self.scale = max(0.25, min(self.scale, 1.25))  # clamp an toàn

        # ===== MOVE RANDOM =====
        ang = random.random() * 6.283
        spd = random.randint(int(speed_range[0]), int(speed_range[1]))
        self.vel = pygame.Vector2(spd, 0).rotate_rad(ang)

        # ===== SPRITE =====
        self.sprite: Optional[AnimatedSprite] = None
        self.flip_x = False

        if fish_folder:
            self.sprite = AnimatedSprite(
                [
                    f"{fish_folder}/swim_01.png",
                    f"{fish_folder}/swim_02.png",
                ],
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
        r = self.radius
        return pygame.Rect(
            int(self.pos.x - r),
            int(self.pos.y - r),
            int(r * 2),
            int(r * 2),
        )

    # =========================
    # MOVEMENT
    # =========================
    def _bounce_bounds(self, world_w, world_h):
        if self.pos.x < 20:
            self.pos.x = 20
            self.vel.x *= -1
        elif self.pos.x > world_w - 20:
            self.pos.x = world_w - 20
            self.vel.x *= -1

        if self.pos.y < 20:
            self.pos.y = 20
            self.vel.y *= -1
        elif self.pos.y > world_h - 20:
            self.pos.y = world_h - 20
            self.vel.y *= -1

    def update(self, dt, world_w, world_h, **kwargs):
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
            pygame.draw.circle(
                screen,
                (255, 170, 90),
                (int(p.x), int(p.y)),
                self.radius,
            )
            pygame.draw.circle(
                screen,
                (0, 0, 0),
                (int(p.x), int(p.y)),
                self.radius,
                2,
            )
            r_for_label = self.radius

        if font:
            self._ensure_label(font)
            tx = int(p.x)
            ty = int(p.y - r_for_label - 12)

            screen.blit(
                self._label_outline,
                self._label_outline.get_rect(center=(tx + 1, ty + 1)),
            )
            screen.blit(
                self._label_surf,
                self._label_surf.get_rect(center=(tx, ty)),
            )


# =========================
# SHY PREY
# =========================
class ShyPreyFish(PreyFish):
    """
    Cá mồi nhút nhát:
    - Player tới gần thì chạy trốn
    """

    def __init__(
        self,
        pos,
        points: int,
        radius: int,
        fish_folder: Optional[str] = None,
        flee_radius: float = 260.0,
        flee_boost: float = 2.2,
        calm_turn_rate: float = 0.10,
        speed_range=(35, 90),
        fps=8,
    ):
        super().__init__(
            pos=pos,
            points=points,
            radius=radius,
            fish_folder=fish_folder,
            speed_range=speed_range,
            fps=fps,
        )

        self.flee_radius = float(flee_radius)
        self.flee_boost = float(flee_boost)
        self.calm_turn_rate = float(calm_turn_rate)

        self.base_speed = max(35.0, self.vel.length())
        self.wander_t = random.random() * 10.0

    def update(self, dt, world_w, world_h, players=None, **kwargs):
        flee_dir = None

        if players:
            nearest = min(
                players,
                key=lambda p: (p.pos - self.pos).length_squared(),
            )
            d2 = (nearest.pos - self.pos).length_squared()

            if d2 <= self.flee_radius ** 2:
                v = self.pos - nearest.pos
                if v.length_squared() > 1:
                    flee_dir = v.normalize()

        if flee_dir is not None:
            target_vel = flee_dir * (self.base_speed * self.flee_boost)
            self.vel += (target_vel - self.vel) * min(1.0, dt * 6.0)
        else:
            self.wander_t += dt
            if self.wander_t > 1.2:
                self.wander_t = 0.0
                self.vel = self.vel.rotate_rad(random.uniform(-0.7, 0.7))

            if self.vel.length_squared() > 1:
                self.vel = self.vel.normalize() * self.base_speed

        super().update(dt, world_w, world_h)
