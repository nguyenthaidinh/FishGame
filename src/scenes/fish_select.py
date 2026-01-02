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

        # ⚠️ nếu thiếu sprite file -> sẽ crash
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

    def draw(self, screen, font_name, selected_p1=False, selected_p2=False, active=False):
        lift = int(6 * self.hover)
        r = self.rect.copy()
        r.y -= lift

        # base
        pygame.draw.rect(screen, (12, 24, 40), r, border_radius=16)

        # border theo trạng thái
        border = (90, 150, 210)
        if selected_p1 and selected_p2:
            border = (255, 220, 120)      # cả 2 chọn trùng (vàng)
        elif selected_p1:
            border = (120, 255, 160)      # P1 (xanh)
        elif selected_p2:
            border = (255, 140, 140)      # P2 (đỏ)
        if active:
            # active glow nhẹ
            pygame.draw.rect(screen, (120, 200, 255), r.inflate(8, 8), 2, border_radius=18)

        pygame.draw.rect(screen, border, r, 2, border_radius=16)

        img = self.sprite.get_image(scale=0.82)
        screen.blit(img, img.get_rect(center=r.center))

        name_s = font_name.render(self.name, True, (235, 245, 255))
        screen.blit(name_s, (r.x + 16, r.y + r.h - 32))

        # tag nhỏ P1/P2
        if selected_p1:
            t = font_name.render("P1", True, (15, 20, 25))
            tag = pygame.Surface((38, 22), pygame.SRCALPHA)
            pygame.draw.rect(tag, (120, 255, 160, 220), tag.get_rect(), border_radius=8)
            tag.blit(t, t.get_rect(center=tag.get_rect().center))
            screen.blit(tag, (r.x + 12, r.y + 12))

        if selected_p2:
            t = font_name.render("P2", True, (15, 20, 25))
            tag = pygame.Surface((38, 22), pygame.SRCALPHA)
            pygame.draw.rect(tag, (255, 140, 140, 220), tag.get_rect(), border_radius=8)
            tag.blit(t, t.get_rect(center=tag.get_rect().center))
            screen.blit(tag, (r.right - 50, r.y + 12))


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
        self.small = self.app.assets.font("assets/fonts/Baloo2-Bold.ttf", 18)

        # mode (nếu Lio đã chọn 1P/2P ở mode_select)
        # - nếu chưa có, mặc định 1P
        self.mode = int(self.app.runtime.get("mode", 1))

        # selections
        self.sel_p1 = self.app.save.data.get("selected_fish_p1", "fish01")
        self.sel_p2 = self.app.save.data.get("selected_fish_p2", "fish02")

        # ai đang chọn? (0=P1, 1=P2)
        self.active_player = 0

        # ===== GRID =====
        self.cards = []
        margin_x = 70
        top = 130
        cols = 4
        gap = 18

        card_w = (self.app.width - margin_x * 2 - gap * (cols - 1)) // cols
        card_h = 170

        items = list(self.fish_db.items())
        for idx, (fish_id, meta) in enumerate(items):
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
            self._go_back,          # ✅ FIX: không dùng self.app.back
            scale=0.12,
            hover_scale=1.15
        )

        self.btn_start = ImageButton(
            "assets/ui/button/start.png",
            (cx, 60),
            self._start,
            scale=0.2,
            scale_x=1.6,
            scale_y=1.0,
            hover_scale=1.15
        )

    # =========================
    # Back (✅ FIX)
    # =========================
    def _go_back(self):
        # quay về map_select (đúng flow của Lio)
        from src.scenes.map_select import MapSelectScene
        self.app.scenes.set_scene(MapSelectScene(self.app))

    # =========================
    # Start game
    # =========================
    def _start(self):
        from src.scenes.game_scene import GameScene
        from src.entities.player import PlayerFish

        # save selections
        self.app.save.data["selected_fish_p1"] = self.sel_p1
        self.app.save.data["selected_fish_p2"] = self.sel_p2
        self.app.save.save()

        map_data = self.app.runtime.get("map")
        if not map_data:
            with open("data/maps/map1.json", "r", encoding="utf-8") as f:
                map_data = json.load(f)
            self.app.runtime["map"] = map_data

        # ✅ build players runtime theo mode
        world_w, world_h = map_data.get("world_size", [3200, 1800])

        p1 = PlayerFish(
            pos=(world_w / 2 - 80, world_h / 2),
            controls={"up": pygame.K_w, "down": pygame.K_s, "left": pygame.K_a, "right": pygame.K_d},
            fish_folder=f"assets/fish/player/{self.sel_p1}",
        )
        p1.points = 5

        players = [p1]

        if self.mode == 2:
            p2 = PlayerFish(
                pos=(world_w / 2 + 80, world_h / 2),
                controls={"up": pygame.K_UP, "down": pygame.K_DOWN, "left": pygame.K_LEFT, "right": pygame.K_RIGHT},
                fish_folder=f"assets/fish/player/{self.sel_p2}",
            )
            p2.points = 5
            players.append(p2)

        self.app.runtime["players"] = players

        self.app.scenes.set_scene(GameScene(self.app), map_data=map_data)

    # =========================
    # Events
    # =========================
    def handle_event(self, event):
        self.btn_back.handle_event(event)
        self.btn_start.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._go_back()

            # ✅ TAB đổi người đang chọn (chỉ khi mode 2P)
            if self.mode == 2 and event.key == pygame.K_TAB:
                self.active_player = 1 - self.active_player

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # click chọn cá
            for card in self.cards:
                if card.hit(event.pos):
                    if self.mode == 2:
                        if self.active_player == 0:
                            self.sel_p1 = card.fish_id
                        else:
                            self.sel_p2 = card.fish_id
                    else:
                        self.sel_p1 = card.fish_id

            # click vào text “P1/P2” để đổi active (nhẹ nhàng)
            if self.mode == 2:
                if self._p1_label_rect().collidepoint(event.pos):
                    self.active_player = 0
                elif self._p2_label_rect().collidepoint(event.pos):
                    self.active_player = 1

    def update(self, dt):
        mouse = pygame.mouse.get_pos()
        for card in self.cards:
            card.update(dt, mouse)

    # =========================
    # UI helper rects
    # =========================
    def _p1_label_rect(self):
        return pygame.Rect(70, 92, 260, 28)

    def _p2_label_rect(self):
        return pygame.Rect(340, 92, 260, 28)

    def draw(self, screen):
        draw_cover(screen, self.bg, self.app.width, self.app.height)

        overlay = pygame.Surface((self.app.width, self.app.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 90))
        screen.blit(overlay, (0, 0))

        title = self.h1.render("Select Fish", True, self.app.theme["text"])
        screen.blit(title, (70, 45))

        # =========================
        # ✅ status chọn P1/P2
        # =========================
        if self.mode == 1:
            s = self.small.render(f"P1: {self.sel_p1}", True, (220, 240, 255))
            screen.blit(s, (70, 95))
        else:
            # P1 label
            p1_bg = pygame.Surface((260, 28), pygame.SRCALPHA)
            pygame.draw.rect(p1_bg,
                             (120, 255, 160, 230) if self.active_player == 0 else (40, 55, 75, 200),
                             p1_bg.get_rect(), border_radius=10)
            t1 = self.small.render(f"P1: {self.sel_p1}  (WASD)", True, (15, 20, 25) if self.active_player == 0 else (220, 240, 255))
            p1_bg.blit(t1, t1.get_rect(midleft=(12, 14)))
            screen.blit(p1_bg, (70, 92))

            # P2 label
            p2_bg = pygame.Surface((260, 28), pygame.SRCALPHA)
            pygame.draw.rect(p2_bg,
                             (255, 140, 140, 230) if self.active_player == 1 else (40, 55, 75, 200),
                             p2_bg.get_rect(), border_radius=10)
            t2 = self.small.render(f"P2: {self.sel_p2}  (ARROWS)", True, (15, 20, 25) if self.active_player == 1 else (220, 240, 255))
            p2_bg.blit(t2, t2.get_rect(midleft=(12, 14)))
            screen.blit(p2_bg, (340, 92))

            hint = self.small.render("TAB to switch selection (P1/P2)", True, (190, 210, 235))
            screen.blit(hint, (620, 95))

        # =========================
        # cards
        # =========================
        for card in self.cards:
            card.draw(
                screen,
                self.font,
                selected_p1=(card.fish_id == self.sel_p1),
                selected_p2=(self.mode == 2 and card.fish_id == self.sel_p2),
                active=(self.mode == 2 and (
                    (self.active_player == 0 and card.fish_id == self.sel_p1) or
                    (self.active_player == 1 and card.fish_id == self.sel_p2)
                ))
            )

        self.btn_back.draw(screen)
        self.btn_start.draw(screen)
