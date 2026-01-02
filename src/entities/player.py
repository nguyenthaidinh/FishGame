# src/entities/player.py
import math
import pygame
from src.entities.animated_sprite import AnimatedSprite


class PlayerFish:
    def __init__(self, pos, controls, fish_folder, player_id: int = 1):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(0, 0)

        self.player_id = int(player_id)
        self.controls = controls
        self.speed = 280.0

        # =========================
        # PROGRESSION
        # =========================
        self.points = 5

        # ✅ cá khởi đầu to hơn
        self.base_scale = 0.60
        self.scale = self.base_scale

        # ✅ render to rõ hơn (giảm chia)
        self.render_div = 1.12

        # pop khi ăn
        self._pop = 0.0
        self._pop_decay = 9.0
        self._pop_strength = 0.24

        # =========================
        # LIFE + BUFFS
        # =========================
        self.lives = 3
        self.invincible = 0.0          # i-frames sau HIT (va chạm mất máu)
        self.invincible_time = 0.0     # bất tử do thưởng/khiên
        self.shield_tier = 0           # 0/1/2/3
        self.x2_time = 0.0

        # =========================
        # SPRITE
        # =========================
        self.sprite = AnimatedSprite(
            [f"{fish_folder}/swim_01.png", f"{fish_folder}/swim_02.png"],
            fps=8
        )

        # =========================
        # LABEL (điểm trên đầu cá) - KHÔNG KHUNG
        # =========================
        self._font_path = "assets/fonts/Fredoka-Bold.ttf"
        self._font = None
        self._font_size = 24
        self._label_cache_key = None
        self._label_surf = None

        # ✅ hạ label xuống 1 chút
        self.LABEL_LOWER_PX = 10

        # =========================
        # RING (chỉ khi ăn thưởng khiên/bất tử)
        # =========================
        self._ring_phase = 0.0

    # =========================
    # SCORE
    # =========================
    def add_points(self, pts: int) -> int:
        mult = 2 if self.x2_time > 0 else 1
        gained = int(pts) * mult
        if gained <= 0:
            return 0

        self.points += gained

        # ✅ pop rõ khi ăn
        self._pop = min(0.65, self._pop + self._pop_strength)

        # invalidate label cache
        self._label_cache_key = None
        return gained

    # =========================
    # SCALE TARGET (điểm -> size)
    # =========================
    def _scale_target_from_points(self) -> float:
        p = float(self.points)

        # ✅ lớn nhanh đầu game, chậm dần sau
        if p < 500:
            target = self.base_scale + p * 0.0025
        elif p < 1500:
            target = (self.base_scale + 500 * 0.0025) + (p - 500) * 0.00135
        else:
            target = (self.base_scale + 500 * 0.0025) + (1000 * 0.00135) + (p - 1500) * 0.00065

        return min(target, 6.2)

    def _update_scale(self, dt: float):
        target = self._scale_target_from_points()

        # pop giảm dần
        if self._pop > 0:
            self._pop -= dt * self._pop_decay
            if self._pop < 0:
                self._pop = 0.0

        # ✅ scale bám nhanh để thấy lớn rõ
        self.scale += (target - self.scale) * 0.40

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
            self.invincible_time = max(self.invincible_time, 12.0)
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
        # nếu đang có khiên/bất tử thưởng hoặc đang i-frame thì bỏ qua
        if self.invincible_time > 0 or self.invincible > 0:
            return
        self.lives -= 1
        self.invincible = 1.2  # i-frame sau hit

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
            if self.invincible < 0:
                self.invincible = 0.0

        if self.invincible_time > 0:
            self.invincible_time -= dt
            if self.invincible_time <= 0:
                self.invincible_time = 0.0
                self.shield_tier = 0

        if self.x2_time > 0:
            self.x2_time -= dt
            if self.x2_time < 0:
                self.x2_time = 0.0

        # scale + pop
        self._update_scale(dt)

        # ring animation phase
        self._ring_phase += dt * 7.0

        self.sprite.update(dt)

    # =========================
    # LABEL RENDER (NO BOX)
    # =========================
    def _ensure_font(self, size: int):
        if self._font is None or size != self._font_size:
            self._font_size = size
            try:
                self._font = pygame.font.Font(self._font_path, size)
            except Exception:
                self._font = pygame.font.Font(None, size)
            self._label_cache_key = None

    def _label_color(self):
        # ✅ giữ đúng màu Lio muốn (không đổi)
        return (210, 255, 245)

    def _get_label_surface(self) -> pygame.Surface:
        # size chữ tăng nhẹ theo scale
        size = int(24 + min(14, (self.scale - self.base_scale) * 4.5))
        self._ensure_font(size)

        text = str(int(self.points))
        key = (text, size)
        if key == self._label_cache_key and self._label_surf is not None:
            return self._label_surf

        color = self._label_color()

        shadow = self._font.render(text, True, (0, 0, 0))
        main = self._font.render(text, True, color)

        surf = pygame.Surface((main.get_width() + 6, main.get_height() + 6), pygame.SRCALPHA)
        surf.blit(shadow, (4, 4))
        surf.blit(main, (1, 1))

        self._label_cache_key = key
        self._label_surf = surf
        return surf

    # =========================
    # RING (glow) - CHỈ KHI ĂN THƯỞNG KHIÊN/BẤT TỬ
    # =========================
    def _draw_ring(self, screen, rect: pygame.Rect):
        # ✅ CHỈ HIỆN KHI ĂN THƯỞNG (không hiện khi va chạm mất máu)
        # (fix logic: chỉ cần invincible_time > 0 là đủ)
        if self.invincible_time <= 0:
            return

        # màu theo tier khiên
        if self.shield_tier >= 3:
            ring_color = (255, 210, 90)
        elif self.shield_tier == 2:
            ring_color = (170, 235, 255)
        elif self.shield_tier == 1:
            ring_color = (140, 255, 200)
        else:
            ring_color = (210, 255, 245)

        # pulse alpha
        pulse = 1.0 + 0.10 * (0.5 + 0.5 * math.sin(self._ring_phase))

        radius = int(max(rect.w, rect.h) * 0.62 * pulse)
        radius = max(radius, 18)

        ring = pygame.Surface((radius * 2 + 6, radius * 2 + 6), pygame.SRCALPHA)

        base_a = 150
        a = int(base_a + 90 * (0.5 + 0.5 * math.sin(self._ring_phase + 0.6)))
        a = max(70, min(230, a))

        pygame.draw.circle(ring, (*ring_color, int(a * 0.55)), (radius + 3, radius + 3), radius, 6)
        pygame.draw.circle(ring, (*ring_color, a), (radius + 3, radius + 3), radius, 3)

        screen.blit(ring, ring.get_rect(center=rect.center))

    # =========================
    # DRAW
    # =========================
    def draw(self, screen, camera):
        draw_scale = (self.scale + self._pop) / self.render_div
        img = self.sprite.get_image(scale=draw_scale)

        rect = img.get_rect(center=camera.world_to_screen(self.pos))

        # ✅ FIX "giật giật" khi mất máu:
        # không return ẩn/hiện nữa, mà nhấp nháy bằng alpha (nhẹ hơn)
        if self.invincible > 0:
            t = pygame.time.get_ticks() / 1000.0
            flick = 0.5 + 0.5 * math.sin(t * 8.0)
            alpha = int(170 + 85 * flick)  # 170..255 (mượt hơn, ít giật)
            img2 = img.copy()
            img2.set_alpha(alpha)
            screen.blit(img2, rect)
        else:
            screen.blit(img, rect)

        # ✅ vòng tròn chỉ khi ăn thưởng khiên/bất tử
        self._draw_ring(screen, rect)

        # label điểm
        label = self._get_label_surface()
        lx = rect.centerx - label.get_width() // 2
        ly = rect.top - int(rect.height * 0.42) + self.LABEL_LOWER_PX
        screen.blit(label, (lx, ly))
