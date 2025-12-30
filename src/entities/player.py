# src/entities/player.py
import pygame
from src.entities.animated_sprite import AnimatedSprite


class PlayerFish:
    def __init__(self, pos, controls, fish_folder):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(0, 0)

        self.speed = 280.0

        # progression
        self.points = 5
        self.scale = 1.0

        # lives + invincible
        self.lives = 3
        self.invincible = 0.0          # i-frames sau hit (blink ngắn)
        self.invincible_time = 0.0     # bất tử từ thưởng (10/20/30s)
        self.shield_tier = 0           # 0/1/2/3 -> HUD icon thuong1/2/3

        # buffs
        self.x2_time = 0.0             # x2 điểm theo thời gian

        self.controls = controls

        self.sprite = AnimatedSprite(
            [f"{fish_folder}/swim_01.png", f"{fish_folder}/swim_02.png"],
            fps=8
        )

    # ---------- SCORE ----------
    def add_points(self, pts: int) -> int:
        """Cộng điểm, tự nhân 2 nếu đang x2. Trả về số điểm thực cộng."""
        mult = 2 if self.x2_time > 0 else 1
        gained = int(pts) * mult
        self.points += gained
        return gained

    def _update_scale(self):
        # 5 điểm ~1.0+, 226 điểm ~2.2 (xấp xỉ)
        target = 1.0 + min(1.2, (self.points / 226.0) * 1.2)
        self.scale += (target - self.scale) * 0.10  # smooth

    # ---------- ITEMS ----------
    def apply_item(self, kind: str):
        if kind == "x2":
            self.x2_time = max(self.x2_time, 12.0)

        elif kind == "shield1":
            self.invincible_time = max(self.invincible_time, 20.0)
            self.shield_tier = max(self.shield_tier, 1)

        elif kind == "shield2":
            self.invincible_time = max(self.invincible_time, 10.0)
            self.shield_tier = max(self.shield_tier, 2)

        elif kind == "shield3":
            self.invincible_time = max(self.invincible_time, 30.0)
            self.shield_tier = max(self.shield_tier, 3)

        elif kind == "heart":
            self.lives = min(3, self.lives + 1)

    # ---------- DAMAGE ----------
    def hit(self):
        # bất tử thưởng hoặc i-frames thì không trừ tiếp
        if self.invincible_time > 0 or self.invincible > 0:
            return
        self.lives -= 1
        self.invincible = 1.2

    # ---------- UPDATE ----------
    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.vel.update(0, 0)

        if keys[self.controls["left"]]:
            self.vel.x = -1
            self.sprite.flip_x = True
        if keys[self.controls["right"]]:
            self.vel.x = 1
            self.sprite.flip_x = False
        if keys[self.controls["up"]]:
            self.vel.y = -1
        if keys[self.controls["down"]]:
            self.vel.y = 1

        if self.vel.length_squared() > 0:
            self.vel = self.vel.normalize()

        self.pos += self.vel * self.speed * dt

        # timers
        if self.invincible > 0:
            self.invincible -= dt

        if self.invincible_time > 0:
            self.invincible_time -= dt
            if self.invincible_time <= 0:
                self.invincible_time = 0.0
                self.shield_tier = 0

        if self.x2_time > 0:
            self.x2_time -= dt

        self._update_scale()
        self.sprite.update(dt)

    def draw(self, screen, camera):
        img = self.sprite.get_image(scale=self.scale)
        rect = img.get_rect(center=camera.world_to_screen(self.pos))

        # blink khi đang i-frames hoặc bất tử
        blink = (self.invincible > 0) or (self.invincible_time > 0)
        if blink and int((self.invincible + self.invincible_time) * 10) % 2 == 0:
            return

        screen.blit(img, rect)
