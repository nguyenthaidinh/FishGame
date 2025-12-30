import json
import pygame
from src.core.scene import Scene
from src.ui.button import Button


# ---------- helpers ----------
def draw_cover(screen, image, w, h, alpha=255):
    if image is None:
        return
    iw, ih = image.get_width(), image.get_height()
    if iw <= 0 or ih <= 0:
        return
    scale = max(w / iw, h / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    surf = pygame.transform.smoothscale(image, (nw, nh))
    if alpha < 255:
        surf.set_alpha(alpha)
    x = (w - nw) // 2
    y = (h - nh) // 2
    screen.blit(surf, (x, y))


def clamp(x, a, b):
    return a if x < a else b if x > b else x


class MapCard:
    """Card UI: thumbnail + title + lock + hover anim"""
    def __init__(self, rect, map_data, thumb, unlocked, font_title, font_small):
        self.rect = pygame.Rect(rect)
        self.map = map_data
        self.thumb = thumb
        self.unlocked = unlocked
        self.font_title = font_title
        self.font_small = font_small

        self.hover = 0.0
        self._lift = 0.0

    def update(self, dt, mouse_pos):
        target = 1.0 if self.rect.collidepoint(mouse_pos) else 0.0
        self.hover += (target - self.hover) * min(1.0, dt * 10.0)
        self._lift = self.hover * 6.0

    def hit(self, pos):
        return self.rect.collidepoint(pos)

    def draw(self, screen, selected=False):
        # lifted rect for hover
        r = self.rect.copy()
        r.y -= int(self._lift)

        # glow
        if self.hover > 0.01:
            glow = pygame.Surface((r.w + 20, r.h + 20), pygame.SRCALPHA)
            a = int(80 * self.hover)
            pygame.draw.rect(glow, (120, 200, 255, a), glow.get_rect(), border_radius=22)
            screen.blit(glow, (r.x - 10, r.y - 10))

        # base card
        bg = (12, 24, 40)
        border = (120, 200, 255) if (selected or self.hover > 0.2) else (55, 85, 120)
        pygame.draw.rect(screen, bg, r, border_radius=18)
        pygame.draw.rect(screen, border, r, 2, border_radius=18)

        # thumbnail (cropped center)
        thumb_rect = pygame.Rect(r.x + 12, r.y + 12, 140, r.h - 24)
        pygame.draw.rect(screen, (0, 0, 0), thumb_rect, border_radius=14)

        if self.thumb:
            tw, th = self.thumb.get_width(), self.thumb.get_height()
            scale = max(thumb_rect.w / tw, thumb_rect.h / th)
            nw, nh = int(tw * scale), int(th * scale)
            img = pygame.transform.smoothscale(self.thumb, (nw, nh))
            x = thumb_rect.centerx - nw // 2
            y = thumb_rect.centery - nh // 2
            screen.blit(img, (x, y))

        # title + info
        name = self.map.get("name", "Map")
        map_id = int(self.map.get("id", 1))
        wsize = self.map.get("world_size", [3000, 1800])

        tx = r.x + 170
        ty = r.y + 22

        title = self.font_title.render(name, True, (235, 245, 255))
        screen.blit(title, (tx, ty))

        info = self.font_small.render(f"World: {wsize[0]} x {wsize[1]}", True, (190, 210, 235))
        screen.blit(info, (tx, ty + 34))

        goal = self.font_small.render("Goal: 226 pts", True, (190, 210, 235))
        screen.blit(goal, (tx, ty + 56))

        # lock overlay
        if not self.unlocked:
            overlay = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (r.x, r.y))

            lock = self.font_title.render("🔒 Khóa", True, (255, 220, 120))
            screen.blit(lock, lock.get_rect(center=r.center))

            hint = self.font_small.render(f"Cần Win Map {map_id-1} để mở khóa", True, (255, 235, 170))
            screen.blit(hint, hint.get_rect(center=(r.centerx, r.centery + 28)))


class MapSelectScene(Scene):
    def on_enter(self, **kwargs):
        self.h1 = self.app.assets.font(None, 46)
        self.font_card = self.app.assets.font(None, 28)
        self.font_small = self.app.assets.font(None, 18)
        self.btn_font = self.app.assets.font(None, 24)

        # background UI
        self.bg = self.app.assets.image("assets/bg/khungchoi_bg.jpg")

        # click sound (optional)
        self.click_sfx = None
        try:
            self.click_sfx = self.app.assets.sound("assets/sfx/ui_click.wav")
        except Exception:
            self.click_sfx = None

        # load maps
        self.maps = []
        for i in [1, 2, 3]:
            with open(f"data/maps/map{i}.json", "r", encoding="utf-8") as f:
                self.maps.append(json.load(f))

        # load thumbs
        self.thumbs = {}
        for i in [1, 2, 3]:
            try:
                self.thumbs[i] = self.app.assets.image(f"assets/bg/map{i}_bg.jpg")
            except Exception:
                self.thumbs[i] = None

        # build cards
        cx = self.app.w // 2
        y0 = 240
        self.cards = []

        for idx, m in enumerate(self.maps):
            map_id = int(m.get("id", idx + 1))
            unlocked = self.app.save.is_unlocked_map(map_id)
            rect = (cx - 320, y0 + idx * 140, 640, 120)

            self.cards.append(
                MapCard(
                    rect=rect,
                    map_data=m,
                    thumb=self.thumbs.get(map_id),
                    unlocked=unlocked,
                    font_title=self.font_card,
                    font_small=self.font_small
                )
            )

        # back button (keep old button)
        theme = self.app.theme
        self.btn_back = Button((30, 20, 120, 44), "Trở lại", self.app.back, self.btn_font, theme)

        # tooltip
        self.tooltip = ""
        self.tooltip_pos = (0, 0)

        self.selected_index = 0

    def _play_click(self):
        if self.click_sfx:
            try:
                self.click_sfx.play()
            except Exception:
                pass

    def _start(self, map_data):
        from src.scenes.fish_select import FishSelectScene 

        self._play_click()
        self.app.runtime["map"] = map_data
        self.app.scenes.set_scene(FishSelectScene(self.app))

    def handle_event(self, event):
        self.btn_back.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            for i, card in enumerate(self.cards):
                if card.hit(pos):
                    self.selected_index = i
                    if card.unlocked:
                        self._start(card.map)
                    else:
                        self._play_click()  # vẫn click sound nhẹ
                    return

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = (self.selected_index - 1) % len(self.cards)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = (self.selected_index + 1) % len(self.cards)
            elif event.key == pygame.K_RETURN:
                card = self.cards[self.selected_index]
                if card.unlocked:
                    self._start(card.map)
                else:
                    self._play_click()

    def update(self, dt):
        mouse = pygame.mouse.get_pos()
        self.tooltip = ""

        for card in self.cards:
            card.update(dt, mouse)
            if card.hit(mouse) and not card.unlocked:
                map_id = int(card.map.get("id", 1))
                self.tooltip = f"Cần chiến thắng bản đồ {map_id-1} để mở khóa bản đồ này."
                self.tooltip_pos = (mouse[0] + 16, mouse[1] + 12)

    def _draw_tooltip(self, screen):
        if not self.tooltip:
            return
        text = self.font_small.render(self.tooltip, True, (240, 245, 255))
        pad = 10
        w = text.get_width() + pad * 2
        h = text.get_height() + pad * 2
        x, y = self.tooltip_pos
        x = clamp(x, 10, self.app.w - w - 10)
        y = clamp(y, 10, self.app.h - h - 10)
        box = pygame.Rect(x, y, w, h)
        pygame.draw.rect(screen, (0, 0, 0), box, border_radius=12)
        pygame.draw.rect(screen, (120, 200, 255), box, 2, border_radius=12)
        screen.blit(text, (x + pad, y + pad))

    def draw(self, screen):
        # background cover
        draw_cover(screen, self.bg, self.app.w, self.app.h)

        # overlay
        overlay = pygame.Surface((self.app.w, self.app.h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 95))
        screen.blit(overlay, (0, 0))

        # title
        t = self.h1.render("Select Map", True, self.app.theme["text"])
        screen.blit(t, (70, 70))

        # cards
        for i, card in enumerate(self.cards):
            card.draw(screen, selected=(i == self.selected_index))

        # back
        self.btn_back.draw(screen)

        # tooltip
        self._draw_tooltip(screen)
