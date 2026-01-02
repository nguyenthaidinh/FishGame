# src/scenes/game_scene.py
import pygame
from typing import List

from src.core.scene import Scene
from src.world.camera import Camera
from src.entities.player import PlayerFish
from src.entities.floating_text import FloatingText
from src.world.spawner import Spawner
from src.entities.item_drop import DropSpawner
from src.ui.hud import HUD
from src.ui.image_button import ImageButton


class GameScene(Scene):
    MAP_TARGETS = {
        1: 500,
        2: 3000,
        3: 5000,
    }

    # =========================
    # Enter
    # =========================
    def on_enter(self, map_data=None, **kwargs):
        # ---------- MAP ----------
        self.map = map_data or {
            "id": 1,
            "bg": None,
            "world_size": [3000, 1800],
            "name": "Map 1",
        }

        self.world_w, self.world_h = self.map["world_size"]
        self.map_id = int(self.map.get("id", 1))
        self.TARGET_POINTS = self.MAP_TARGETS.get(self.map_id, 300)

        self.bg = (
            self.app.assets.image(self.map["bg"])
            if self.map.get("bg")
            else None
        )

        # ---------- CAMERA ----------
        self.camera = Camera(
            self.app.width,
            self.app.height,
            self.world_w,
            self.world_h
        )

        # ---------- HUD ----------
        self.font_big = self.app.assets.font(None, 26)
        self.font_small = self.app.assets.font(None, 18)
        self.hud = HUD(self.font_big, self.font_small)

        # ---------- PLAYER MODE ----------
        mode = self.app.runtime.get("mode", 1)

        self.players: List[PlayerFish] = []

        if mode == 2:
            # ===== PLAYER 1 =====
            p1_fish = self.app.save.data.get(
                "selected_fish_p1", "fish01"
            )
            p1 = PlayerFish(
                pos=(self.world_w / 2 - 80, self.world_h / 2),
                controls={
                    "up": pygame.K_w,
                    "down": pygame.K_s,
                    "left": pygame.K_a,
                    "right": pygame.K_d,
                },
                fish_folder=f"assets/fish/player/{p1_fish}",
                player_id=1
            )

            # ===== PLAYER 2 =====
            p2_fish = self.app.save.data.get(
                "selected_fish_p2", "fish02"
            )
            p2 = PlayerFish(
                pos=(self.world_w / 2 + 80, self.world_h / 2),
                controls={
                    "up": pygame.K_UP,
                    "down": pygame.K_DOWN,
                    "left": pygame.K_LEFT,
                    "right": pygame.K_RIGHT,
                },
                fish_folder=f"assets/fish/player/{p2_fish}",
                player_id=2
            )

            self.players = [p1, p2]

        else:
            # ===== SINGLE PLAYER =====
            p1_fish = self.app.save.data.get(
                "selected_fish_p1", "fish01"
            )
            p1 = PlayerFish(
                pos=(self.world_w / 2, self.world_h / 2),
                controls={
                    "up": pygame.K_w,
                    "down": pygame.K_s,
                    "left": pygame.K_a,
                    "right": pygame.K_d,
                },
                fish_folder=f"assets/fish/player/{p1_fish}",
                player_id=1
            )
            self.players = [p1]

        self.app.runtime["players"] = self.players

        # ---------- ENEMIES / DROPS ----------
        self.preys = []
        self.spawner = Spawner(self.world_w, self.world_h)

        self.drops = []
        self.drop_spawner = DropSpawner(self.world_w, self.world_h)

        self.floating: List[FloatingText] = []
        self.elapsed = 0.0

        # ---------- CAMERA START ----------
        self.camera.follow(self.players[0].pos)
        self.camera.update(0.0)

        # ---------- BGM ----------
        if self.app.sound_on:
            pygame.mixer.music.load("assets/sound/bgm_game.mp3")
            pygame.mixer.music.set_volume(0.35)
            pygame.mixer.music.play(-1)

        # ---------- PAUSE BUTTON ----------
        self.btn_pause = ImageButton(
            "assets/ui/button/pause.png",
            (self.app.width - 42, 32),
            self._pause_game,
            scale=0.08,
            hover_scale=1.15
        )

    # =========================
    # Pause
    # =========================
    def _pause_game(self):
        pygame.mixer.music.fadeout(300)
        from src.scenes.pause import PauseScene
        self.app.scenes.set_scene(PauseScene(self.app, self))

    # =========================
    # Events
    # =========================
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._pause_game()
        self.btn_pause.handle_event(event)

    # =========================
    # Update
    # =========================
    def update(self, dt):
        self.elapsed += dt

        for p in self.players:
            p.update(dt)
            p.pos.x = max(0, min(self.world_w, p.pos.x))
            p.pos.y = max(0, min(self.world_h, p.pos.y))

        avg_pts = int(sum(p.points for p in self.players) / len(self.players))

        # CAMERA FOLLOW
        if len(self.players) == 2:
            center = (self.players[0].pos + self.players[1].pos) / 2
            self.camera.follow(center)
        else:
            self.camera.follow(self.players[0].pos)

        self.camera.update(dt)

        for prey in self.preys:
            prey.update(dt, self.world_w, self.world_h, players=self.players)

        if len(self.preys) < 90:
            self.spawner.update(
                dt, avg_pts, self.preys, self.camera, map_id=self.map_id
            )

        self.drop_spawner.update(dt, self.drops, self.map_id, avg_pts)
        for d in self.drops:
            d.update(dt, self.world_w, self.world_h)

        self._handle_collisions()

        self.preys = [p for p in self.preys if p.alive]
        self.drops = [d for d in self.drops if d.alive]
        self.floating = [ft for ft in self.floating if ft.update(dt)]

        self._check_end_conditions()

    # =========================
    # Collision
    # =========================
    def _player_rect(self, p):
        img = p.sprite.get_image(scale=p.scale / p.render_div)
        r = max(img.get_width(), img.get_height()) * 0.35
        return pygame.Rect(p.pos.x - r, p.pos.y - r, r * 2, r * 2)

    def _handle_collisions(self):
        for p in self.players:
            p_rect = self._player_rect(p)

            for prey in self.preys:
                if prey.alive and p_rect.colliderect(prey.rect()):
                    if prey.points <= int(p.points * 1.02):
                        prey.alive = False
                        gained = p.add_points(prey.points)
                        self.floating.append(
                            FloatingText(prey.pos, f"P{p.player_id} +{gained}")
                        )
                    else:
                        p.hit()
                        self.camera.shake(6, 0.15)

            for d in self.drops:
                if d.alive and p_rect.colliderect(d.rect()):
                    d.alive = False
                    if str(d.kind).startswith("ob"):
                        p.hit()
                        self.camera.shake(8, 0.2)
                    else:
                        p.apply_item(d.kind)

    # =========================
    # End game
    # =========================
    def _check_end_conditions(self):
        for p in self.players:
            if p.points >= self.TARGET_POINTS:
                pygame.mixer.music.fadeout(800)
                from src.scenes.victory import VictoryScene
                self.app.scenes.set_scene(
                    VictoryScene(self.app),
                    map_id=self.map_id,
                    points=int(p.points),
                    time_alive=self.elapsed,
                )
                return

            if p.lives <= 0:
                pygame.mixer.music.fadeout(800)
                from src.scenes.game_over import GameOverScene
                self.app.scenes.set_scene(
                    GameOverScene(self.app),
                    map_id=self.map_id,
                    points=int(p.points),
                    time_alive=self.elapsed,
                )
                return

    # =========================
    # Draw
    # =========================
    def draw(self, screen):
        screen.fill((8, 30, 55))

        if self.bg:
            bg = pygame.transform.smoothscale(
                self.bg, (self.world_w, self.world_h)
            )
            screen.blit(
                bg,
                (-self.camera.offset.x, -self.camera.offset.y)
            )

        for d in self.drops:
            d.draw(screen, self.camera, self.app.assets)

        for prey in self.preys:
            prey.draw(screen, self.camera, self.app.assets, self.font_small)

        for p in self.players:
            p.draw(screen, self.camera)

        for ft in self.floating:
            ft.draw(screen, self.camera, self.font_small)

        # ===== HUD (HIỆN PLAYER 1) =====
        self.hud.draw(
            screen,
            assets=self.app.assets,
            lives=self.players[0].lives,
            points=int(self.players[0].points),
            elapsed=self.elapsed,
            target=self.TARGET_POINTS,
            player=self.players[0],
            map_name=self.map.get("name", ""),
        )

        self.btn_pause.draw(screen)
