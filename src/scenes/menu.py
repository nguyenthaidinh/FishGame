import pygame
from src.core.scene import Scene
from src.ui.image_button import ImageButton


def scale_cover(image, w, h):
    if image is None:
        return None

    iw, ih = image.get_width(), image.get_height()
    scale = max(w / iw, h / ih)
    nw, nh = int(iw * scale), int(ih * scale)

    return pygame.transform.smoothscale(image, (nw, nh))


class MenuScene(Scene):
    def on_enter(self, **kwargs):
        # ===== BACKGROUND =====
        bg_raw = self.app.assets.image("assets/bg/khungchoi_bg.jpg")
        self.bg = scale_cover(bg_raw, self.app.width, self.app.height)

        # ===== FONTS =====
        self.title_font = self.app.assets.font(None, 64)
        self.sub_font = self.app.assets.font(None, 26)

        # ===== LAYOUT CHUẨN UI GAME =====
        cx = self.app.width // 2
        y0 = int(self.app.height * 0.38)   # menu hơi cao hơn trung tâm

        gap = 90        # khoảng cách nút thường
        exit_gap = 120  # EXIT cách xa hơn để tránh bấm nhầm

        # ===== MENU BUTTONS =====
        self.buttons = [
            # START – NỔI BẬT
            ImageButton(
                "assets/ui/button/start.png",
                (cx, y0),
                self._go_mode,
                scale=0.15,
                hover_scale=1.18
            ),

            # RANKING
            ImageButton(
                "assets/ui/button/ranking.png",
                (cx, y0 + gap),
                self._go_leaderboard,
                scale=0.15,
                hover_scale=1.12
            ),

            # HISTORY
            ImageButton(
                "assets/ui/button/history.png",
                (cx, y0 + gap * 2),
                self._go_history,
                scale=0.15,
                hover_scale=1.12
            ),

            # EXIT – TÁCH RIÊNG
            ImageButton(
                "assets/ui/button/exit.png",
                (cx, y0 + gap * 3),
                self.app.quit,
                scale=0.15,
                hover_scale=1.12,
                
            ),
        ]

        # ===== SOUND BUTTON – GÓC TRÁI =====
        self.sound_button = ImageButton(
            "assets/ui/button/sound.png",
            (70, self.app.height - 90),
            self.app.toggle_sound,
            scale=0.11,
            hover_scale=1.15,
            alt_image_path="assets/ui/button/mute.png"
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

        # ===== OVERLAY NHẸ =====
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

        screen.blit(title, title.get_rect(center=(self.app.width // 2, 150)))
        screen.blit(subtitle, subtitle.get_rect(center=(self.app.width // 2, 200)))

        # ===== BUTTONS =====
        for b in self.buttons:
            b.draw(screen)

        self.sound_button.draw(screen)
