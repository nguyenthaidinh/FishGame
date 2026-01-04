import pygame
from src.core.scene import Scene
from src.ui.image_button import ImageButton
from src.scenes.map_select import MapSelectScene


# =========================
# Helpers
# =========================
def scale_cover(image, w, h):
    iw, ih = image.get_width(), image.get_height()
    if iw <= 0 or ih <= 0:
        return None
    scale = max(w / iw, h / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    return pygame.transform.smoothscale(image, (nw, nh))


# =========================
# MODE SELECT SCENE
# =========================
class ModeSelectScene(Scene):
    def on_enter(self, **kwargs):
        # ===== BACKGROUND =====
        bg_raw = self.app.assets.image("assets/bg/mode_bg.png")
        self.bg = scale_cover(bg_raw, self.app.width, self.app.height)

        # ===== FONT =====
        self.h1 = self.app.assets.font(
            "assets/fonts/Fredoka-Bold.ttf", 46
        )

        # ===== CLICK SOUND =====
        self.click_sound = self.app.assets.sound(
            "assets/sound/click.wav"
        )

        # ===== BACKGROUND MUSIC =====
        self._play_bgm()

        # ===== LAYOUT =====
        cx = self.app.width // 2
        y0 = int(self.app.height * 0.40)
        gap = 100

        # ===== IMAGE BUTTONS =====
        self.buttons = [
            ImageButton(
                "assets/ui/button/1_player.png",
                (cx, y0),
                lambda: self._pick(1),
                scale=0.22,
                scale_x=1.5,
                hover_scale=1.15,
                click_sound=self.click_sound
            ),
            ImageButton(
                "assets/ui/button/2_player.png",
                (cx, y0 + gap * 1.5),
                lambda: self._pick(2),
                scale=0.22,
                scale_x=1.5,
                hover_scale=1.15,
                click_sound=self.click_sound
            ),
            ImageButton(
                "assets/ui/button/back.png",
                (cx, y0 + gap * 3.0),
                self._go_menu,
                scale=0.18,     
                scale_x=1.4,
                hover_scale=1.12,
                click_sound=self.click_sound
            ),
        ]

    # =========================
    # MUSIC
    # =========================
    def _play_bgm(self):
        try:
            pygame.mixer.music.load("assets/sound/mode_bgm.mp3")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print("[WARN] Cannot play mode bgm:", e)

    def on_exit(self):
        pygame.mixer.music.stop()

    # =========================
    # LOGIC
    # =========================
    def _pick(self, mode: int):
        # ✅ set mode cho GameScene
        self.app.runtime["mode"] = mode

        # ✅ clear players cũ để tránh sót 2P/1P
        self.app.runtime.pop("players", None)

        self.app.scenes.set_scene(MapSelectScene(self.app))

    def _go_menu(self):
        from src.scenes.menu import MenuScene
        self.app.scenes.set_scene(MenuScene(self.app))

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
        if self.bg:
            screen.blit(
                self.bg,
                self.bg.get_rect(
                    center=(self.app.width // 2, self.app.height // 2)
                )
            )
        else:
            screen.fill((8, 30, 55))

        overlay = pygame.Surface(
            (self.app.width, self.app.height), pygame.SRCALPHA
        )
        overlay.fill((0, 30, 60, 70))
        screen.blit(overlay, (0, 0))

        title = self.h1.render(
            "Select Mode",
            True,
            self.app.theme["text"]
        )
        screen.blit(
            title,
            title.get_rect(center=(self.app.width // 2, 220))
        )

        for b in self.buttons:
            b.draw(screen)
