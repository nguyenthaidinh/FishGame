import pygame
from src.core.scene import Scene
from src.ui.image_button import ImageButton


# =========================
# Helpers
# =========================
def draw_cover(screen, image, w, h, alpha=255):
    if image is None:
        return
    iw, ih = image.get_width(), image.get_height()
    if iw <= 0 or ih <= 0:
        return
    scale = max(w / iw, h / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    surf = pygame.transform.smoothscale(image, (nw, nh))
    if alpha < 255:
        surf.set_alpha(alpha)
    x = (w - nw) // 2
    y = (h - nh) // 2
    screen.blit(surf, (x, y))


def clamp(val, minv, maxv):
    return max(minv, min(val, maxv))


# =========================
# HISTORY SCENE
# =========================
class HistoryScene(Scene):
    def on_enter(self, **kwargs):
        # ===== BACKGROUND =====
        self.bg = self.app.assets.image("assets/bg/khungchoi_bg.jpg")

        # ===== FONTS =====
        self.h1 = self.app.assets.font("assets/fonts/Baloo2-Bold.ttf", 56)
        self.font = self.app.assets.font("assets/fonts/Baloo2-Bold.ttf", 24)
        self.small = self.app.assets.font("assets/fonts/Baloo2-Bold.ttf", 18)

        # ===== BACK BUTTON (IMAGE) =====
        self.btn_back = ImageButton(
            "assets/ui/button/back.png",
            (70, 70),
            self._go_menu,
            scale=0.18,
            hover_scale=1.1
        )

        # ===== HISTORY DATA =====
        # ✅ SaveManager thường insert(0) => mới nhất đã ở đầu list
        self.history = self.app.save.data.get("history", [])

        # ===== PANEL =====
        self.panel = pygame.Rect(
            70, 170,
            self.app.width - 140,
            470
        )

        # ===== TABLE CONFIG =====
        self.row_h = 34
        self.header_h = 44
        self.scroll = 0

        # CỘT CỐ ĐỊNH (KHÔNG BAO GIỜ ĐÈ)
        self.col_x = {
            "time": 20,
            "map": 140,
            "mode": 230,
            "result": 310,
            "points": 410,
            "alive": 520
        }

    # =========================
    # Navigation
    # =========================
    def _go_menu(self):
        from src.scenes.menu import MenuScene
        self.app.scenes.set_scene(MenuScene(self.app))

    # =========================
    # Events
    # =========================
    def handle_event(self, event):
        self.btn_back.handle_event(event)

        if event.type == pygame.MOUSEWHEEL:
            max_scroll = max(
                0,
                len(self.history) * self.row_h
                - (self.panel.height - self.header_h)
            )
            self.scroll -= event.y * 30
            self.scroll = clamp(self.scroll, 0, max_scroll)

    # =========================
    # Draw
    # =========================
    def draw(self, screen):
        draw_cover(screen, self.bg, self.app.width, self.app.height)

        # overlay
        overlay = pygame.Surface((self.app.width, self.app.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 110))
        screen.blit(overlay, (0, 0))

        # ===== TITLE =====
        title = self.h1.render("History", True, self.app.theme["text"])
        screen.blit(title, (140, 60))

        # ===== PANEL =====
        pygame.draw.rect(screen, (10, 20, 35), self.panel, border_radius=20)
        pygame.draw.rect(screen, (120, 200, 255), self.panel, 2, border_radius=20)

        # ===== HEADER =====
        headers = [
            ("Time", "time"),
            ("Map", "map"),
            ("Mode", "mode"),
            ("Result", "result"),
            ("Points", "points"),
            ("Alive", "alive"),
        ]

        for text, key in headers:
            t = self.small.render(text, True, (190, 210, 235))
            screen.blit(t, (self.panel.x + self.col_x[key], self.panel.y + 12))

        pygame.draw.line(
            screen,
            (90, 150, 210),
            (self.panel.x + 10, self.panel.y + self.header_h),
            (self.panel.right - 10, self.panel.y + self.header_h),
            1
        )

        # ===== EMPTY STATE =====
        if not self.history:
            msg = self.font.render("No history yet.", True, (235, 245, 255))
            screen.blit(msg, msg.get_rect(center=self.panel.center))

            hint = self.small.render(
                "Play a match to create history",
                True,
                self.app.theme["muted"]
            )
            screen.blit(hint, (70, 660))

            self.btn_back.draw(screen)
            return

        # ===== CLIP SCROLL =====
        clip_rect = pygame.Rect(
            self.panel.x,
            self.panel.y + self.header_h,
            self.panel.width,
            self.panel.height - self.header_h
        )
        screen.set_clip(clip_rect)

        # ===== ROWS =====
        y = self.panel.y + self.header_h - self.scroll

        for item in self.history:
            raw_time = str(item.get("time", ""))
            time_s = raw_time[-8:] if len(raw_time) >= 8 else raw_time

            values = {
                "time": time_s,
                "map": f"Map {item.get('map_id', 1)}",
                "mode": f"{item.get('mode', 1)}P",
                "result": item.get("result", ""),
                "points": str(item.get("points", 0)),
                "alive": f"{item.get('time_alive', 0):.1f}s",
            }

            if y + self.row_h > clip_rect.top and y < clip_rect.bottom:
                for key, value in values.items():
                    if value == "LOSE":
                        color = (255, 120, 120)
                    elif value == "WIN":
                        color = (120, 255, 160)
                    else:
                        color = (235, 245, 255)

                    txt = self.font.render(value, True, color)
                    screen.blit(txt, (self.panel.x + self.col_x[key], y))

            y += self.row_h

        screen.set_clip(None)

        # ===== HINT =====
        hint = self.small.render(
            "Use mouse wheel to scroll history",
            True,
            self.app.theme["muted"]
        )
        screen.blit(hint, (70, 660))

        # ===== BACK BUTTON =====
        self.btn_back.draw(screen)
