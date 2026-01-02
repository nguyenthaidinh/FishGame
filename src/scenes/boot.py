import pygame
from src.core.scene import Scene
from src.ui.bg import draw_cover


class BootScene(Scene):
    def on_enter(self, **kwargs):
        self.t = 0.0
        self.done = False
        self.bg = self.app.assets.image("assets/bg/khungchoi_bg.jpg")

    def update(self, dt):
        if self.done:
            return

        self.t += dt
        if self.t > 0.6:
            self.done = True
            from src.scenes.menu import MenuScene  # lazy import
            self.app.scenes.set_scene(MenuScene(self.app))

    def draw(self, screen):
        # background cover
        draw_cover(
            screen,
            self.bg,
            self.app.width,
            self.app.height,
            alpha=235
        )

        # overlay
        overlay = pygame.Surface(
            (self.app.width, self.app.height),
            pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 70))
        screen.blit(overlay, (0, 0))

        # loading text
        font = self.app.assets.font(None, 44)
        txt = font.render("Loading...", True, (230, 240, 255))
        screen.blit(
            txt,
            txt.get_rect(
                center=(
                    self.app.width // 2,
                    self.app.height // 2
                )
            )
        )
