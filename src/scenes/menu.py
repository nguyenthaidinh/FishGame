import pygame
from src.core.scene import Scene
from src.ui.image_button import ImageButton


# =========================
# Helpers
# =========================
def scale_cover(image, w, h):
    if image is None:
        return None

    iw, ih = image.get_width(), image.get_height()
    scale = max(w / iw, h / ih)
    nw, nh = int(iw * scale), int(ih * scale)

    return pygame.transform.smoothscale(image, (nw, nh))


# =========================
# MENU SCENE
# =========================
class MenuScene(Scene):
    def on_enter(self, **kwargs):
        # ===== BACKGROUND =====
        bg_raw = self.app.assets.image("assets/bg/khungchoi_bg.jpg")
        self.bg = scale_cover(bg_raw, self.app.width, self.app.height)

        # ===== FONTS =====
        self.title_font = self.app.assets.font(None, 64)
        self.sub_font = self.app.assets.font(None, 26)

        # ===== LOAD CLICK SOUND =====
        # (âm thanh click dùng chung cho tất cả button)
        self.click_sound = self.app.assets.sound(
            "assets/sound/click.wav"
        )

        # ===== LAYOUT =====
        cx = self.app.width // 2
        y0 = int(self.app.height * 0.38)   # menu hơi cao hơn trung tâm
        gap = 95

        # ===== MENU BUTTONS =====
        self.buttons = [
            # ===== START (NỔI BẬT) =====
            ImageButton(
                "assets/ui/button/start.png",
                (cx, y0),
                self._go_mode,
                scale=0.2,
                scale_x=2.0,        # ⭐ kéo dài ngang
                scale_y=1.0,
                hover_scale=1.2,
                click_sound=self.click_sound
            ),

            # ===== RANKING =====
            ImageButton(
                "assets/ui/button/ranking.png",
                (cx, y0 + gap),
                self._go_leaderboard,
                scale=0.2,
                scale_x=2.0,
                scale_y=1.0,
                hover_scale=1.2,
                click_sound=self.click_sound
            ),

            # ===== HISTORY =====
            ImageButton(
                "assets/ui/button/history.png",
                (cx, y0 + gap * 2.5),
                self._go_history,
                scale=0.2,
                scale_x=2.0,
                scale_y=1.2,
                hover_scale=1.2,
                click_sound=self.click_sound
            ),

            # ===== EXIT =====
            ImageButton(
                "assets/ui/button/exit.png",
                (cx, y0 + gap * 3.5),
                self.app.quit,
                scale=0.2,
                scale_x=2.0,
                scale_y=1.0,
                hover_scale=1.2,
                click_sound=self.click_sound
            ),
        ]

        # ===== SOUND BUTTON (MUTE / UNMUTE) =====
        self.sound_button = ImageButton(
            "assets/ui/button/sound.png",
            (70, self.app.height - 90),
            self.app.toggle_sound,
            scale=0.11,
            hover_scale=1.0,
            alt_image_path="assets/ui/button/mute.png",
            click_sound=self.click_sound
        )
        self.sound_button.use_alt = not self.app.sound_on

    # =========================
    # Navigation
    # =========================
    def _go_mode(self):
        from src.scenes.mode_select import ModeSelectScene
        self.app.scenes.set_scene(ModeSelectScene(self.app))

    def _go_leaderboard(self):
        from src.scenes.leaderboard import LeaderboardScene
        self.app.scenes.set_scene(LeaderboardScene(self.app))

    def _go_history(self):
        from src.scenes.history import HistoryScene
        self.app.scenes.set_scene(HistoryScene(self.app))

    # =========================
    # EVENTS
    # =========================
    def handle_event(self, event):
        for b in self.buttons:
            b.handle_event(event)

        self.sound_button.handle_event(event)

    # =========================
    # UPDATE
    # =========================
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

        # ===== OVERLAY =====
        overlay = pygame.Surface(
            (self.app.width, self.app.height), pygame.SRCALPHA
        )
        overlay.fill((0, 40, 80, 40))
        screen.blit(overlay, (0, 0))

        # ===== TITLE =====
        title = self.title_font.render(
            "Blue Ocean", True, self.app.theme["text"]
        )
        subtitle = self.sub_font.render(
            "Một đại dương, một quy luật.",
            True,
            self.app.theme["muted"]
        )

        screen.blit(
            title,
            title.get_rect(center=(self.app.width // 2, 150))
        )
        screen.blit(
            subtitle,
            subtitle.get_rect(center=(self.app.width // 2, 200))
        )

        # ===== BUTTONS =====
        for b in self.buttons:
            b.draw(screen)

        self.sound_button.draw(screen)
