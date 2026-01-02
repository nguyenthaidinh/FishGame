import json
import pygame
from src.core.scene import Scene
from src.ui.button import Button
from src.entities.animated_sprite import AnimatedSprite


def clamp(x, a, b):
    return a if x < a else b if x > b else x


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

    def draw(self, screen, font_name, font_small, selected=False, active=False, subtitle=""):
        lift = int(6 * self.hover)
        r = self.rect.copy()
        r.y -= lift

        shadow = pygame.Surface((r.w + 10, r.h + 10), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 110), shadow.get_rect(), border_radius=18)
        screen.blit(shadow, (r.x - 5, r.y - 2))

        if self.hover > 0.01:
            glow = pygame.Surface((r.w + 22, r.h + 22), pygame.SRCALPHA)
            a = int(85 * self.hover)
            pygame.draw.rect(glow, (120, 200, 255, a), glow.get_rect(), border_radius=22)
            screen.blit(glow, (r.x - 11, r.y - 11))

        base_bg = (12, 24, 40)
        border = (120, 200, 255) if (selected or self.hover > 0.2) else (55, 85, 120)
        if active and selected:
            border = (255, 220, 120)

        pygame.draw.rect(screen, base_bg, r, border_radius=16)
        pygame.draw.rect(screen, border, r, 2, border_radius=16)

        frame = pygame.Rect(r.x + 10, r.y + 10, r.w - 20, 92)
        pygame.draw.rect(screen, (8, 16, 28), frame, border_radius=14)
        pygame.draw.rect(screen, (40, 70, 105), frame, 2, border_radius=14)

        img = self.sprite.get_image(scale=0.82)
        screen.blit(img, img.get_rect(center=frame.center))

        vign = pygame.Surface((frame.w, frame.h), pygame.SRCALPHA)
        pygame.draw.rect(vign, (0, 0, 0, 70), vign.get_rect(), border_radius=14)
        screen.blit(vign, (frame.x, frame.y))

        name_s = font_name.render(self.name, True, (235, 245, 255))
        screen.blit(name_s, (r.x + 16, r.y + 108))

        if subtitle:
            sub = font_small.render(subtitle, True, (190, 210, 235))
            screen.blit(sub, (r.x + 16, r.y + 132))

        if not self.unlocked:
            overlay = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 155))
            screen.blit(overlay, (r.x, r.y))
            lock = font_small.render("LOCKED", True, (255, 220, 120))
            screen.blit(lock, lock.get_rect(center=r.center))


class FishSelectScene(Scene):
    def on_enter(self, **kwargs):
        self.bg = self.app.assets.image("assets/bg/khungchoi_bg.jpg")

        self.app.save.sync_unlocked_fish_by_progress()
        self.app.save.save()

        self.mode = int(self.app.runtime.get("mode", 1))

        with open("data/player_fish.json", "r", encoding="utf-8") as f:
            self.fish_db = json.load(f)

        self.h1 = self.app.assets.font(None, 46)
        self.font = self.app.assets.font(None, 22)
        self.small = self.app.assets.font(None, 18)
        self.btn_font = self.app.assets.font(None, 22)

        self.sel_p1 = self.app.save.data.get("selected_fish_p1", "fish01")
        self.sel_p2 = self.app.save.data.get("selected_fish_p2", "fish02")

        self.active_player = 1
        self.max_map = self.app.save.progress_max_map()
        self.allowed = self.app.save.allowed_fish_count_by_progress()

        self.cards = []
        margin_x = 70
        top = 190
        cols = 4
        gap = 18

        card_w = (
            self.app.width - margin_x * 2 - gap * (cols - 1)
        ) // cols
        card_h = 170

        for idx, (fish_id, meta) in enumerate(self.fish_db.items()):
            r = idx // cols
            c = idx % cols
            x = margin_x + c * (card_w + gap)
            y = top + r * (card_h + gap)

            folder = meta["path"]
            name = meta.get("name", fish_id)
            unlocked = self.app.save.is_unlocked_fish(fish_id)

            self.cards.append(
                FishCard((x, y, card_w, card_h), fish_id, name, folder, unlocked)
            )

        theme = self.app.theme
        self.btn_back = Button((30, 20, 120, 44), "BACK", self.app.back, self.btn_font, theme)
        self.btn_start = Button(
            (self.app.width // 2 - 170, 670, 340, 56),
            "START",
            self._start,
            self.btn_font,
            theme
        )

        self.toggle_p1 = pygame.Rect(70, 130, 140, 42)
        self.toggle_p2 = pygame.Rect(220, 130, 140, 42)

        self.tooltip = ""
        self.tooltip_pos = (0, 0)

    def _start(self):
        from src.scenes.game_scene import GameScene

        self.app.save.data["selected_fish_p1"] = self.sel_p1
        if self.mode == 2:
            self.app.save.data["selected_fish_p2"] = self.sel_p2
        self.app.save.save()

        map_data = self.app.runtime.get("map")
        if not map_data:
            with open("data/maps/map1.json", "r", encoding="utf-8") as f:
                map_data = json.load(f)
            self.app.runtime["map"] = map_data

        self.app.scenes.set_scene(GameScene(self.app), map_data=map_data)

    def _unlock_hint(self, fish_id: str) -> str:
        try:
            n = int(fish_id.replace("fish", ""))
        except Exception:
            n = 99
        if n <= 3:
            return "Unlocked (Map 1)"
        if n <= 8:
            return "Unlock at Map 2"
        return "Unlock at Map 3"

    def handle_event(self, event):
        self.btn_back.handle_event(event)
        self.btn_start.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mp = event.pos

            if self.mode == 2:
                if self.toggle_p1.collidepoint(mp):
                    self.active_player = 1
                elif self.toggle_p2.collidepoint(mp):
                    self.active_player = 2

            for card in self.cards:
                if card.hit(mp):
                    if not card.unlocked:
                        return
                    if self.mode == 1:
                        self.sel_p1 = card.fish_id
                    else:
                        if self.active_player == 1:
                            self.sel_p1 = card.fish_id
                        else:
                            self.sel_p2 = card.fish_id

    def update(self, dt):
        mouse = pygame.mouse.get_pos()
        self.tooltip = ""

        for card in self.cards:
            card.update(dt, mouse)
            if card.rect.collidepoint(mouse) and not card.unlocked:
                self.tooltip = self._unlock_hint(card.fish_id)
                self.tooltip_pos = (mouse[0] + 16, mouse[1] + 12)

    def _draw_toggle(self, screen):
        pygame.draw.rect(screen, (10, 20, 35), (60, 118, 330, 56), border_radius=16)
        pygame.draw.rect(screen, (90, 150, 210), (60, 118, 330, 56), 2, border_radius=16)

        def draw_tab(rect, label, active):
            bg = (35, 60, 90) if active else (18, 32, 52)
            bd = (255, 220, 120) if active else (60, 95, 135)
            pygame.draw.rect(screen, bg, rect, border_radius=12)
            pygame.draw.rect(screen, bd, rect, 2, border_radius=12)
            t = self.font.render(label, True, (235, 245, 255))
            screen.blit(t, t.get_rect(center=rect.center))

        if self.mode == 1:
            draw_tab(self.toggle_p1, "P1", True)
        else:
            draw_tab(self.toggle_p1, "P1", self.active_player == 1)
            draw_tab(self.toggle_p2, "P2", self.active_player == 2)

    def _draw_tooltip(self, screen):
        if not self.tooltip:
            return
        text = self.small.render(self.tooltip, True, (240, 245, 255))
        pad = 10
        w = text.get_width() + pad * 2
        h = text.get_height() + pad * 2
        x, y = self.tooltip_pos
        x = clamp(x, 10, self.app.width - w - 10)
        y = clamp(y, 10, self.app.height - h - 10)

        box = pygame.Rect(x, y, w, h)
        pygame.draw.rect(screen, (0, 0, 0), box, border_radius=12)
        pygame.draw.rect(screen, (120, 200, 255), box, 2, border_radius=12)
        screen.blit(text, (x + pad, y + pad))

    def draw(self, screen):
        draw_cover(screen, self.bg, self.app.width, self.app.height)

        overlay = pygame.Surface((self.app.width, self.app.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 95))
        screen.blit(overlay, (0, 0))

        title = self.h1.render("Select Fish", True, self.app.theme["text"])
        screen.blit(title, (70, 55))

        hint = self.small.render(
            f"Progress: unlocked map {self.max_map} | Available fish: {self.allowed}/12",
            True,
            self.app.theme["muted"]
        )
        screen.blit(hint, (70, 95))

        self._draw_toggle(screen)

        for card in self.cards:
            selected = (card.fish_id == self.sel_p1) or (self.mode == 2 and card.fish_id == self.sel_p2)
            active = (
                self.mode == 2 and (
                    (self.active_player == 1 and card.fish_id == self.sel_p1) or
                    (self.active_player == 2 and card.fish_id == self.sel_p2)
                )
            )
            subtitle = self._unlock_hint(card.fish_id)
            card.draw(screen, self.font, self.small, selected=selected, active=active, subtitle=subtitle)

        p1 = self.small.render(f"P1: {self.sel_p1}", True, (230, 240, 255))
        screen.blit(p1, (70, 635))
        if self.mode == 2:
            p2 = self.small.render(f"P2: {self.sel_p2}", True, (230, 240, 255))
            screen.blit(p2, (220, 635))

        self.btn_back.draw(screen)
        self.btn_start.draw(screen)
        self._draw_tooltip(screen)
