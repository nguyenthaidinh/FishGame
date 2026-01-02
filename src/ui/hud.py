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
    - Progress bar
    - Hearts
    - Time, Map
    - Buff icons
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

        # ===== PROGRESS BAR CONFIG =====
        self.bar_w = 200
        self.bar_h = 10
        self.bar_bg = (55, 70, 95)
        self.bar_fg = (190, 80, 220)
        self.bar_border = (140, 160, 190)

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
    # Draw progress bar
    # =========================
    def _draw_progress(
        self, screen, x, y, points, target
    ):
        # nền
        pygame.draw.rect(
            screen,
            self.bar_bg,
            (x, y, self.bar_w, self.bar_h),
            border_radius=6,
        )

        # viền
        pygame.draw.rect(
            screen,
            self.bar_border,
            (x, y, self.bar_w, self.bar_h),
            1,
            border_radius=6,
        )

        # tiến trình
        ratio = points / max(1, target)
        fill_w = int(self.bar_w * max(0.0, min(ratio, 1.0)))
        if fill_w > 0:
            pygame.draw.rect(
                screen,
                self.bar_fg,
                (x, y, fill_w, self.bar_h),
                border_radius=6,
            )

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

        # ===== HUD PANEL =====
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

        # ===== POINTS TEXT =====
        t_points = self.font_big.render(
            f"{points} / {target}",
            True,
            (240, 245, 255),
        )
        screen.blit(t_points, (130, 16))

        # ===== PROGRESS BAR (ĐÂY LÀ PHẦN BẠN CẦN) =====
        self._draw_progress(
            screen,
            x=130,
            y=42,
            points=points,
            target=target,
        )

        # ===== TIME + MAP =====
        mm = int(elapsed) // 60
        ss = int(elapsed) % 60
        line = f"Time {mm:02d}:{ss:02d}"
        if map_name:
            line = f"{map_name}  |  " + line

        t_time = self.font_small.render(
            line, True, (200, 215, 235)
        )
        screen.blit(t_time, (130, 56))

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
