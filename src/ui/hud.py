import pygame


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


class HUD:
    """
    draw(..., player=playerFish, map_id=..., ...)
    - heart icon: assets/items/thuong.png
    - x2 icon: assets/items/x2diem.png
    - shield icons: assets/items/thuong1.png / thuong2.png / thuong3.png
    """
    def __init__(self, font_big, font_small):
        self.font_big = font_big
        self.font_small = font_small

        # cache icon surfaces after first draw
        self._loaded = False
        self._ico_heart = None
        self._ico_x2 = None
        self._ico_sh1 = None
        self._ico_sh2 = None
        self._ico_sh3 = None

    def _ensure_icons(self, assets):
        if self._loaded:
            return
        self._loaded = True
        self._ico_heart = assets.image("assets/items/thuong.png")
        self._ico_x2 = assets.image("assets/items/x2diem.png")
        self._ico_sh1 = assets.image("assets/items/thuong1.png")
        self._ico_sh2 = assets.image("assets/items/thuong2.png")
        self._ico_sh3 = assets.image("assets/items/thuong3.png")

    def draw(self, screen, assets, lives: int, points: int, elapsed: float, target: int, player=None, map_name: str = ""):
        self._ensure_icons(assets)

        # panel
        panel = pygame.Rect(12, 10, 420, 76)
        pygame.draw.rect(screen, (10, 20, 35), panel, border_radius=16)
        pygame.draw.rect(screen, (110, 190, 255), panel, 2, border_radius=16)

        # hearts (icon)
        # tim tối đa = 3 (như code Lio)
        base_x = 40
        base_y = 40
        gap = 34
        size = 26
        for i in range(3):
            cx = base_x + i * gap
            # còn tim -> full alpha, mất tim -> dim
            if i < lives:
                _draw_icon(screen, self._ico_heart, cx, base_y, size, alpha=255)
            else:
                _draw_icon(screen, self._ico_heart, cx, base_y, size, alpha=70)
                # phủ vòng tròn tối cho rõ “mất”
                pygame.draw.circle(screen, (10, 20, 35), (cx, base_y), 12)

        # points
        t_points = self.font_big.render(f"{points} pts", True, (240, 245, 255))
        screen.blit(t_points, (130, 18))

        # time + target
        mm = int(elapsed) // 60
        ss = int(elapsed) % 60
        line2 = f"Time: {mm:02d}:{ss:02d}   Target: {target}"
        if map_name:
            line2 = f"{map_name}   " + line2
        t_time = self.font_small.render(line2, True, (200, 215, 235))
        screen.blit(t_time, (130, 52))

        # buff icons (right side inside panel)
        # show: x2 + shield + invincible (nếu Lio dùng invincible_time)
        bx = panel.right - 20
        by = panel.y + 20
        icon_size = 24
        pad = 8

        def draw_buff(img, seconds, label_color=(240, 245, 255)):
            nonlocal bx, by
            _draw_icon(screen, img, bx, by, icon_size, alpha=255)
            # timer nhỏ
            if seconds is not None and seconds > 0:
                tt = self.font_small.render(f"{seconds:0.0f}s", True, label_color)
                screen.blit(tt, tt.get_rect(midtop=(bx, by + icon_size//2 - 2)))
            bx -= (icon_size + 46)  # chừa chỗ timer

        if player is not None:
            # x2
            x2_time = float(getattr(player, "x2_time", 0.0))
            if x2_time > 0:
                draw_buff(self._ico_x2, x2_time, label_color=(255, 235, 170))

            # shield tier
            shield_tier = int(getattr(player, "shield_tier", 0))
            inv_time = float(getattr(player, "invincible_time", 0.0))
            if inv_time > 0:
                ico = self._ico_sh2
                if shield_tier == 1:
                    ico = self._ico_sh1
                elif shield_tier == 2:
                    ico = self._ico_sh2
                elif shield_tier == 3:
                    ico = self._ico_sh3
                draw_buff(ico, inv_time, label_color=(120, 200, 255))
