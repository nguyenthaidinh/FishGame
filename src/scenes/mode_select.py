import pygame
from src.core.scene import Scene
from src.ui.image_button import ImageButton
from src.scenes.map_select import MapSelectScene


# =========================
# Helpers
# =========================
def scale_cover(image, w, h):
    """
    Scale ảnh nền kiểu cover:
    - Phủ kín toàn bộ màn hình
    - Giữ đúng tỉ lệ ảnh
    """
    iw, ih = image.get_width(), image.get_height()
    scale = max(w / iw, h / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    return pygame.transform.smoothscale(image, (nw, nh))


# =========================
# MODE SELECT SCENE
# =========================
class ModeSelectScene(Scene):
    def on_enter(self, **kwargs):
        # ===== BACKGROUND =====
        # (có thể dùng chung ảnh với menu chính)
        bg_raw = self.app.assets.image("assets/bg/mode_bg.png")
        self.bg = scale_cover(bg_raw, self.app.width, self.app.height)

        # ===== FONT (TITLE) =====
        self.h1 = self.app.assets.font(
            "assets/fonts/Fredoka-Bold.ttf", 46
        )

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
                scale_x=1.5,
                scale_y=1.0,
                hover_scale=1.15,
                click_sound=self.click_sound
            ),

            # ===== 2 PLAYERS =====
            ImageButton(
                "assets/ui/button/2_player.png",
                (cx, y0 + gap * 1.5),
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
        screen.blit(
            self.bg,
            self.bg.get_rect(
                center=(self.app.width // 2, self.app.height // 2)
            )
        )

        # ===== OVERLAY NHẸ (CHO NÚT NỔI) =====
        overlay = pygame.Surface(
            (self.app.width, self.app.height), pygame.SRCALPHA
        )
        overlay.fill((0, 30, 60, 70))  # xanh đậm mờ
        screen.blit(overlay, (0, 0))

        # ===== TITLE =====
        title = self.h1.render(
            "Select Mode",
            True,
            self.app.theme["text"]
        )
        screen.blit(
            title,
            title.get_rect(center=(self.app.width // 2, 220))
        )

        # ===== BUTTONS =====
        for b in self.buttons:
            b.draw(screen)
