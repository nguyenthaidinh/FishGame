# src/ui/hud.py
import pygame

# =========================
# Helpers: text outline
# =========================
def render_outline(font, text, fill=(245, 250, 255), outline=(0, 0, 0)):
    base = font.render(text, True, fill)
    out = font.render(text, True, outline)
    return base, out

def blit_outline(screen, base, out, x, y, thick=2):
    for ox, oy in [(-thick,0),(thick,0),(0,-thick),(0,thick),(-thick,-thick),(thick,-thick),(-thick,thick),(thick,thick)]:
        screen.blit(out, (x+ox, y+oy))
    screen.blit(base, (x, y))

# =========================
# Helpers: icons
# =========================
def scale_icon(img: pygame.Surface, size: int) -> pygame.Surface:
    if img is None:
        return None
    w, h = img.get_width(), img.get_height()
    if w <= 0 or h <= 0:
        return img
    s = float(size) / float(max(w, h))
    return pygame.transform.smoothscale(img, (int(w * s), int(h * s)))

def draw_icon(screen, img, cx, cy, size, alpha=255):
    if img is None:
        return
    icon = scale_icon(img, int(size))
    if icon is None:
        return
    if alpha < 255:
        icon = icon.copy()
        icon.set_alpha(alpha)
    screen.blit(icon, icon.get_rect(center=(int(cx), int(cy))))

# =========================
# Helpers: fancy panel + bar
# =========================
def draw_panel(screen, rect: pygame.Rect):
    # shadow
    shadow = pygame.Surface((rect.w + 18, rect.h + 18), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0, 0, 0, 95), shadow.get_rect(), border_radius=26)
    screen.blit(shadow, (rect.x - 9, rect.y + 9))

    # base panel
    panel = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(panel, (10, 18, 30, 205), panel.get_rect(), border_radius=24)

    # top highlight (glass)
    hi = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(hi, (255, 255, 255, 26), pygame.Rect(0, 0, rect.w, int(rect.h * 0.45)), border_radius=24)
    panel.blit(hi, (0, 0))

    # border
    pygame.draw.rect(panel, (110, 210, 255, 120), panel.get_rect(), width=2, border_radius=24)

    screen.blit(panel, rect.topleft)

def draw_progress_bar(screen, rect: pygame.Rect, ratio: float):
    ratio = 0.0 if ratio < 0 else 1.0 if ratio > 1 else ratio
    r = rect.h // 2

    # bg
    pygame.draw.rect(screen, (6, 10, 16), rect, border_radius=r)
    pygame.draw.rect(screen, (255, 255, 255), rect, width=2, border_radius=r)

    # fill
    fill_w = max(0, int(rect.w * ratio))
    if fill_w > 0:
        fill = pygame.Rect(rect.x, rect.y, fill_w, rect.h)
        pygame.draw.rect(screen, (70, 220, 255), fill, border_radius=r)

        # shine line
        shine = pygame.Surface((fill_w, rect.h), pygame.SRCALPHA)
        pygame.draw.rect(shine, (255, 255, 255, 55), pygame.Rect(0, 0, fill_w, rect.h // 2), border_radius=r)
        screen.blit(shine, (rect.x, rect.y))

def draw_divider(screen, x, y, h):
    # đường chia mảnh + mờ
    pygame.draw.line(screen, (255, 255, 255), (x, y), (x, y + h), 1)
    overlay = pygame.Surface((2, h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 110))
    screen.blit(overlay, (x - 1, y))

# =========================
# HUD
# =========================
class HUD:
    def __init__(self, font_big, font_small):
        self.font_big = font_big
        self.font_small = font_small
        self._loaded = False

        self.ico_heart_full = None
        self.ico_heart_empty = None
        self.ico_x2 = None
        self.ico_sh1 = None
        self.ico_sh2 = None
        self.ico_sh3 = None

    def _safe_image(self, assets, path):
        try:
            return assets.image(path)
        except Exception:
            return None

    def _ensure_assets(self, assets):
        if self._loaded:
            return
        self._loaded = True

        # ✅ Lio đang có icon ở đây (theo ảnh folder Lio gửi)
        self.ico_heart_full  = self._safe_image(assets, "assets/ui/button/heart_full.png")
        self.ico_heart_empty = self._safe_image(assets, "assets/ui/button/heart_empty.png")

        self.ico_x2 = self._safe_image(assets, "assets/ui/items/x2diem.png")
        self.ico_sh1 = self._safe_image(assets, "assets/ui/items/thuong1.png")
        self.ico_sh2 = self._safe_image(assets, "assets/ui/items/thuong2.png")
        self.ico_sh3 = self._safe_image(assets, "assets/ui/items/thuong3.png")

    def draw(self, screen, assets, lives, points, elapsed, target, player=None, map_name=""):
        self._ensure_assets(assets)

        sw, sh = screen.get_width(), screen.get_height()

        # ===== Panel size (co giãn theo màn hình) =====
        panel_w = min(760, int(sw * 0.62))
        panel_h = 112
        panel = pygame.Rect(18, 14, panel_w, panel_h)

        draw_panel(screen, panel)

        # ===== Layout columns =====
        pad = 18
        left_w = 170          # hearts + small labels
        right_w = 170         # buffs
        mid_w = panel.w - (pad*2 + left_w + right_w)

        left_x = panel.x + pad
        mid_x  = left_x + left_w
        right_x = mid_x + mid_w

        draw_divider(screen, mid_x - 10, panel.y + 18, panel.h - 36)
        draw_divider(screen, right_x - 10, panel.y + 18, panel.h - 36)

        # ===== Hearts (to hơn) =====
        max_lives = 3
        lives = int(lives)
        heart_size = 30
        hx = left_x + 18
        hy = panel.y + 34
        gap = 40
        for i in range(max_lives):
            img = self.ico_heart_full if i < lives else self.ico_heart_empty
            draw_icon(screen, img, hx + i * gap, hy, heart_size)

        # ===== Score text =====
        pts_str = f"{int(points)} / {int(target)}"
        base, out = render_outline(self.font_big, pts_str, (245, 252, 255), (0, 0, 0))
        blit_outline(screen, base, out, mid_x, panel.y + 16, thick=2)

        # ===== Progress bar (dày + đẹp) =====
        ratio = (float(points) / float(target)) if target else 0.0
        bar = pygame.Rect(mid_x, panel.y + 52, max(120, int(mid_w * 0.82)), 18)
        draw_progress_bar(screen, bar, ratio)

        # ===== Map + Time =====
        mm = int(elapsed) // 60
        ss = int(elapsed) % 60
        line = f"Time {mm:02d}:{ss:02d}"
        if map_name:
            line = f"{map_name}  |  {line}"

        txt = self.font_small.render(line, True, (205, 225, 242))
        shd = self.font_small.render(line, True, (0, 0, 0))
        screen.blit(shd, (mid_x + 1, panel.y + 78 + 1))
        screen.blit(txt, (mid_x, panel.y + 78))

        # ===== Buff area (right) =====
        if player:
            bx = right_x + right_w - 24
            by = panel.y + 34
            icon_size = 28
            step = 54

            def draw_buff(img, seconds, label_color=(255, 235, 170)):
                nonlocal bx
                if img is None:
                    bx -= step
                    return
                draw_icon(screen, img, bx, by, icon_size)
                # time badge
                if seconds > 0:
                    s = f"{seconds:.0f}s"
                    t = self.font_small.render(s, True, label_color)
                    o = self.font_small.render(s, True, (0, 0, 0))
                    rx = bx - t.get_width() // 2
                    ry = by + 18
                    screen.blit(o, (rx + 1, ry + 1))
                    screen.blit(t, (rx, ry))
                bx -= step

            x2_time = float(getattr(player, "x2_time", 0.0))
            if x2_time > 0:
                draw_buff(self.ico_x2, x2_time, (255, 235, 170))

            inv = float(getattr(player, "invincible_time", 0.0))
            tier = int(getattr(player, "shield_tier", 0))
            if inv > 0:
                ico = self.ico_sh1
                if tier == 2:
                    ico = self.ico_sh2
                elif tier == 3:
                    ico = self.ico_sh3
                draw_buff(ico, inv, (140, 210, 255))
