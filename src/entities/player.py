# src/entities/player.py
import pygame
from src.entities.animated_sprite import AnimatedSprite


class PlayerFish:
    def __init__(self, pos, controls, fish_folder, player_id: int = 1):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(0, 0)

        self.player_id = int(player_id)

        self.speed = 280.0

        # =========================
        # PROGRESSION
        # =========================
        self.points = 5

        # 🔥 to hơn ngay từ đầu (Lio muốn to hơn nữa)
        self.base_scale = 0.52
        self.scale = self.base_scale

        # 🔥 giảm chia để render to hơn
        self.render_div = 1.7

        # pop effect khi ăn
        self._pop = 0.0
        self._pop_strength = 0.14

        # =========================
        # LIFE + BUFFS
        # =========================
        self.lives = 3
        self.invincible = 0.0
        self.invincible_time = 0.0
        self.shield_tier = 0
        self.x2_time = 0.0

        self.controls = controls

        self.sprite = AnimatedSprite(
            [
                f"{fish_folder}/swim_01.png",
                f"{fish_folder}/swim_02.png",
            ],
            fps=8
        )

        # =========================
        # SCORE UI
        # =========================
        self._font_path = "assets/fonts/Baloo2-Bold.ttf"
        self._font = None
        self._font_size = 20
        self._label_cache = {"key": None, "surf": None}

    # =========================
    # SCORE
    # =========================
    def add_points(self, pts: int) -> int:
        mult = 2 if self.x2_time > 0 else 1
        gained = int(pts) * mult
        self.points += gained

        # pop ăn là thấy phình
        self._pop = max(self._pop, 0.18)

        self._label_cache["key"] = None
        return gained

    # =========================
    # SCALE LOGIC
    # =========================
    def _scale_target_from_points(self) -> float:
        p = float(self.points)

        # tăng rõ giai đoạn đầu
        if p < 500:
            target = self.base_scale + p * 0.0012
        elif p < 1500:
            target = (self.base_scale + 500 * 0.0012) + (p - 500) * 0.0008
        else:
            target = (self.base_scale + 500 * 0.0012) + (1000 * 0.0008) + (p - 1500) * 0.0004

        return min(target, 4.6)

    def _update_scale(self):
        target = self._scale_target_from_points()
        self.scale += (target - self.scale) * 0.25

    # =========================
    # ITEMS
    # =========================
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

    # =========================
    # DAMAGE
    # =========================
    def hit(self):
        if self.invincible_time > 0 or self.invincible > 0:
            return
        self.lives -= 1
        self.invincible = 1.2

    # =========================
    # UPDATE
    # =========================
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

        # pop decay
        if self._pop > 0:
            self._pop -= dt
            if self._pop < 0:
                self._pop = 0

        self._update_scale()
        self.sprite.update(dt)

    # =========================
    # LABEL UI (khung điểm đẹp)
    # =========================
    def _ensure_font(self, size: int):
        if self._font is None or size != self._font_size:
            self._font_size = size
            try:
                self._font = pygame.font.Font(self._font_path, size)
            except Exception:
                self._font = pygame.font.Font(None, size)
            self._label_cache["key"] = None

    def _theme_colors(self):
        # P1 xanh; P2 cam đỏ
        if self.player_id == 2:
            bg1 = (255, 120, 80, 210)
            bg2 = (255, 90, 60, 210)
            stroke = (255, 235, 220, 220)
            text = (255, 255, 255)
        else:
            bg1 = (70, 200, 170, 210)
            bg2 = (40, 170, 150, 210)
            stroke = (230, 255, 245, 220)
            text = (255, 255, 255)
        return bg1, bg2, stroke, text

    def _render_label(self):
        # font scale nhẹ theo cá để nhìn “pro”
        size = int(18 + min(10, (self.scale - self.base_scale) * 4.5))  # 18..28
        self._ensure_font(size)

        label = f"{int(self.points)}"
        cache_key = (label, size, self.player_id)
        if self._label_cache["key"] == cache_key and self._label_cache["surf"] is not None:
            return self._label_cache["surf"]

        bg1, bg2, stroke, text = self._theme_colors()

        txt = self._font.render(label, True, text)
        out = self._font.render(label, True, (0, 0, 0))

        pad_x, pad_y = 14, 8
        w = txt.get_width() + pad_x * 2
        h = txt.get_height() + pad_y * 2

        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        r = surf.get_rect()
        radius = 12

        # shadow
        shadow = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 80), r, border_radius=radius)
        surf.blit(shadow, (2, 2))

        # gradient fake: vẽ 2 rect chồng nhau
        pygame.draw.rect(surf, bg2, r, border_radius=radius)
        top_half = pygame.Rect(0, 0, w, h // 2 + 1)
        pygame.draw.rect(surf, bg1, top_half, border_radius=radius)

        # stroke
        pygame.draw.rect(surf, stroke, r, 2, border_radius=radius)

        # text outline
        x, y = pad_x, pad_y
        surf.blit(out, (x - 1, y))
        surf.blit(out, (x + 1, y))
        surf.blit(out, (x, y - 1))
        surf.blit(out, (x, y + 1))
        surf.blit(txt, (x, y))

        self._label_cache["key"] = cache_key
        self._label_cache["surf"] = surf
        return surf

    # =========================
    # DRAW
    # =========================
    def draw(self, screen, camera):
        # pop scale
        pop_mul = 1.0
        if self._pop > 0:
            t = self._pop / 0.18
            pop_mul = 1.0 + self._pop_strength * (t * t)

        render_scale = (self.scale * pop_mul) / self.render_div

        img = self.sprite.get_image(scale=render_scale)
        center = camera.world_to_screen(self.pos)
        rect = img.get_rect(center=center)

        blink = (self.invincible > 0) or (self.invincible_time > 0)
        if blink and int((self.invincible + self.invincible_time) * 10) % 2 == 0:
            return

        screen.blit(img, rect)

        # label above head
        label = self._render_label()
        offset_y = int(rect.height * 0.78) + 10
        sx = rect.centerx - label.get_width() // 2
        sy = rect.centery - offset_y - label.get_height()
        screen.blit(label, (sx, sy))
