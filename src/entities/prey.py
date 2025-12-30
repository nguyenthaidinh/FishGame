# src/entities/prey.py
import random
import pygame

from src.entities.entity import Entity
from src.entities.animated_sprite import AnimatedSprite


class PreyFish(Entity):
    """
    Cá mồi cơ bản: bơi random + bật tường.
    Optional sprite 2 frame: swim_01.png / swim_02.png
    """

    def __init__(
        self,
        pos,
        points: int,
        radius: int = 10,
        fish_folder: str | None = None,
        speed_range=(35, 90),
        fps=8,
    ):
        super().__init__(pos)
        self.points = int(points)
        self.radius = int(radius)

        # move random
        ang = random.random() * 6.283
        spd = random.randint(int(speed_range[0]), int(speed_range[1]))
        self.vel = pygame.Vector2(spd, 0).rotate_rad(ang)

        # sprite optional
        self.sprite: AnimatedSprite | None = None
        self.flip_x = False

        # ✅ scale mặc định nhỏ cho đẹp
        self.scale = self._scale_by_points(self.points)

        if fish_folder:
            self.sprite = AnimatedSprite(
                [f"{fish_folder}/swim_01.png", f"{fish_folder}/swim_02.png"],
                fps=fps,
            )

        # label cache: chỉ render lại khi điểm đổi
        self._label_value = None
        self._label_surf = None
        self._label_outline = None

    def _scale_by_points(self, pts: int) -> float:
        """
        Mồi nhỏ -> scale nhỏ, mồi lớn -> scale nhỉnh hơn.
        Không phá kiến trúc, chỉ làm đẹp.
        """
        if pts <= 5:
            return 0.38
        if pts <= 15:
            return 0.42
        if pts <= 30:
            return 0.46
        if pts <= 50:
            return 0.50
        return 0.55

    def rect(self) -> pygame.Rect:
        r = self.radius
        return pygame.Rect(self.pos.x - r, self.pos.y - r, r * 2, r * 2)

    def _bounce_bounds(self, world_w, world_h):
        # bounce bounds (kèm clamp để không kẹt tường)
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
        # move
        self.pos += self.vel * dt
        self._bounce_bounds(world_w, world_h)

        # flip by direction
        if self.vel.x < 0:
            self.flip_x = True
        elif self.vel.x > 0:
            self.flip_x = False

        # sprite
        if self.sprite:
            self.sprite.flip_x = self.flip_x
            self.sprite.update(dt)

    def _ensure_label(self, font):
        if self._label_value == self.points and self._label_surf is not None:
            return
        self._label_value = self.points
        s = str(self.points)
        self._label_surf = font.render(s, True, (245, 250, 255))
        self._label_outline = font.render(s, True, (0, 0, 0))

    def draw(self, screen, camera, assets=None, font=None, **kwargs):
        p = camera.world_to_screen(self.pos)

        # draw body
        if self.sprite:
            img = self.sprite.get_image(scale=self.scale)
            rect = img.get_rect(center=(int(p.x), int(p.y)))
            screen.blit(img, rect)
            r_for_label = max(self.radius, rect.height // 2)
        else:
            pygame.draw.circle(screen, (255, 170, 90), (int(p.x), int(p.y)), self.radius)
            pygame.draw.circle(screen, (0, 0, 0), (int(p.x), int(p.y)), self.radius, 2)
            r_for_label = self.radius

        # label
        if font:
            self._ensure_label(font)
            tx, ty = int(p.x), int(p.y - r_for_label - 12)
            screen.blit(self._label_outline, self._label_outline.get_rect(center=(tx + 1, ty + 1)))
            screen.blit(self._label_surf, self._label_surf.get_rect(center=(tx, ty)))


class ShyPreyFish(PreyFish):
    """
    Cá mồi nhút nhát:
    - Bình thường vẫn bơi random như PreyFish
    - Khi player tới gần: chạy trốn (boost tốc độ)
    - Không phải "AI full all cá": chỉ 1 số con dùng class này
    """

    def __init__(
        self,
        pos,
        points: int,
        radius: int = 10,
        fish_folder: str | None = None,
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

        # tìm player gần nhất (nếu có)
        if players:
            best_d2 = 10**18
            nearest = None
            for pl in players:
                d2 = (pl.pos - self.pos).length_squared()
                if d2 < best_d2:
                    best_d2 = d2
                    nearest = pl

            if nearest and best_d2 <= (self.flee_radius ** 2):
                v = (self.pos - nearest.pos)
                if v.length_squared() > 1:
                    flee_dir = v.normalize()

        if flee_dir is not None:
            # chạy trốn: tăng tốc, mượt
            target_vel = flee_dir * (self.base_speed * self.flee_boost)
            self.vel += (target_vel - self.vel) * min(1.0, dt * 6.0)
        else:
            # bình thường: lâu lâu bẻ lái nhẹ
            self.wander_t += dt
            if self.wander_t > 1.2:
                self.wander_t = 0.0
                turn = random.uniform(-0.7, 0.7)
                self.vel = self.vel.rotate_rad(turn)

            # giữ speed ổn định
            if self.vel.length_squared() > 1:
                self.vel = self.vel.normalize() * self.base_speed

        # rồi dùng logic base (bounce + sprite + flip)
        super().update(dt, world_w, world_h)
