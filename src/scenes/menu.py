import pygame
from src.core.scene import Scene
from src.ui.button import Button


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


# =========================
# MENU SCENE
# =========================
class MenuScene(Scene):
    def on_enter(self, **kwargs):
        self.bg = self.app.assets.image("assets/bg/khungchoi_bg.jpg")

        self.title_font = self.app.assets.font(None, 64)
        self.sub_font = self.app.assets.font(None, 26)
        self.btn_font = self.app.assets.font(None, 30)

        cx = self.app.w // 2
        y0 = 320
        gap = 74
        theme = self.app.theme

        self.buttons = [
            Button(
                rect=(cx - 190, y0 + 0 * gap, 380, 64),
                text="CHƠI NGAY",
                on_click=self._go_mode,
                font=self.btn_font,
                theme=theme
            ),
            Button(
                rect=(cx - 190, y0 + 1 * gap, 380, 64),
                text="BẢNG XẾP HẠNG",
                on_click=self._go_leaderboard,
                font=self.btn_font,
                theme=theme
            ),
            Button(
                rect=(cx - 190, y0 + 2 * gap, 380, 64),
                text="LỊCH SỬ",
                on_click=self._go_history,
                font=self.btn_font,
                theme=theme
            ),
            Button(
                rect=(cx - 190, y0 + 3 * gap, 380, 64),
                text="CÀI ĐẶT",
                on_click=self._go_settings,
                font=self.btn_font,
                theme=theme
            ),
            Button(
                rect=(cx - 190, y0 + 4 * gap, 380, 64),
                text="THOÁT GAME",
                on_click=self.app.quit,
                font=self.btn_font,
                theme=theme
            ),
        ]

    # =========================
    # Navigation (LAZY IMPORT)
    # =========================
    def _go_mode(self):
        from src.scenes.mode_select import ModeSelectScene
        self.app.scenes.set_scene(ModeSelectScene(self.app))

    def _go_leaderboard(self):
        from src.scenes.leaderboard import LeaderboardScene
        self.app.scenes.set_scene(LeaderboardScene(self.app))

    def _go_history(self):
        from src.scenes.history import HistoryScene
        self.app.scenes.set_scene(HistoryScene(self.app))

    def _go_settings(self):
        from src.core.settings import SettingsScene
        self.app.scenes.set_scene(SettingsScene(self.app))

    # =========================
    # Events
    # =========================
    def handle_event(self, event):
        for b in self.buttons:
            b.handle_event(event)

    # =========================
    # Draw
    # =========================
    def draw(self, screen):
        draw_cover(screen, self.bg, self.app.w, self.app.h)

        overlay = pygame.Surface((self.app.w, self.app.h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 95))
        screen.blit(overlay, (0, 0))

        title = self.title_font.render("Blue Ocean", True, self.app.theme["text"])
        subtitle = self.sub_font.render(
            "Một đại dương, một quy luật.",
            True,
            self.app.theme["muted"]
        )

        screen.blit(title, title.get_rect(center=(self.app.w // 2, 160)))
        screen.blit(subtitle, subtitle.get_rect(center=(self.app.w // 2, 210)))

        for b in self.buttons:
            b.draw(screen)
