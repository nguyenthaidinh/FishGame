import json
import pygame
from src.core.scene import Scene
from src.ui.image_button import ImageButton

FONT_PATH = "assets/fonts/Baloo2-Bold.ttf"


# =========================
# HELPERS
# =========================
def draw_cover(screen, image, w, h, alpha=255):
    iw, ih = image.get_width(), image.get_height()
    scale = max(w / iw, h / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    surf = pygame.transform.smoothscale(image, (nw, nh))
    if alpha < 255:
        surf.set_alpha(alpha)
    screen.blit(
        surf,
        ((w - nw) // 2, (h - nh) // 2)
    )


def draw_rounded_image(screen, img, rect, radius=16):
    mask = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=radius)

    tw, th = img.get_width(), img.get_height()
    scale = max(rect.w / tw, rect.h / th)
    nw, nh = int(tw * scale), int(th * scale)
    img = pygame.transform.smoothscale(img, (nw, nh))

    temp = pygame.Surface(rect.size, pygame.SRCALPHA)
    temp.blit(img, ((rect.w - nw) // 2, (rect.h - nh) // 2))
    temp.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    screen.blit(temp, rect.topleft)


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

    def update(self, dt, mouse):
        target = 1.0 if self.rect.collidepoint(mouse) else 0.0
        self.hover += (target - self.hover) * min(1.0, dt * 10)

    def hit(self, pos):
        return self.rect.collidepoint(pos)

    def draw(self, screen, selected=False):
        lift = int(self.hover * 8)
        r = self.rect.move(0, -lift)

        # glow
        if self.hover > 0:
            glow = pygame.Surface((r.w + 16, r.h + 16), pygame.SRCALPHA)
            pygame.draw.rect(
                glow, (120, 200, 255, int(80 * self.hover)),
                glow.get_rect(), border_radius=24
            )
            screen.blit(glow, (r.x - 8, r.y - 8))

        # card bg
        pygame.draw.rect(screen, (10, 24, 40), r, border_radius=20)
        pygame.draw.rect(
            screen,
            (140, 210, 255) if (selected or self.hover > 0.3) else (70, 110, 160),
            r, 2, border_radius=20
        )

        # thumbnail
        thumb_rect = pygame.Rect(r.x + 16, r.y + 16, 160, r.h - 32)
        if self.thumb:
            draw_rounded_image(screen, self.thumb, thumb_rect, radius=14)

        # text
        name = self.map.get("name", "Map")
        w, h = self.map.get("world_size", [0, 0])

        screen.blit(
            self.font_title.render(name, True, (235, 245, 255)),
            (thumb_rect.right + 20, r.y + 30)
        )
        screen.blit(
            self.font_small.render(f"World: {w} x {h}", True, (190, 210, 235)),
            (thumb_rect.right + 20, r.y + 64)
        )

        if not self.unlocked:
            lock = pygame.Surface(r.size, pygame.SRCALPHA)
            lock.fill((0, 0, 0, 160))
            screen.blit(lock, r.topleft)
            txt = self.font_title.render("🔒 LOCKED", True, (255, 220, 120))
            screen.blit(txt, txt.get_rect(center=r.center))


# =========================
# MAP SELECT SCENE
# =========================
class MapSelectScene(Scene):
    def on_enter(self, **kwargs):
        self.bg = self.app.assets.image("assets/bg/khungchoi_bg.jpg")

        self.h1 = self.app.assets.font(FONT_PATH, 46)
        self.font_card = self.app.assets.font(FONT_PATH, 26)
        self.font_small = self.app.assets.font(FONT_PATH, 18)

        # maps
        self.maps = []
        for i in [1, 2, 3]:
            with open(f"data/maps/map{i}.json", "r", encoding="utf-8") as f:
                self.maps.append(json.load(f))

        self.thumbs = {
            i: self.app.assets.image(f"assets/bg/map{i}_bg.jpg")
            for i in [1, 2, 3]
        }

        # cards
        cx = self.app.width // 2
        y0 = 240
        self.cards = []

        for i, m in enumerate(self.maps):
            rect = (cx - 360, y0 + i * 150, 720, 130)
            unlocked = self.app.save.is_unlocked_map(int(m["id"]))
            self.cards.append(
                MapCard(rect, m, self.thumbs[int(m["id"])], unlocked,
                        self.font_card, self.font_small)
            )

        # 🔙 IMAGE BACK BUTTON
        self.btn_back = ImageButton(
            "assets/ui/button/back.png",
            (70, 60),
            self._go_back,
            scale=0.14,
            hover_scale=1.15
        )

        self.selected_index = 0

    def _go_back(self):
        from src.scenes.mode_select import ModeSelectScene
        self.app.scenes.set_scene(ModeSelectScene(self.app))

    def handle_event(self, event):
        self.btn_back.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, c in enumerate(self.cards):
                if c.hit(event.pos) and c.unlocked:
                    self._start(c.map)

    def update(self, dt):
        mouse = pygame.mouse.get_pos()
        for c in self.cards:
            c.update(dt, mouse)

    def _start(self, map_data):
        from src.scenes.fish_select import FishSelectScene
        self.app.runtime["map"] = map_data
        self.app.scenes.set_scene(FishSelectScene(self.app))

    def draw(self, screen):
        draw_cover(screen, self.bg, self.app.width, self.app.height)

        overlay = pygame.Surface((self.app.width, self.app.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 90))
        screen.blit(overlay, (0, 0))

        screen.blit(
            self.h1.render("Select Map", True, (255, 255, 255)),
            (90, 80)
        )

        for i, c in enumerate(self.cards):
            c.draw(screen, selected=(i == self.selected_index))

        self.btn_back.draw(screen)
