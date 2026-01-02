import pygame
from src.core.scene import Scene
from src.ui.image_button import ImageButton
from src.scenes.map_select import MapSelectScene


class ModeSelectScene(Scene):
    def on_enter(self, **kwargs):
        # ===== FONT (CHỈ DÙNG CHO TITLE) =====
        self.h1 = self.app.assets.font(None, 46)

        # ===== LAYOUT =====
        cx = self.app.width // 2
        y0 = int(self.app.height * 0.40)
        gap = 100

        # ===== IMAGE BUTTONS =====
        self.buttons = [
            # 1 PLAYER
            ImageButton(
                "assets/ui/button/1_player.png",
                (cx, y0),
                lambda: self._pick(1),
                scale=0.22,
                hover_scale=1.15
            ),

            # 2 PLAYERS
            ImageButton(
                "assets/ui/button/2_player.png",
                (cx, y0 + gap),
                lambda: self._pick(2),
                scale=0.22,
                hover_scale=1.15
            ),

            # BACK
            ImageButton(
                "assets/ui/button/back.png",
                (cx, y0 + gap * 2),
                self.app.back,
                scale=0.18,
                hover_scale=1.12
            ),
        ]

    # =========================
    # LOGIC
    # =========================
    def _pick(self, mode: int):
        self.app.runtime["mode"] = mode
        self.app.scenes.set_scene(MapSelectScene(self.app))

    # =========================
    # EVENTS
    # =========================
    def handle_event(self, event):
        for b in self.buttons:
            b.handle_event(event)

    def update(self, dt):
        pass

    # =========================
    # DRAW
    # =========================
    def draw(self, screen):
        # nền xanh đậm (đồng bộ menu)
        screen.fill((6, 22, 44))

        # title
        t = self.h1.render(
            "Select Mode",
            True,
            self.app.theme["text"]
        )
        screen.blit(
            t,
            t.get_rect(center=(self.app.width // 2, 220))
        )

        # buttons
        for b in self.buttons:
            b.draw(screen)
