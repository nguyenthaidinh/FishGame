import json
import pygame
from src.core.scene import Scene
from src.ui.image_button import ImageButton
from src.entities.animated_sprite import AnimatedSprite


# =========================
# Helpers
# =========================
def clamp(x, a, b):
    return a if x < a else b if x > b else x


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
# Fish Card
# =========================
class FishCard:
    def __init__(self, rect, fish_id, name, folder, unlocked):
        self.rect = pygame.Rect(rect)
        self.fish_id = fish_id
        self.name = name
        self.folder = folder
        self.unlocked = unlocked

        self.sprite = AnimatedSprite(
            [f"{folder}/swim_01.png", f"{folder}/swim_02.png"],
            fps=8
        )
        self.hover = 0.0

    def update(self, dt, mouse_pos):
        self.sprite.update(dt)
        target = 1.0 if self.rect.collidepoint(mouse_pos) else 0.0
        self.hover += (target - self.hover) * min(1.0, dt * 10.0)

    def hit(self, pos):
        return self.rect.collidepoint(pos)

    def draw(self, screen, font_name, font_small, selected=False):
        lift = int(6 * self.hover)
        r = self.rect.copy()
        r.y -= lift

        pygame.draw.rect(screen, (12, 24, 40), r, border_radius=16)
        pygame.draw.rect(
            screen,
            (255, 220, 120) if selected else (90, 150, 210),
            r,
            2,
            border_radius=16
        )

        img = self.sprite.get_image(scale=0.82)
        screen.blit(img, img.get_rect(center=r.center))

        name_s = font_name.render(self.name, True, (235, 245, 255))
        screen.blit(name_s, (r.x + 16, r.y + r.h - 32))


# =========================
# Fish Select Scene
# =========================
class FishSelectScene(Scene):
    def on_enter(self, **kwargs):
        self.bg = self.app.assets.image("assets/bg/khungchoi_bg.jpg")

        with open("data/player_fish.json", "r", encoding="utf-8") as f:
            self.fish_db = json.load(f)

        self.h1 = self.app.assets.font("assets/fonts/Fredoka-Bold.ttf", 46)
        self.font = self.app.assets.font("assets/fonts/Baloo2-Bold.ttf", 22)

        self.sel_p1 = self.app.save.data.get("selected_fish_p1", "fish01")

        # ===== GRID =====
        self.cards = []
        margin_x = 70
        top = 130
        cols = 4
        gap = 18

        card_w = (self.app.width - margin_x * 2 - gap * (cols - 1)) // cols
        card_h = 170

        for idx, (fish_id, meta) in enumerate(self.fish_db.items()):
            r = idx // cols
            c = idx % cols
            x = margin_x + c * (card_w + gap)
            y = top + r * (card_h + gap)

            self.cards.append(
                FishCard(
                    (x, y, card_w, card_h),
                    fish_id,
                    meta.get("name", fish_id),
                    meta["path"],
                    True
                )
            )

        cx = self.app.width // 2

        # =========================
        # IMAGE BUTTONS
        # =========================
        self.btn_back = ImageButton(
            "assets/ui/button/back.png",
            (80, 50),
            self.app.back,
            scale=0.12,
            hover_scale=1.15
        )

        self.btn_start = ImageButton(
            "assets/ui/button/start.png",
            (cx, 60),
            self._start,
            scale=0.2,
            scale_x=1.6,      # 🔥 kéo dài ngang
            scale_y=1.0,
            hover_scale=1.15
        )

    # =========================
    # Start game
    # =========================
    def _start(self):
        from src.scenes.game_scene import GameScene

        self.app.save.data["selected_fish_p1"] = self.sel_p1
        self.app.save.save()

        map_data = self.app.runtime.get("map")
        if not map_data:
            with open("data/maps/map1.json", "r", encoding="utf-8") as f:
                map_data = json.load(f)
            self.app.runtime["map"] = map_data

        self.app.scenes.set_scene(GameScene(self.app), map_data=map_data)

    # =========================
    # Events
    # =========================
    def handle_event(self, event):
        self.btn_back.handle_event(event)
        self.btn_start.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for card in self.cards:
                if card.hit(event.pos):
                    self.sel_p1 = card.fish_id

    def update(self, dt):
        mouse = pygame.mouse.get_pos()
        for card in self.cards:
            card.update(dt, mouse)

    def draw(self, screen):
        draw_cover(screen, self.bg, self.app.width, self.app.height)

        overlay = pygame.Surface((self.app.width, self.app.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 90))
        screen.blit(overlay, (0, 0))

        title = self.h1.render("Select Fish", True, self.app.theme["text"])
        screen.blit(title, (70, 55))

        for card in self.cards:
            card.draw(screen, self.font, self.font, selected=(card.fish_id == self.sel_p1))

        self.btn_back.draw(screen)
        self.btn_start.draw(screen)
