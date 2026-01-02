import pygame
from src.core.scene import Scene
from src.ui.image_button import ImageButton


# =========================
# Helper: scale cover background
# =========================
def scale_cover(image, w, h):
    iw, ih = image.get_width(), image.get_height()
    scale = max(w / iw, h / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    return pygame.transform.smoothscale(image, (nw, nh))


# =========================
# MENU SCENE
# =========================
class MenuScene(Scene):
    def on_enter(self, **kwargs):
        # ==================================================
        # 🎨 BACKGROUND
        # ==================================================
        bg_raw = self.app.assets.image("assets/bg/khungchoi_bg.jpg")
        self.bg = scale_cover(bg_raw, self.app.width, self.app.height)

        # ==================================================
        # 🔤 FONTS
        # ==================================================
        self.title_font = self.app.assets.font(
            "assets/fonts/Fredoka-Bold.ttf", 72
        )
        self.sub_font = self.app.assets.font(
            "assets/fonts/Baloo2-Bold.ttf", 26
        )

        # ==================================================
        # 🔊 SOUNDS
        # ==================================================
        self.click_sound = self.app.assets.sound(
            "assets/sound/click.wav"
        )

        # ==================================================
        # 🎵 MENU BGM
        # ==================================================
        if self.app.sound_on:
            pygame.mixer.music.stop()
            pygame.mixer.music.load("assets/sound/bgm_game.mp3")
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(-1)

        # ==================================================
        # 📐 LAYOUT
        # ==================================================
        cx = self.app.width // 2
        y0 = int(self.app.height * 0.38)
        gap = 95

        # ==================================================
        # 🟦 MAIN BUTTONS
        # ==================================================
        self.buttons = [
            ImageButton(
                "assets/ui/button/start.png",
                (cx, y0),
                self._go_mode,
                scale=0.2,
                scale_x=1.5,
                hover_scale=1.2,
                click_sound=self.click_sound
            ),
            ImageButton(
                "assets/ui/button/ranking.png",
                (cx, y0 + gap),
                self._go_leaderboard,
                scale=0.2,
                scale_x=1.5,
                hover_scale=1.2,
                click_sound=self.click_sound
            ),
            ImageButton(
                "assets/ui/button/history.png",
                (cx, y0 + gap * 2.5),
                self._go_history,
                scale=0.2,
                scale_x=1.5,
                hover_scale=1.2,
                click_sound=self.click_sound
            ),
            ImageButton(
                "assets/ui/button/exit.png",
                (cx, y0 + gap * 3.5),
                self.app.quit,
                scale=0.2,
                scale_x=1.5,
                hover_scale=1.2,
                click_sound=self.click_sound
            ),
        ]

        # ==================================================
        # 🔈 SOUND BUTTON (BOTTOM LEFT)
        # ==================================================
        self.sound_button = ImageButton(
            "assets/ui/button/sound.png",
            (70, self.app.height - 90),
            self.app.toggle_sound,
            scale=0.11,
            alt_image_path="assets/ui/button/mute.png",
            click_sound=self.click_sound
        )
        self.sound_button.use_alt = not self.app.sound_on

        # ==================================================
        # ⚙️ SETTING BUTTON (BOTTOM RIGHT)
        # ==================================================
        self.setting_button = ImageButton(
            "assets/ui/button/setting.png",
            (self.app.width - 70, self.app.height - 90),
            self._go_setting,
            scale=0.11,
            hover_scale=1.2,
            click_sound=self.click_sound
        )

    # =========================
    # Navigation
    # =========================
    def _go_mode(self):
        pygame.mixer.music.fadeout(600)
        from src.scenes.mode_select import ModeSelectScene
        self.app.scenes.set_scene(ModeSelectScene(self.app))

    def _go_leaderboard(self):
        from src.scenes.leaderboard import LeaderboardScene
        self.app.scenes.set_scene(LeaderboardScene(self.app))

    def _go_history(self):
        from src.scenes.history import HistoryScene
        self.app.scenes.set_scene(HistoryScene(self.app))

    def _go_setting(self):
        # 👉 GẮN SETTINGS SCENE CŨ CỦA BẠN
        from src.core.settings import SettingsScene
        self.app.scenes.set_scene(SettingsScene(self.app))

    # =========================
    # EVENTS
    # =========================
    def handle_event(self, event):
        for b in self.buttons:
            b.handle_event(event)
        self.sound_button.handle_event(event)
        self.setting_button.handle_event(event)

    # =========================
    # UPDATE
    # =========================
    def update(self, dt):
        pass

    # =========================
    # DRAW
    # =========================
    def draw(self, screen):
        # background
        screen.blit(
            self.bg,
            self.bg.get_rect(
                center=(self.app.width // 2, self.app.height // 2)
            )
        )

        # overlay
        overlay = pygame.Surface(
            (self.app.width, self.app.height), pygame.SRCALPHA
        )
        overlay.fill((0, 40, 80, 35))
        screen.blit(overlay, (0, 0))

        # title
        title = self.title_font.render(
            "Blue Ocean", True, (255, 255, 255)
        )
        subtitle = self.sub_font.render(
            "Một đại dương, một quy luật.",
            True, (220, 240, 255)
        )

        screen.blit(
            title,
            title.get_rect(center=(self.app.width // 2, 140))
        )
        screen.blit(
            subtitle,
            subtitle.get_rect(center=(self.app.width // 2, 200))
        )

        # buttons
        for b in self.buttons:
            b.draw(screen)

        self.sound_button.draw(screen)
        self.setting_button.draw(screen)
