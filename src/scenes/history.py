import pygame
from src.core.scene import Scene
from src.ui.button import Button
from src.scenes.menu import MenuScene

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

class HistoryScene(Scene):
    def on_enter(self, **kwargs):
        self.bg = self.app.assets.image("assets/bg/khungchoi_bg.jpg")
        self.h1 = self.app.assets.font(None, 54)
        self.font = self.app.assets.font(None, 22)
        self.small = self.app.assets.font(None, 18)

        theme = self.app.theme
        self.btn_back = Button((30, 20, 140, 44), "BACK", lambda: self.app.scenes.set_scene(MenuScene(self.app)), self.small, theme)

        self.history = self.app.save.data.get("history", [])
        self.scroll = 0

    def handle_event(self, event):
        self.btn_back.handle_event(event)
        if event.type == pygame.MOUSEWHEEL:
            self.scroll -= event.y * 40
            self.scroll = max(0, self.scroll)

    def draw(self, screen):
        draw_cover(screen, self.bg, self.app.w, self.app.h)
        overlay = pygame.Surface((self.app.w, self.app.h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 105))
        screen.blit(overlay, (0, 0))

        title = self.h1.render("HISTORY", True, self.app.theme["text"])
        screen.blit(title, (70, 70))

        panel = pygame.Rect(70, 170, self.app.w - 140, 470)
        pygame.draw.rect(screen, (10, 20, 35), panel, border_radius=18)
        pygame.draw.rect(screen, (120, 200, 255), panel, 2, border_radius=18)

        y = panel.y + 16 - self.scroll
        for item in self.history:
            time_s = str(item.get("time", ""))
            mode = int(item.get("mode", 1))
            map_id = int(item.get("map_id", 1))
            pts = int(item.get("points", 0))
            t_alive = float(item.get("time_alive", 0.0))
            res = str(item.get("result", ""))

            line = f"[{time_s}]  Map {map_id}  |  Mode {mode}  |  {res}  |  {pts} pts  |  {t_alive:.1f}s"
            txt = self.font.render(line, True, (235, 245, 255))
            if y + txt.get_height() > panel.y and y < panel.bottom:
                screen.blit(txt, (panel.x + 18, y))
            y += 34

        hint = self.small.render("Scroll mouse wheel to view more.", True, self.app.theme["muted"])
        screen.blit(hint, (70, 650))

        self.btn_back.draw(screen)
