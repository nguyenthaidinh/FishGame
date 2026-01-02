import pygame

from src.core.scene import Scene
from src.ui.panel import Panel
from src.ui.image_button import ImageButton


class PauseScene(Scene):
    def __init__(self, app, game_scene):
        super().__init__(app)
        self.game_scene = game_scene

    def on_enter(self, **kwargs):
        # ==================================================
        # 🔊 CLICK SOUND
        # ==================================================
        self.click_sound = self.app.assets.sound(
            "assets/sound/click.wav"
        )

        cx = self.app.width // 2

        # ==================================================
        # 📦 PANEL
        # ==================================================
        

        # ==================================================
        # 📐 LAYOUT
        # ==================================================
        y0 = 220
        gap = 90

        # ==================================================
        # 🟦 IMAGE BUTTONS
        # ==================================================
        self.buttons = [
            ImageButton(
                "assets/ui/button/retry.png",
                (cx, y0),
                self._resume,
                scale=0.22,
                scale_x=2.0,
                hover_scale=1.15,
                click_sound=self.click_sound
            ),
            ImageButton(
                "assets/ui/button/resume.png",
                (cx, y0 + gap),
                self._retry,
                scale=0.2,
                scale_x=2.0,
                hover_scale=1.15,
                click_sound=self.click_sound
            ),
            ImageButton(
                "assets/ui/button/map_select.png",
                (cx, y0 + gap * 2),
                self._go_map_select,
                scale=0.2,
                scale_x=2.0,
                hover_scale=1.15,
                click_sound=self.click_sound
            ),
            ImageButton(
                "assets/ui/button/menu.png",
                (cx, y0 + gap * 3),
                self._go_menu,
                scale=0.2,
                scale_x=2.0,
                hover_scale=1.15,
                click_sound=self.click_sound
            ),
        ]

    # =========================
    # Actions
    # =========================
    def _resume(self):
        self.app.scenes.replace_scene(self.game_scene)

    def _retry(self):
        from src.scenes.game_scene import GameScene

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
        pygame.mixer.music.fadeout(600)
        from src.scenes.menu import MenuScene
        self.app.scenes.set_scene(MenuScene(self.app))

    def _go_map_select(self):
        from src.scenes.map_select import MapSelectScene
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
        # freeze gameplay
        self.game_scene.draw(screen)

        # overlay tối
        overlay = pygame.Surface(
            (self.app.width, self.app.height),
            pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 140))
        screen.blit(overlay, (0, 0))

        

        # buttons
        for b in self.buttons:
            b.draw(screen)
