import json
import pygame
from src.core.scene import Scene
from src.ui.image_button import ImageButton


# =========================
# CONSTANT
# =========================
FONT_PATH = "assets/fonts/Baloo2-Bold.ttf"


# =========================
# HELPERS
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
# MAP CARD
# =========================
class MapCard:
    def __init__(self, rect, map_data, thumb, unlocked, font_title, font_small):
        self.rect = pygame.Rect(rect)
        self.map = map_data
        self.thumb = thumb
        self.unlocked = unlocked
        self.font_title = font_title
        self.font_small = font_small

        self.hover = 0.0
        self.lift = 0.0

    def update(self, dt, mouse_pos):
        target = 1.0 if self.rect.collidepoint(mouse_pos) else 0.0
        self.hover += (target - self.hover) * min(1.0, dt * 10)
        self.lift = self.hover * 6

    def hit(self, pos):
        return self.rect.collidepoint(pos)

    def draw(self, screen, selected=False):
        r = self.rect.copy()
        r.y -= int(self.lift)

        # glow
        if self.hover > 0.01:
            glow = pygame.Surface((r.w + 20, r.h + 20), pygame.SRCALPHA)
            pygame.draw.rect(
                glow, (120, 200, 255, int(90 * self.hover)),
                glow.get_rect(), border_radius=22
            )
            screen.blit(glow, (r.x - 10, r.y - 10))

        bg_color = (12, 26, 46)
        border = (120, 200, 255) if (selected or self.hover > 0.2) else (60, 90, 130)
        pygame.draw.rect(screen, bg_color, r, border_radius=18)
        pygame.draw.rect(screen, border, r, 2, border_radius=18)

        thumb_rect = pygame.Rect(r.x + 12, r.y + 12, 140, r.h - 24)
        pygame.draw.rect(screen, (0, 0, 0), thumb_rect, border_radius=14)

        if self.thumb:
            tw, th = self.thumb.get_width(), self.thumb.get_height()
            scale = max(thumb_rect.w / tw, thumb_rect.h / th)
            nw, nh = int(tw * scale), int(th * scale)
            img = pygame.transform.smoothscale(self.thumb, (nw, nh))
            screen.blit(
                img,
                (thumb_rect.centerx - nw // 2,
                 thumb_rect.centery - nh // 2)
            )

        name = self.map.get("name", "Map")
        wsize = self.map.get("world_size", [3000, 1800])

        tx = r.x + 170
        ty = r.y + 22

        screen.blit(
            self.font_title.render(name, True, (235, 245, 255)),
            (tx, ty)
        )
        screen.blit(
            self.font_small.render(
                f"World: {wsize[0]} x {wsize[1]}",
                True, (190, 210, 235)
            ),
            (tx, ty + 32)
        )

        if not self.unlocked:
            overlay = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, r.topleft)

            lock = self.font_title.render("🔒 KHÓA", True, (255, 220, 120))
            screen.blit(lock, lock.get_rect(center=r.center))


# =========================
# MAP SELECT SCENE
# =========================
class MapSelectScene(Scene):
    def on_enter(self, **kwargs):
        # ===== FONT =====
        self.h1 = self.app.assets.font(FONT_PATH, 46)
        self.font_card = self.app.assets.font(FONT_PATH, 26)
        self.font_small = self.app.assets.font(FONT_PATH, 18)

        # ===== BACKGROUND =====
        self.bg = self.app.assets.image("assets/bg/khungchoi_bg.jpg")

        # ===== LOAD MAP DATA =====
        self.maps = []
        for i in [1, 2, 3]:
            with open(f"data/maps/map{i}.json", "r", encoding="utf-8") as f:
                self.maps.append(json.load(f))

        self.thumbs = {}
        for i in [1, 2, 3]:
            try:
                self.thumbs[i] = self.app.assets.image(
                    f"assets/bg/map{i}_bg.jpg"
                )
            except Exception:
                self.thumbs[i] = None

        # ===== CREATE CARDS =====
        cx = self.app.width // 2
        y0 = 240
        self.cards = []

        for idx, m in enumerate(self.maps):
            map_id = int(m.get("id", idx + 1))
            unlocked = self.app.save.is_unlocked_map(map_id)
            rect = (cx - 320, y0 + idx * 140, 640, 120)

            self.cards.append(
                MapCard(
                    rect, m, self.thumbs.get(map_id),
                    unlocked, self.font_card, self.font_small
                )
            )

        # ===== BACK IMAGE BUTTON =====
        self.btn_back = ImageButton(
            "assets/ui/button/back.png",
            (70, 50),
            self._go_back,
            scale=0.12,
            hover_scale=1.15
        )

        self.selected_index = 0

    # =========================
    # BACK
    # =========================
    def _go_back(self):
        from src.scenes.mode_select import ModeSelectScene
        self.app.scenes.set_scene(ModeSelectScene(self.app))

    # =========================
    # EVENTS
    # =========================
    def handle_event(self, event):
        self.btn_back.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, card in enumerate(self.cards):
                if card.hit(event.pos):
                    self.selected_index = i
                    if card.unlocked:
                        self._start(card.map)

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = (self.selected_index - 1) % len(self.cards)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = (self.selected_index + 1) % len(self.cards)
            elif event.key == pygame.K_RETURN:
                card = self.cards[self.selected_index]
                if card.unlocked:
                    self._start(card.map)

    def update(self, dt):
        mouse = pygame.mouse.get_pos()
        for card in self.cards:
            card.update(dt, mouse)

    def _start(self, map_data):
        from src.scenes.fish_select import FishSelectScene
        self.app.runtime["map"] = map_data
        self.app.scenes.set_scene(FishSelectScene(self.app))

    # =========================
    # DRAW
    # =========================
    def draw(self, screen):
        draw_cover(screen, self.bg, self.app.width, self.app.height)

        overlay = pygame.Surface((self.app.width, self.app.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))

        title = self.h1.render("Select Map", True, self.app.theme["text"])
        screen.blit(title, (70, 70))

        for i, card in enumerate(self.cards):
            card.draw(screen, selected=(i == self.selected_index))

        self.btn_back.draw(screen)
