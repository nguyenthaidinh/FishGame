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


class GameOverScene(Scene):
    def on_enter(self, map_id=1, points=0, time_alive=0.0, **kwargs):
        self.bg = self.app.assets.image("assets/bg/khungchoi_bg.jpg")
        self.title_font = self.app.assets.font(None, 68)
        self.font = self.app.assets.font(None, 26)

        self.map_id = int(map_id)
        self.points = int(points)
        self.time_alive = float(time_alive)

        # save history (LOSE) + update highscore
        mode = int(self.app.runtime.get("mode", 1))
        self.app.save.update_highscore(self.map_id, self.points)
        self.app.save.add_history(
            mode=mode,
            map_id=self.map_id,
            points=self.points,
            time_alive=self.time_alive,
            result="LOSE",
        )
        self.app.save.save()

        cx = self.app.width // 2
        theme = self.app.theme
        self.btn_font = self.app.assets.font(None, 28)

        self.buttons = [
            Button(
                rect=(cx - 210, 430, 420, 62),
                text="RETRY",
                on_click=self._retry,
                font=self.btn_font,
                theme=theme,
            ),
            Button(
                rect=(cx - 210, 505, 420, 62),
                text="MAP SELECT",
                on_click=self._go_map_select,
                font=self.btn_font,
                theme=theme,
            ),
            Button(
                rect=(cx - 210, 580, 420, 62),
                text="MAIN MENU",
                on_click=self._go_menu,
                font=self.btn_font,
                theme=theme,
            ),
        ]

    # ======================
    # Actions (LAZY IMPORT)
    # ======================
    def _retry(self):
        from src.scenes.game_scene import GameScene  # ✅ lazy import

        map_data = self.app.runtime.get("map")
        if not map_data:
            map_data = {
                "id": self.map_id,
                "name": f"Map {self.map_id}",
                "bg": None,
                "world_size": [3200, 1800],
            }
            self.app.runtime["map"] = map_data

        self.app.scenes.set_scene(GameScene(self.app), map_data=map_data)

    def _go_menu(self):
        from src.scenes.menu import MenuScene  # ✅ lazy import
        self.app.scenes.set_scene(MenuScene(self.app))

    def _go_map_select(self):
        from src.scenes.map_select import MapSelectScene  # ✅ lazy import
        self.app.scenes.set_scene(MapSelectScene(self.app))

    # ======================
    # Events / Draw
    # ======================
    def handle_event(self, event):
        for b in self.buttons:
            b.handle_event(event)

    def draw(self, screen):
        draw_cover(screen, self.bg, self.app.width, self.app.height)

        overlay = pygame.Surface((self.app.width, self.app.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

        title = self.title_font.render("GAME OVER", True, (255, 140, 140))
        screen.blit(title, title.get_rect(center=(self.app.width // 2, 170)))

        info1 = self.font.render(f"Map: {self.map_id}", True, (235, 245, 255))
        info2 = self.font.render(f"Points: {self.points}", True, (235, 245, 255))
        info3 = self.font.render(f"Time alive: {self.time_alive:.1f}s", True, (235, 245, 255))

        screen.blit(info1, info1.get_rect(center=(self.app.width // 2, 260)))
        screen.blit(info2, info2.get_rect(center=(self.app.width // 2, 295)))
        screen.blit(info3, info3.get_rect(center=(self.app.width // 2, 330)))

        for b in self.buttons:
            b.draw(screen)
