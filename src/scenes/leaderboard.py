import pygame
from src.core.scene import Scene
from src.ui.button import Button


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


class LeaderboardScene(Scene):
    def on_enter(self, **kwargs):
        self.bg = self.app.assets.image("assets/bg/khungchoi_bg.jpg")
        self.h1 = self.app.assets.font(None, 54)
        self.font = self.app.assets.font(None, 26)
        self.small = self.app.assets.font(None, 18)
        theme = self.app.theme

        self.btn_back = Button(
            (30, 20, 140, 44),
            "BACK",
            self._go_menu,
            self.small,
            theme
        )

        hs = self.app.save.data.get("highscores", {"1": 0, "2": 0, "3": 0})
        self.rows = [
            ("Map 1", int(hs.get("1", 0))),
            ("Map 2", int(hs.get("2", 0))),
            ("Map 3", int(hs.get("3", 0))),
        ]

    def _go_menu(self):
        from src.scenes.menu import MenuScene
        self.app.scenes.set_scene(MenuScene(self.app))

    def handle_event(self, event):
        self.btn_back.handle_event(event)

    def draw(self, screen):
        draw_cover(screen, self.bg, self.app.width, self.app.height)

        overlay = pygame.Surface(
            (self.app.width, self.app.height),
            pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 105))
        screen.blit(overlay, (0, 0))

        title = self.h1.render(
            "LEADERBOARD",
            True,
            self.app.theme["text"]
        )
        screen.blit(title, (70, 70))

        panel = pygame.Rect(
            70,
            170,
            self.app.width - 140,
            430
        )
        pygame.draw.rect(screen, (10, 20, 35), panel, border_radius=18)
        pygame.draw.rect(screen, (120, 200, 255), panel, 2, border_radius=18)

        y = panel.y + 30
        for name, score in self.rows:
            line = self.font.render(name, True, (235, 245, 255))
            val = self.font.render(str(score), True, (255, 235, 170))
            screen.blit(line, (panel.x + 30, y))
            screen.blit(val, val.get_rect(topright=(panel.right - 30, y)))
            y += 70

        hint = self.small.render(
            "Highscore saved per map in save.json",
            True,
            self.app.theme["muted"]
        )
        screen.blit(hint, (70, 620))

        self.btn_back.draw(screen)
