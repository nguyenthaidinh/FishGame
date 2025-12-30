import pygame

from src.core.scene import Scene
from src.ui.button import Button
from src.ui.panel import Panel


class PauseScene(Scene):
    def __init__(self, app, game_scene):
        super().__init__(app)
        self.game_scene = game_scene

    def on_enter(self, **kwargs):
        # fonts
        self.h1 = self.app.assets.font(None, 54)
        self.btn_font = self.app.assets.font(None, 28)
        self.small = self.app.assets.font(None, 18)

        cx = self.app.w // 2
        theme = self.app.theme

        # Panel trung tâm
        self.panel = Panel(
            rect=(cx - 260, 260, 520, 360),
            bg_color=(25, 30, 45),
            alpha=210,
            radius=18
        )

        self.buttons = [
            Button(
                (cx - 210, 320, 420, 62),
                "RESUME",
                self._resume,
                self.btn_font,
                theme
            ),
            Button(
                (cx - 210, 395, 420, 62),
                "RETRY",
                self._retry,
                self.btn_font,
                theme
            ),
            Button(
                (cx - 210, 470, 420, 62),
                "MAP SELECT",
                self._go_map_select,
                self.btn_font,
                theme
            ),
            Button(
                (cx - 210, 545, 420, 62),
                "MAIN MENU",
                self._go_menu,
                self.btn_font,
                theme
            ),
        ]

        for b in self.buttons:
            self.panel.add(b)

    # =========================
    # Actions (LAZY IMPORT)
    # =========================
    def _resume(self):
        self.app.scenes.replace_scene(self.game_scene)

    def _retry(self):
        from src.scenes.game_scene import GameScene  # ✅ import muộn

        map_data = self.app.runtime.get("map")
        if not map_data:
            map_data = {
                "id": 1,
                "name": "Map 1",
                "bg": None,
                "world_size": [3200, 1800],
            }
            self.app.runtime["map"] = map_data

        self.app.scenes.set_scene(
            GameScene(self.app),
            map_data=map_data
        )

    def _go_menu(self):
        from src.scenes.menu import MenuScene  # ✅ import muộn
        self.app.scenes.set_scene(MenuScene(self.app))

    def _go_map_select(self):
        from src.scenes.map_select import MapSelectScene  # ✅ import muộn
        self.app.scenes.set_scene(MapSelectScene(self.app))

    # =========================
    # Events
    # =========================
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._resume()
            return

        for b in self.buttons:
            b.handle_event(event)

    # =========================
    # Draw
    # =========================
    def draw(self, screen):
        # gameplay phía sau (freeze frame)
        self.game_scene.draw(screen)

        overlay = pygame.Surface((self.app.w, self.app.h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        screen.blit(overlay, (0, 0))

        self.panel.draw(screen)

        title = self.h1.render("PAUSED", True, self.app.theme["text"])
        screen.blit(
            title,
            title.get_rect(center=(self.app.w // 2, 220))
        )

        hint = self.small.render(
            "ESC to resume",
            True,
            self.app.theme["muted"]
        )
        screen.blit(
            hint,
            hint.get_rect(center=(self.app.w // 2, 250))
        )
