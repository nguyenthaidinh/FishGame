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
    scale = max(w / iw, h / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    surf = pygame.transform.smoothscale(image, (nw, nh))
    if alpha < 255:
        surf.set_alpha(alpha)
    x = (w - nw) // 2
    y = (h - nh) // 2
    screen.blit(surf, (x, y))


# =========================
# LEADERBOARD SCENE
# =========================
class LeaderboardScene(Scene):
    def on_enter(self, **kwargs):
        # ===== BACKGROUND =====
        self.bg = self.app.assets.image("assets/bg/khungchoi_bg.jpg")

        # ===== FONTS =====
        self.h1 = self.app.assets.font(
            "assets/fonts/Baloo2-Bold.ttf", 56
        )
        self.font = self.app.assets.font(
            "assets/fonts/Baloo2-Bold.ttf", 26
        )
        self.small = self.app.assets.font(
            "assets/fonts/Baloo2-Bold.ttf", 18
        )

        # ===== BACK BUTTON (IMAGE) =====
        self.btn_back = ImageButton(
            "assets/ui/button/back.png",
            (90, 55),                       # vị trí góc trái trên
            self._go_menu,
            scale=0.15,
            hover_scale=1.1
        )

        # ===== DATA =====
        hs = self.app.save.data.get(
            "highscores", {"1": 0, "2": 0, "3": 0}
        )

        self.rows = [
            ("Map 1", int(hs.get("1", 0))),
            ("Map 2", int(hs.get("2", 0))),
            ("Map 3", int(hs.get("3", 0))),
        ]

        # sắp xếp theo điểm giảm dần
        self.rows.sort(key=lambda x: x[1], reverse=True)

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

    # =========================
    # Draw
    # =========================
    def draw(self, screen):
        draw_cover(screen, self.bg, self.app.width, self.app.height)

        # overlay tối
        overlay = pygame.Surface(
            (self.app.width, self.app.height), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 110))
        screen.blit(overlay, (0, 0))

        # ===== TITLE =====
        title = self.h1.render(
            "Leaderboard", True, self.app.theme["text"]
        )
        screen.blit(title, (170, 60))

        # ===== PANEL =====
        panel = pygame.Rect(
            70, 150,
            self.app.width - 140,
            430
        )
        pygame.draw.rect(
            screen, (12, 24, 40), panel, border_radius=20
        )
        pygame.draw.rect(
            screen, (120, 200, 255), panel, 2, border_radius=20
        )

        # ===== HEADER =====
        headers = ["Rank", "Map", "High Score"]
        col_x = [40, 140, panel.width - 220]

        for i, h in enumerate(headers):
            txt = self.small.render(h, True, (190, 210, 235))
            screen.blit(
                txt,
                (panel.x + col_x[i], panel.y + 16)
            )

        pygame.draw.line(
            screen,
            (90, 150, 210),
            (panel.x + 20, panel.y + 46),
            (panel.right - 20, panel.y + 46),
            1
        )

        # ===== ROWS =====
        y = panel.y + 70
        for idx, (name, score) in enumerate(self.rows, start=1):
            rank = self.font.render(
                f"#{idx}", True, (255, 220, 120)
            )
            map_name = self.font.render(
                name, True, (235, 245, 255)
            )
            val = self.font.render(
                str(score), True, (255, 235, 170)
            )

            screen.blit(rank, (panel.x + col_x[0], y))
            screen.blit(map_name, (panel.x + col_x[1], y))
            screen.blit(
                val,
                val.get_rect(
                    midright=(panel.right - 40, y + 14)
                )
            )

            y += 72

        # ===== HINT =====
        hint = self.small.render(
            "High score is saved separately for each map",
            True,
            self.app.theme["muted"]
        )
        screen.blit(hint, (70, 620))

        # ===== BACK =====
        self.btn_back.draw(screen)
