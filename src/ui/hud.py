import pygame


# =========================
# Helpers
# =========================
def _scale_icon(img: pygame.Surface, size: int) -> pygame.Surface:
    if img is None:
        return None
    w, h = img.get_width(), img.get_height()
    if w <= 0 or h <= 0:
        return img
    scale = size / max(w, h)
    nw, nh = int(w * scale), int(h * scale)
    return pygame.transform.smoothscale(img, (nw, nh))


def _draw_icon(screen, img, x, y, size, alpha=255):
    if img is None:
        return
    icon = _scale_icon(img, size)
    if alpha < 255:
        icon = icon.copy()
        icon.set_alpha(alpha)
    screen.blit(icon, icon.get_rect(center=(x, y)))


# =========================
# HUD
# =========================
class HUD:
    """
    HUD ingame:
    - Points: current / target
    - Hearts: 3 mạng (heart_full / heart_empty)
    - Time, Map
    - Buff icons (x2, shield)
    """

    def __init__(self, font_big, font_small):
        self.font_big = font_big
        self.font_small = font_small

        self._loaded = False

        # icons
        self.ico_heart_full = None
        self.ico_heart_empty = None
        self.ico_x2 = None
        self.ico_sh1 = None
        self.ico_sh2 = None
        self.ico_sh3 = None

    def _ensure_icons(self, assets):
        if self._loaded:
            return
        self._loaded = True

        self.ico_heart_full = assets.image(
            "assets/ui/hud/heart_full.png"
        )
        self.ico_heart_empty = assets.image(
            "assets/ui/hud/heart_empty.png"
        )

        self.ico_x2 = assets.image("assets/items/x2diem.png")
        self.ico_sh1 = assets.image("assets/items/thuong1.png")
        self.ico_sh2 = assets.image("assets/items/thuong2.png")
        self.ico_sh3 = assets.image("assets/items/thuong3.png")

    # =========================
    # Draw
    # =========================
    def draw(
        self,
        screen,
        assets,
        lives: int,
        points: int,
        elapsed: float,
        target: int,
        player=None,
        map_name: str = "",
    ):
        self._ensure_icons(assets)

        # ===== HUD PANEL (tạm vẽ rect – có thể thay bằng ảnh sau) =====
        panel = pygame.Rect(12, 10, 460, 82)
        pygame.draw.rect(screen, (10, 20, 35), panel, border_radius=18)
        pygame.draw.rect(screen, (110, 190, 255), panel, 2, border_radius=18)

        # ===== HEARTS =====
        base_x = 34
        base_y = panel.centery
        gap = 32
        size = 26
        max_lives = 3

        for i in range(max_lives):
            cx = base_x + i * gap
            if i < lives:
                _draw_icon(
                    screen, self.ico_heart_full, cx, base_y, size
                )
            else:
                _draw_icon(
                    screen, self.ico_heart_empty, cx, base_y, size
                )

        # ===== POINTS =====
        t_points = self.font_big.render(
            f"{points} / {target}",
            True,
            (240, 245, 255),
        )
        screen.blit(t_points, (130, 18))

        # ===== TIME + MAP =====
        mm = int(elapsed) // 60
        ss = int(elapsed) % 60
        line = f"Time {mm:02d}:{ss:02d}"
        if map_name:
            line = f"{map_name}  |  " + line

        t_time = self.font_small.render(
            line, True, (200, 215, 235)
        )
        screen.blit(t_time, (130, 52))

        # ===== BUFF ICONS (RIGHT SIDE) =====
        bx = panel.right - 26
        by = panel.y + 22
        icon_size = 24

        def draw_buff(img, seconds, color):
            nonlocal bx
            _draw_icon(screen, img, bx, by, icon_size)
            if seconds > 0:
                txt = self.font_small.render(
                    f"{seconds:.0f}s", True, color
                )
                screen.blit(
                    txt,
                    txt.get_rect(midtop=(bx, by + icon_size // 2)),
                )
            bx -= 56

        if player:
            # x2
            x2_time = float(getattr(player, "x2_time", 0.0))
            if x2_time > 0:
                draw_buff(
                    self.ico_x2, x2_time, (255, 235, 170)
                )

            # shield
            inv = float(getattr(player, "invincible_time", 0.0))
            tier = int(getattr(player, "shield_tier", 0))
            if inv > 0:
                ico = self.ico_sh1
                if tier == 2:
                    ico = self.ico_sh2
                elif tier == 3:
                    ico = self.ico_sh3
                draw_buff(
                    ico, inv, (120, 200, 255)
                )
