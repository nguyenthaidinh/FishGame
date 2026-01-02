import pygame
from src.core.scene import Scene
from src.ui.image_button import ImageButton
from src.scenes.map_select import MapSelectScene


class ModeSelectScene(Scene):
    def on_enter(self, **kwargs):
        # ===== FONT (CHỈ DÙNG CHO TITLE) =====
        self.h1 = self.app.assets.font(None, 46)

        # ===== CLICK SOUND =====
        self.click_sound = self.app.assets.sound(
            "assets/sound/click.wav"
        )

        # ===== LAYOUT =====
        cx = self.app.width // 2
        y0 = int(self.app.height * 0.40)
        gap = 100

        # ===== IMAGE BUTTONS =====
        self.buttons = [
            # ===== 1 PLAYER =====
            ImageButton(
                "assets/ui/button/1_player.png",
                (cx, y0),
                lambda: self._pick(1),
                scale=0.22,
                scale_x=1.5,        # ⭐ KÉO DÀI NGANG
                scale_y=1.0,
                hover_scale=1.15,
                click_sound=self.click_sound
            ),

            # ===== 2 PLAYERS =====
            ImageButton(
                "assets/ui/button/2_player.png",
                (cx, y0 + gap*1.5),
                lambda: self._pick(2),
                scale=0.22,
                scale_x=1.5,
                scale_y=1.0,
                hover_scale=1.15,
                click_sound=self.click_sound
            ),

            # ===== BACK =====
            ImageButton(
                "assets/ui/button/back.png",
                (cx, y0 + gap * 3.0),
                self.app.back,
                scale=0.18,
                scale_x=1.4,
                scale_y=1.0,
                hover_scale=1.12,
                click_sound=self.click_sound
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
        # ===== BACKGROUND =====
        screen.fill((6, 22, 44))  # nền xanh đậm đồng bộ menu

        # ===== TITLE =====
        t = self.h1.render(
            "Select Mode",
            True,
            self.app.theme["text"]
        )
        screen.blit(
            t,
            t.get_rect(center=(self.app.width // 2, 220))
        )

        # ===== BUTTONS =====
        for b in self.buttons:
            b.draw(screen)
