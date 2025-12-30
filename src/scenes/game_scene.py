# src/scenes/game_scene.py
import pygame

from src.core.scene import Scene
from src.world.camera import Camera
from src.entities.player import PlayerFish
from src.entities.floating_text import FloatingText
from src.world.spawner import Spawner
from src.ui.hud import HUD
from src.entities.item_drop import DropSpawner


class GameScene(Scene):
    TARGET_POINTS = 226

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

        self.bg = self.app.assets.image(self.map["bg"]) if self.map.get("bg") else None

        # ---------- Camera ----------
        self.camera = Camera(self.app.w, self.app.h, self.world_w, self.world_h)

        # ---------- Fonts + HUD ----------
        self.font_big = self.app.assets.font(None, 26)
        self.font_small = self.app.assets.font(None, 18)
        self.hud = HUD(self.font_big, self.font_small)

        # ---------- Players ----------
        p1_fish = self.app.save.data.get("selected_fish_p1", "fish01")
        p2_fish = self.app.save.data.get("selected_fish_p2", "fish02")

        self.players: list[PlayerFish] = []

        self.players.append(
            PlayerFish(
                pos=(self.world_w / 2, self.world_h / 2),
                controls={
                    "up": pygame.K_w,
                    "down": pygame.K_s,
                    "left": pygame.K_a,
                    "right": pygame.K_d,
                },
                fish_folder=f"assets/fish/player/{p1_fish}",
            )
        )
        self.players[0].points = 5

        if int(self.app.runtime.get("mode", 1)) == 2:
            self.players.append(
                PlayerFish(
                    pos=(self.world_w / 2 + 120, self.world_h / 2),
                    controls={
                        "up": pygame.K_UP,
                        "down": pygame.K_DOWN,
                        "left": pygame.K_LEFT,
                        "right": pygame.K_RIGHT,
                    },
                    fish_folder=f"assets/fish/player/{p2_fish}",
                )
            )
            self.players[1].points = 5

        # ---------- Prey ----------
        map_id = int(self.map.get("id", 1))
        if map_id == 1:
            prey_values = [2, 3, 5, 10, 15, 30, 50, 100]
        elif map_id == 2:
            prey_values = [3, 5, 10, 15, 30, 50, 100, 150]
        else:
            prey_values = [5, 10, 15, 30, 50, 100, 150, 200]

        self.preys = []
        self.spawner = Spawner(self.world_w, self.world_h, prey_values)

        # ---------- Drops ----------
        self.drops = []
        self.drop_spawner = DropSpawner(self.world_w, self.world_h)

        # ---------- Misc ----------
        self.floating: list[FloatingText] = []
        self.elapsed = 0.0

        self._status_icons = {
            "x2": "assets/items/x2diem.png",
            "shield1": "assets/items/thuong1.png",
            "shield2": "assets/items/thuong2.png",
            "shield3": "assets/items/thuong3.png",
            "heart": "assets/items/thuong.png",
        }

        # ✅ (Optional) đảm bảo camera đúng ngay từ frame đầu (spawn không lệch)
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

        avg_pts = (
            int((self.players[0].points + self.players[1].points) / 2)
            if len(self.players) == 2
            else int(self.players[0].points)
        )

        # ✅ ---- Camera (PHẢI update trước khi spawn prey) ----
        self.camera.follow(self.players[0].pos)
        self.camera.update(dt)

        # ---- Preys ----
        for prey in self.preys:
            try:
                prey.update(dt, self.world_w, self.world_h, players=self.players)
            except TypeError:
                prey.update(dt, self.world_w, self.world_h)

        if len(self.preys) < 90:
            map_id = int(self.map.get("id", 1))
            self.spawner.update(dt, avg_pts, self.preys, self.camera, map_id=map_id)

        # ---- Drops ----
        map_id = int(self.map.get("id", 1))
        self.drop_spawner.update(dt, self.drops, map_id, avg_pts)
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
        r = 18 * float(getattr(p, "scale", 1.0))
        return pygame.Rect(p.pos.x - r, p.pos.y - r, r * 2, r * 2)

    def _handle_collisions(self):
        for p in self.players:
            p_rect = self._player_rect(p)

            for prey in self.preys:
                if not prey.alive:
                    continue
                if not p_rect.colliderect(prey.rect()):
                    continue

                if prey.points <= int(p.points * 1.02):
                    prey.alive = False
                    gained = p.add_points(prey.points)
                    self.floating.append(FloatingText(prey.pos, f"+{gained}"))
                else:
                    p.hit()
                    self.camera.shake(6, 0.15)

            for d in self.drops:
                if not d.alive:
                    continue
                if not p_rect.colliderect(d.rect()):
                    continue

                d.alive = False
                if str(d.kind).startswith("ob"):
                    p.hit()
                    self.camera.shake(8, 0.2)
                    self.floating.append(FloatingText(d.pos, "-1 ❤️"))
                    continue

                p.apply_item(d.kind)

    # =========================
    # End conditions
    # =========================
    def _check_end_conditions(self):
        if self.players[0].points >= self.TARGET_POINTS:
            from src.scenes.victory import VictoryScene
            self.app.scenes.set_scene(
                VictoryScene(self.app),
                map_id=int(self.map.get("id", 1)),
                points=int(self.players[0].points),
                time_alive=float(self.elapsed),
            )

        if self.players[0].lives <= 0:
            from src.scenes.game_over import GameOverScene
            self.app.scenes.set_scene(
                GameOverScene(self.app),
                map_id=int(self.map.get("id", 1)),
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

        # ✅ gọi đúng tham số (assets + font)
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
