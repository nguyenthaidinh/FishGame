import pygame
from src.core.scene import Scene
from src.ui.bg import draw_cover

class BootScene(Scene):
    def on_enter(self, **kwargs):
        self.t = 0.0
        self.done = False  # ✅ thêm flag
        self.bg = self.app.assets.image("assets/bg/khungchoi_bg.jpg")

    def update(self, dt):
        if self.done:
            return

        self.t += dt
        if self.t > 0.6:
            self.done = True  # ✅ đảm bảo chỉ gọi 1 lần
            from src.scenes.menu import MenuScene  # lazy import
            self.app.scenes.set_scene(MenuScene(self.app))

    def draw(self, screen):
        draw_cover(screen, self.bg, self.app.w, self.app.h, alpha=235)

        overlay = pygame.Surface((self.app.w, self.app.h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 70))
        screen.blit(overlay, (0, 0))

        font = self.app.assets.font(None, 44)
        txt = font.render("Loading...", True, (230, 240, 255))
        screen.blit(txt, txt.get_rect(center=(self.app.w//2, self.app.h//2)))
