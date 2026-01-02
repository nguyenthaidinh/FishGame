# src/scenes/game_scene.py
import pygame
from typing import List

from src.core.scene import Scene
from src.world.camera import Camera
from src.entities.player import PlayerFish
from src.entities.floating_text import FloatingText
from src.world.spawner import Spawner
from src.ui.hud import HUD
from src.entities.item_drop import DropSpawner


class GameScene(Scene):
    # =========================
    # ĐIỂM QUA MÀN THEO MAP
    # =========================
    MAP_TARGETS = {
        1: 500,   # Map 1
        2: 3000,   # Map 2
        3: 5000,   # Map 3
    }

    # =========================
    # Enter
    # =========================
    def on_enter(self, map_data=None, **kwargs):
        # ---------- Map ----------
        self.map = map_data or {
            "id": 1,
            "bg": None,
            "world_size": [3000, 1800],
            "name": "Map 1",
        }
        self.world_w, self.world_h = self.map["world_size"]
        self.map_id = int(self.map.get("id", 1))

        # điểm cần để qua map hiện tại
        self.TARGET_POINTS = self.MAP_TARGETS.get(self.map_id, 300)

        self.bg = (
            self.app.assets.image(self.map["bg"])
            if self.map.get("bg")
            else None
        )

        # ---------- Camera ----------
        self.camera = Camera(
            self.app.width,
            self.app.height,
            self.world_w,
            self.world_h
        )

        # ---------- Fonts + HUD ----------
        self.font_big = self.app.assets.font(None, 26)
        self.font_small = self.app.assets.font(None, 18)
        self.hud = HUD(self.font_big, self.font_small)

        # ==================================================
        # PLAYERS (PERSISTENT – KHÔNG RESET)
        # ==================================================
        if "players" not in self.app.runtime:
            p1_fish = self.app.save.data.get("selected_fish_p1", "fish01")

            player = PlayerFish(
                pos=(self.world_w / 2, self.world_h / 2),
                controls={
                    "up": pygame.K_w,
                    "down": pygame.K_s,
                    "left": pygame.K_a,
                    "right": pygame.K_d,
                },
                fish_folder=f"assets/fish/player/{p1_fish}",
            )
            player.points = 5  # CHỈ SET 1 LẦN DUY NHẤT

            self.app.runtime["players"] = [player]

        # dùng lại player cũ
        self.players: List[PlayerFish] = self.app.runtime["players"]

        # reset vị trí khi sang map (KHÔNG reset điểm / size)
        for i, p in enumerate(self.players):
            p.pos.update(
                self.world_w / 2 + i * 120,
                self.world_h / 2
            )

        # ---------- Prey ----------
        self.preys = []
        self.spawner = Spawner(self.world_w, self.world_h)

        # ---------- Drops ----------
        self.drops = []
        self.drop_spawner = DropSpawner(self.world_w, self.world_h)

        # ---------- Misc ----------
        self.floating: List[FloatingText] = []
        self.elapsed = 0.0

        self._status_icons = {
            "x2": "assets/items/x2diem.png",
            "shield1": "assets/items/thuong1.png",
            "shield2": "assets/items/thuong2.png",
            "shield3": "assets/items/thuong3.png",
            "heart": "assets/items/thuong.png",
        }

        # đảm bảo camera đúng từ frame đầu
        self.camera.follow(self.players[0].pos)
        self.camera.update(0.0)

    # =========================
    # Events
    # =========================
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            from src.scenes.pause import PauseScene
            self.app.scenes.set_scene(PauseScene(self.app, self))

    # =========================
    # Update
    # =========================
    def update(self, dt):
        self.elapsed += dt

        # ---- Players ----
        for p in self.players:
            p.update(dt)
            p.pos.x = max(0, min(self.world_w, p.pos.x))
            p.pos.y = max(0, min(self.world_h, p.pos.y))

        avg_pts = int(self.players[0].points)

        # ---- Camera ----
        self.camera.follow(self.players[0].pos)
        self.camera.update(dt)

        # ---- Preys ----
        for prey in self.preys:
            try:
                prey.update(dt, self.world_w, self.world_h, players=self.players)
            except TypeError:
                prey.update(dt, self.world_w, self.world_h)

        if len(self.preys) < 90:
            self.spawner.update(dt, avg_pts, self.preys, self.camera, map_id=self.map_id)

        # ---- Drops ----
        self.drop_spawner.update(dt, self.drops, self.map_id, avg_pts)
        for d in self.drops:
            d.update(dt, self.world_w, self.world_h)

        # ---- Collisions ----
        self._handle_collisions()

        # ---- Cleanup ----
        self.preys = [p for p in self.preys if p.alive]
        self.drops = [d for d in self.drops if d.alive]
        self.floating = [ft for ft in self.floating if ft.update(dt)]

        # ---- End ----
        self._check_end_conditions()

    # =========================
    # Collision helpers
    # =========================
    def _player_rect(self, p: PlayerFish) -> pygame.Rect:
        img = p.sprite.get_image(scale=p.scale / p.render_div)
        r = max(img.get_width(), img.get_height()) * 0.35
        return pygame.Rect(
            p.pos.x - r,
            p.pos.y - r,
            r * 2,
            r * 2,
        )

    def _handle_collisions(self):
        for p in self.players:
            p_rect = self._player_rect(p)

            for prey in self.preys:
                if not prey.alive or not p_rect.colliderect(prey.rect()):
                    continue

                if prey.points <= int(p.points * 1.02):
                    prey.alive = False
                    gained = p.add_points(prey.points)
                    self.floating.append(FloatingText(prey.pos, f"+{gained}"))
                else:
                    p.hit()
                    self.camera.shake(6, 0.15)

            for d in self.drops:
                if not d.alive or not p_rect.colliderect(d.rect()):
                    continue

                d.alive = False
                if str(d.kind).startswith("ob"):
                    p.hit()
                    self.camera.shake(8, 0.2)
                    self.floating.append(FloatingText(d.pos, "-1 ❤️"))
                else:
                    p.apply_item(d.kind)

    # =========================
    # End conditions
    # =========================
    def _check_end_conditions(self):
        if self.players[0].points >= self.TARGET_POINTS:
            from src.scenes.victory import VictoryScene
            self.app.scenes.set_scene(
                VictoryScene(self.app),
                map_id=self.map_id,
                points=int(self.players[0].points),
                time_alive=float(self.elapsed),
            )

        if self.players[0].lives <= 0:
            from src.scenes.game_over import GameOverScene
            self.app.scenes.set_scene(
                GameOverScene(self.app),
                map_id=self.map_id,
                points=int(self.players[0].points),
                time_alive=float(self.elapsed),
            )

    # =========================
    # Draw
    # =========================
    def draw(self, screen):
        screen.fill((8, 30, 55))

        if self.bg:
            bg = pygame.transform.smoothscale(self.bg, (self.world_w, self.world_h))
            screen.blit(bg, (-self.camera.offset.x, -self.camera.offset.y))

        for d in self.drops:
            d.draw(screen, self.camera, self.app.assets)

        for prey in self.preys:
            prey.draw(screen, self.camera, assets=self.app.assets, font=self.font_small)

        for p in self.players:
            p.draw(screen, self.camera)
            pos = self.camera.world_to_screen(p.pos)
            label = self.font_small.render(str(p.points), True, (255, 255, 255))
            screen.blit(label, label.get_rect(center=(int(pos.x), int(pos.y - 34))))

        for ft in self.floating:
            ft.draw(screen, self.camera, self.font_small)

        self.hud.draw(
            screen,
            assets=self.app.assets,
            lives=self.players[0].lives,
            points=self.players[0].points,
            elapsed=self.elapsed,
            target=self.TARGET_POINTS,
            player=self.players[0],
            map_name=self.map.get("name", ""),
        )
