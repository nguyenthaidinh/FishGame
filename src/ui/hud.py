# src/ui/hud.py
import pygame


# =========================================================
# Text helpers (outline)
# =========================================================
def render_outline(font, text, fill=(245, 250, 255), outline=(0, 0, 0)):
    base = font.render(text, True, fill)
    out = font.render(text, True, outline)
    return base, out


def blit_outline(screen, base, out, x, y, thick=2):
    for ox, oy in [
        (-thick, 0), (thick, 0), (0, -thick), (0, thick),
        (-thick, -thick), (thick, -thick), (-thick, thick), (thick, thick)
    ]:
        screen.blit(out, (x + ox, y + oy))
    screen.blit(base, (x, y))


# =========================================================
# Icon helpers
# =========================================================
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


# =========================================================
# HUD
# =========================================================
class HUD:
    """
    HUD (panel PNG + vẽ text/icon nằm TRONG panel):
    - Hàng trên: Score + Map/Time
    - Hàng dưới: Hearts + Buff slots
    - Không vẽ khung đen/đổ bóng ngoài (panel đã có viền đẹp)
    """

    def __init__(self, font_big, font_small):
        self.font_big = font_big
        self.font_small = font_small

        self._loaded = False

        # panel image
        self.panel_img = None
        self._panel_cache_size = None
        self._panel_cache_scaled = None

        # icons
        self.ico_heart_full = None
        self.ico_heart_empty = None
        self.ico_x2 = None
        self.ico_sh1 = None
        self.ico_sh2 = None
        self.ico_sh3 = None

        # optional: empty slot icon (nếu có)
        self.ico_slot = None

    def _safe_image(self, assets, path):
        try:
            return assets.image(path)
        except Exception:
            return None

    def _ensure_assets(self, assets):
        if self._loaded:
            return
        self._loaded = True

        self.panel_img = self._safe_image(assets, "assets/ui/hud/panel.png")

        self.ico_heart_full = self._safe_image(assets, "assets/ui/button/heart_full.png")
        self.ico_heart_empty = self._safe_image(assets, "assets/ui/button/heart_empty.png")

        self.ico_x2 = self._safe_image(assets, "assets/ui/items/x2diem.png")
        self.ico_sh1 = self._safe_image(assets, "assets/ui/items/thuong1.png")
        self.ico_sh2 = self._safe_image(assets, "assets/ui/items/thuong2.png")
        self.ico_sh3 = self._safe_image(assets, "assets/ui/items/thuong3.png")


    def _panel_scaled(self, w, h):
        """
        Cache panel scale để không smoothscale mỗi frame.
        """
        if self.panel_img is None:
            return None

        key = (int(w), int(h))
        if self._panel_cache_size == key and self._panel_cache_scaled is not None:
            return self._panel_cache_scaled

        self._panel_cache_size = key
        self._panel_cache_scaled = pygame.transform.smoothscale(self.panel_img, key)
        return self._panel_cache_scaled

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
        self._ensure_assets(assets)

        sw, sh = screen.get_width(), screen.get_height()

        # =========================================================
        # PANEL: nhỏ lại + ngắn lại (đẹp, gọn)
        # =========================================================
        panel_w = min(520, int(sw * 0.58))  # ✅ ngắn lại
        panel_h = 92                        # ✅ thấp lại
        panel_x = 18
        panel_y = 12
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

        # vẽ panel PNG
        panel_surf = self._panel_scaled(panel_w, panel_h)
        if panel_surf:
            screen.blit(panel_surf, panel_rect.topleft)
        else:
            # fallback nếu thiếu panel.png
            fallback = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            pygame.draw.rect(fallback, (10, 18, 30, 210), fallback.get_rect(), border_radius=20)
            pygame.draw.rect(fallback, (110, 210, 255, 140), fallback.get_rect(), width=2, border_radius=20)
            screen.blit(fallback, panel_rect.topleft)

        # =========================================================
        # LAYOUT "TRONG PANEL"
        # Dùng tỉ lệ theo panel để không bị lệch khi đổi size
        # =========================================================
        x0, y0, w0, h0 = panel_rect.x, panel_rect.y, panel_rect.w, panel_rect.h

        # vùng "ruột" (tránh góc trang trí)
        inner_l = x0 + int(w0 * 0.06)  # tránh icon cua bên trái
        inner_r = x0 + int(w0 * 0.94)  # tránh sò bên phải
        inner_w = inner_r - inner_l

        # hàng trên / dưới
        top_y = y0 + int(h0 * 0.18)
        bottom_y = y0 + int(h0 * 0.66)

        # =========================================================
        # TOP: SCORE + MAP/TIME
        # =========================================================
        score_text = f"{int(points)} / {int(target)}"
        score_base, score_out = render_outline(
            self.font_big,
            score_text,
            fill=(245, 252, 255),
            outline=(0, 0, 0),
        )

        # score nằm trong ruột panel
        score_x = inner_l + 40 
        score_y = top_y + 4 
        blit_outline(screen, score_base, score_out, score_x, score_y, thick=2)

        mm = int(elapsed) // 60
        ss = int(elapsed) % 60
        line = f"Time {mm:02d}:{ss:02d}"
        if map_name:
            line = f"{map_name} | {line}"

        # time nằm cùng hàng, bên phải score
        # canh sao cho vẫn nằm trong ruột panel
        time_base, time_out = render_outline(
            self.font_small,
            line,
            fill=(215, 232, 245),
            outline=(0, 0, 0),
        )
        time_x = inner_l + int(inner_w * 0.30)
        time_y = top_y + 4
        blit_outline(screen, time_base, time_out, time_x, time_y, thick=1)

        # =========================================================
        # BOTTOM: HEARTS (to hơn) + BUFF SLOTS
        # =========================================================
        max_lives = 3
        lives = int(lives)

        heart_size = 48      
        heart_gap = 36
        hearts_x = inner_l + int(inner_w * 0.02) + 180

        for i in range(max_lives):
            img = self.ico_heart_full if i < lives else self.ico_heart_empty
            draw_icon(
                screen,
                img,
                hearts_x + i * heart_gap,
                bottom_y,
                heart_size
            )

        # ===== Buff slots bên phải (2 ô) =====
        slot_size = 28
        slot_gap = 42
        slots_count = 2

        # slot area sát phải, vẫn nằm trong ruột panel
        slots_right = inner_r - int(inner_w * 0.02) - 50
        slot_centers = []
        for i in range(slots_count):
            cx = slots_right - i * slot_gap
            slot_centers.append(cx)

        # vẽ slot nền (nếu không có icon slot thì vẽ hình rounded)
        for cx in slot_centers:
            if self.ico_slot:
                draw_icon(screen, self.ico_slot, cx, bottom_y, slot_size, alpha=255)
            else:
                slot_rect = pygame.Rect(0, 0, slot_size, slot_size)
                slot_rect.center = (int(cx), int(bottom_y))
                # nền slot nhẹ, nhìn “game UI”
                s = pygame.Surface((slot_size, slot_size), pygame.SRCALPHA)
                pygame.draw.rect(s, (0, 0, 0, 70), s.get_rect(), border_radius=10)
                pygame.draw.rect(s, (255, 255, 255, 70), s.get_rect(), width=2, border_radius=10)
                screen.blit(s, slot_rect.topleft)

        # ===== đặt buff icons vào slot (ưu tiên x2 rồi shield) =====
        if player:
            buffs = []

            x2_time = float(getattr(player, "x2_time", 0.0))
            if x2_time > 0:
                buffs.append(("x2", self.ico_x2, x2_time))

            inv = float(getattr(player, "invincible_time", 0.0))
            tier = int(getattr(player, "shield_tier", 0))
            if inv > 0:
                ico = self.ico_sh1
                if tier == 2:
                    ico = self.ico_sh2
                elif tier == 3:
                    ico = self.ico_sh3
                buffs.append(("sh", ico, inv))

            # draw buffs vào slot (tối đa 2)
            for idx, (kind, img, secs) in enumerate(buffs[:slots_count]):
                cx = slot_centers[idx]
                draw_icon(screen, img, cx, bottom_y, slot_size - 4, alpha=255)

                # badge thời gian nhỏ phía dưới icon
                badge = f"{secs:.0f}s"
                b = self.font_small.render(badge, True, (255, 245, 190))
                o = self.font_small.render(badge, True, (0, 0, 0))
                bx = int(cx - b.get_width() / 2)
                by = int(bottom_y + slot_size * 0.38)
                screen.blit(o, (bx + 1, by + 1))
                screen.blit(b, (bx, by))
