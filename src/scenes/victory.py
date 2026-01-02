import pygame
from src.core.scene import Scene
from src.ui.image_button import ImageButton


# =========================
# Helpers
# =========================
def draw_cover(screen, image, w, h, alpha=255):
    if image is None:
        return
    iw, ih = image.get_width(), image.get_height()
    scale = max(w / iw, h / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    surf = pygame.transform.smoothscale(image, (nw, nh))
    if alpha < 255:
        surf.set_alpha(alpha)
    x = (w - nw) // 2
    y = (h - nh) // 2
    screen.blit(surf, (x, y))


# =========================
# VICTORY SCENE
# =========================
class VictoryScene(Scene):
    def on_enter(self, map_id=1, points=0, time_alive=0.0, **kwargs):
        # ===== BACKGROUND =====
        self.bg = self.app.assets.image("assets/bg/khungchoi_bg.jpg")

        # ===== FONTS =====
        self.title_font = self.app.assets.font(
            "assets/fonts/Baloo2-Bold.ttf", 68
        )
        self.font = self.app.assets.font(
            "assets/fonts/Baloo2-Bold.ttf", 26
        )
        self.small = self.app.assets.font(
            "assets/fonts/Baloo2-Bold.ttf", 20
        )

        self.map_id = int(map_id)
        self.points = int(points)
        self.time_alive = float(time_alive)

        # ===== UNLOCK NEXT MAP =====
        next_map = min(3, self.map_id + 1)
        if next_map != self.map_id:
            self.app.save.unlock_map(next_map)

        # sync fish unlock
        self.app.save.sync_unlocked_fish_by_progress()

        # ===== SAVE HISTORY + HIGHSCORE =====
        self.app.save.update_highscore(self.map_id, self.points)
        mode = int(self.app.runtime.get("mode", 1))
        self.app.save.add_history(
            mode=mode,
            map_id=self.map_id,
            points=self.points,
            time_alive=self.time_alive,
            result="WIN",
        )
        self.app.save.save()

        # ===== CLICK SOUND =====
        try:
            self.click_sound = self.app.assets.sound(
                "assets/sound/click.wav"
            )
        except Exception:
            self.click_sound = None

        # ===== BUTTON LAYOUT =====
        cx = self.app.width // 2
        y0 = 430
        gap = 90

        # ===== IMAGE BUTTONS =====
        self.buttons = [
            ImageButton(
                "assets/ui/button/next.png",
                (cx, y0),
                self._next_map,
                scale=0.22,
                scale_x=1.6,
                scale_y=1.0,
                hover_scale=1.15,
                click_sound=self.click_sound
            ),
            ImageButton(
                "assets/ui/button/map_select.png",
                (cx, y0 + gap),
                self._go_map_select,
                scale=0.22,
                scale_x=1.6,
                scale_y=1.0,
                hover_scale=1.15,
                click_sound=self.click_sound
            ),
            ImageButton(
                "assets/ui/button/menu.png",
                (cx, y0 + gap * 2),
                self._go_menu,
                scale=0.22,
                scale_x=1.6,
                scale_y=1.0,
                hover_scale=1.15,
                click_sound=self.click_sound
            ),
        ]

    # ======================
    # Actions
    # ======================
    def _go_menu(self):
        from src.scenes.menu import MenuScene
        self.app.scenes.set_scene(MenuScene(self.app))

    def _go_map_select(self):
        from src.scenes.map_select import MapSelectScene
        self.app.scenes.set_scene(MapSelectScene(self.app))

    def _next_map(self):
        from src.scenes.game_scene import GameScene
        import json

        next_id = min(3, self.map_id + 1)
        try:
            with open(
                f"data/maps/map{next_id}.json",
                "r",
                encoding="utf-8"
            ) as f:
                map_data = json.load(f)
        except Exception:
            map_data = {
                "id": next_id,
                "name": f"Map {next_id}",
                "bg": None,
                "world_size": [3200, 1800],
            }

        self.app.runtime["map"] = map_data
        self.app.scenes.set_scene(
            GameScene(self.app),
            map_data=map_data
        )

    # ======================
    # Events / Draw
    # ======================
    def handle_event(self, event):
        for b in self.buttons:
            b.handle_event(event)

    def draw(self, screen):
        draw_cover(screen, self.bg, self.app.width, self.app.height)

        # overlay
        overlay = pygame.Surface(
            (self.app.width, self.app.height),
            pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 105))
        screen.blit(overlay, (0, 0))

        # ===== TITLE =====
        title = self.title_font.render(
            "VICTORY!", True, (255, 235, 170)
        )
        screen.blit(
            title,
            title.get_rect(center=(self.app.width // 2, 170))
        )

        # ===== INFO =====
        info1 = self.font.render(
            f"Map {self.map_id} cleared",
            True, (235, 245, 255)
        )
        info2 = self.font.render(
            f"Points: {self.points}",
            True, (235, 245, 255)
        )
        info3 = self.font.render(
            f"Time alive: {self.time_alive:.1f}s",
            True, (235, 245, 255)
        )

        screen.blit(info1, info1.get_rect(center=(self.app.width // 2, 260)))
        screen.blit(info2, info2.get_rect(center=(self.app.width // 2, 295)))
        screen.blit(info3, info3.get_rect(center=(self.app.width // 2, 330)))

        # ===== BUTTONS =====
        for b in self.buttons:
            b.draw(screen)
