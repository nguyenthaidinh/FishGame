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
    MAP_TARGETS = {1: 500, 2: 3000, 3: 5000}

    # =========================
    # Enter
    # =========================
    def on_enter(self, map_data=None, **kwargs):
        self.map = map_data or {
            "id": 1,
            "bg": None,
            "world_size": [2400, 1344],
            "name": "Map 1",
        }

        self.world_w, self.world_h = self.map.get("world_size", [2400, 1344])
        self.map_id = int(self.map.get("id", 1))
        self.TARGET_POINTS = self.MAP_TARGETS.get(self.map_id, 300)

        # ===== mode: 1P/2P =====
        self.mode = int(self.app.runtime.get("mode", 1))
        self.mode = 2 if self.mode == 2 else 1

        # ===== Background (cache scaled 1 lần) =====
        self.bg = self.app.assets.image(self.map["bg"]) if self.map.get("bg") else None
        self.bg_world = (
            pygame.transform.smoothscale(self.bg, (self.world_w, self.world_h))
            if self.bg
            else None
        )

        # ===== Camera =====
        self.camera = Camera(self.app.width, self.app.height, self.world_w, self.world_h)

        # ===== Fonts + HUD =====
        self.font_big = self.app.assets.font(None, 26)
        self.font_small = self.app.assets.font(None, 18)
        self.hud = HUD(self.font_big, self.font_small)

        # ===== Players =====
        self._ensure_players()

        # ===== Enemies / Drops =====
        self.preys = []
        self.predators = []
        self.spawner = Spawner(self.world_w, self.world_h)

        self.drops = []
        self.drop_spawner = DropSpawner(self.world_w, self.world_h)

        self.floating: List[FloatingText] = []
        self.elapsed = 0.0

        # ===== Spawn caps theo map/mode (EASY BALANCE) =====
        if self.map_id == 1:
            self.max_preys = 22 if self.mode == 1 else 28
            self.max_predators = 2 if self.mode == 1 else 3
        elif self.map_id == 2:
            self.max_preys = 28 if self.mode == 1 else 36
            self.max_predators = 3 if self.mode == 1 else 4
        else:  # map3+
            self.max_preys = 34 if self.mode == 1 else 44
            self.max_predators = 4 if self.mode == 1 else 5

        # ===== Camera init =====
        self._camera_follow_players()
        self.camera.update(0.0)

        # ===== BGM =====
        if self.app.sound_on:
            try:
                pygame.mixer.music.load("assets/sound/map.mp3")
                pygame.mixer.music.set_volume(0.35)
                pygame.mixer.music.play(-1)
            except Exception as e:
                print("[WARN] BGM load failed:", e)

        # ===== Pause Button =====
        self.btn_pause = ImageButton(
            "assets/ui/button/pause.png",
            (self.app.width - 42, 32),
            self._pause_game,
            scale=0.08,
            hover_scale=1.15
        )

    # =========================
    # Create/ensure players
    # =========================
    def _ensure_players(self):
        p1_fish = self.app.save.data.get("selected_fish_p1", "fish01")
        p2_fish = self.app.save.data.get("selected_fish_p2", "fish02")

        # 1P: arrows
        p1_controls = {
            "up": pygame.K_UP,
            "down": pygame.K_DOWN,
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
        }

        # 2P: WASD
        p2_controls = {
            "up": pygame.K_w,
            "down": pygame.K_s,
            "left": pygame.K_a,
            "right": pygame.K_d,
        }

        p1 = PlayerFish(
            pos=(self.world_w / 2 - 80, self.world_h / 2),
            controls=p1_controls,
            fish_folder=f"assets/fish/player/{p1_fish}",
            player_id=1,
        )
        p1.points = 5

        players = [p1]

        if self.mode == 2:
            p2 = PlayerFish(
                pos=(self.world_w / 2 + 80, self.world_h / 2),
                controls=p2_controls,
                fish_folder=f"assets/fish/player/{p2_fish}",
                player_id=2,
            )
            p2.points = 5
            players.append(p2)

        self.players: List[PlayerFish] = players
        self.app.runtime["players"] = players

    # =========================
    # Helpers
    # =========================
    def _player_radius(self, p: PlayerFish) -> float:
        img = p.sprite.get_image(scale=(p.scale / p.render_div))
        return max(img.get_width(), img.get_height()) * 0.35

    def _player_rect(self, p: PlayerFish) -> pygame.Rect:
        r = self._player_radius(p)
        return pygame.Rect(int(p.pos.x - r), int(p.pos.y - r), int(r * 2), int(r * 2))

    def _camera_follow_players(self):
        if len(self.players) >= 2:
            center = (self.players[0].pos + self.players[1].pos) / 2
            self.camera.follow(center)
        else:
            self.camera.follow(self.players[0].pos)

    def _team_points(self) -> int:
        return int(sum(p.points for p in self.players))

    def _all_dead(self) -> bool:
        return all(p.lives <= 0 for p in self.players)

    # DESPAWN xa camera để cá không tích tụ mãi
    def _despawn_far_entities(self):
        view_l = self.camera.offset.x
        view_r = self.camera.offset.x + self.camera.sw
        view_t = self.camera.offset.y
        view_b = self.camera.offset.y + self.camera.sh

        pad = 520  # càng lớn càng ít despawn (520 là cân bằng)
        left = view_l - pad
        right = view_r + pad
        top = view_t - pad
        bottom = view_b + pad

        for e in self.preys:
            if getattr(e, "alive", True):
                if e.pos.x < left or e.pos.x > right or e.pos.y < top or e.pos.y > bottom:
                    e.alive = False

        for e in self.predators:
            if getattr(e, "alive", True):
                if e.pos.x < left or e.pos.x > right or e.pos.y < top or e.pos.y > bottom:
                    e.alive = False

    # =========================
    # Pause
    # =========================
    def _pause_game(self):
        try:
            pygame.mixer.music.fadeout(300)
        except Exception:
            pass
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

        # players
        for p in self.players:
            if p.lives > 0:
                p.update(dt)

            r = self._player_radius(p)
            p.pos.x = max(r, min(self.world_w - r, p.pos.x))
            p.pos.y = max(r, min(self.world_h - r, p.pos.y))

        # camera follow
        self._camera_follow_players()
        self.camera.update(dt)

        # difficulty points:
        # - 1P: dùng điểm player[0]
        # - 2P: dùng trung bình team để spawn hợp lý hơn
        if self.mode == 1:
            diff_pts = int(self.players[0].points)
        else:
            diff_pts = max(1, int(self._team_points() / max(1, len(self.players))))

        # update prey
        for prey in self.preys:
            prey.update(dt, self.world_w, self.world_h, players=self.players)

        # update predator
        for pr in self.predators:
            pr.update(dt, self.world_w, self.world_h, players=self.players)

        # spawn: theo TỔNG cap (tránh OR spawn miết)
        total_now = len(self.preys) + len(self.predators)
        total_cap = self.max_preys + self.max_predators

        if total_now < total_cap:
            self.spawner.update(
                dt,
                player_points=diff_pts,
                preys=self.preys,
                predators=self.predators,
                camera=self.camera,
                map_id=self.map_id
            )

        # drops
        self.drop_spawner.update(dt, self.drops, self.map_id, diff_pts)
        for d in self.drops:
            d.update(dt, self.world_w, self.world_h)

        # collision
        self._handle_collisions()

        # despawn xa camera (giảm đông dần theo thời gian)
        self._despawn_far_entities()

        # cleanup
        self.preys = [e for e in self.preys if getattr(e, "alive", True)]
        self.predators = [e for e in self.predators if getattr(e, "alive", True)]
        self.drops = [d for d in self.drops if d.alive]
        self.floating = [ft for ft in self.floating if ft.update(dt)]

        self._check_end_conditions()

    # =========================
    # Collision
    # =========================
    def _handle_collisions(self):
        for p in self.players:
            if p.lives <= 0:
                continue

            p_rect = self._player_rect(p)

            # ===== prey collisions =====
            for prey in self.preys:
                if getattr(prey, "alive", True) and p_rect.colliderect(prey.rect()):
                    if prey.points <= int(p.points * 1.02):
                        prey.alive = False
                        gained = p.add_points(prey.points)
                        self.floating.append(FloatingText(prey.pos, f"+{gained}"))
                    else:
                        p.hit()
                        self.camera.shake(6, 0.15)

            # ===== predator collisions (EASY FAIR RULE) =====
            for pr in self.predators:
                if not getattr(pr, "alive", True):
                    continue
                if not p_rect.colliderect(pr.rect()):
                    continue

                # ✅ đủ lớn thì ăn predator (công bằng)
                if pr.points <= int(p.points * 0.92):
                    pr.alive = False
                    gained = p.add_points(pr.points)
                    self.floating.append(FloatingText(pr.pos, f"+{gained}"))
                    self.camera.shake(6, 0.12)
                else:
                    p.hit()
                    self.camera.shake(10, 0.22)

            # ===== drops collisions =====
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
        if self._team_points() >= self.TARGET_POINTS:
            try:
                pygame.mixer.music.fadeout(800)
            except Exception:
                pass
            from src.scenes.victory import VictoryScene
            self.app.scenes.set_scene(
                VictoryScene(self.app),
                map_id=self.map_id,
                points=self._team_points(),
                time_alive=self.elapsed,
            )
            return

        if self.mode == 1:
            if self.players[0].lives <= 0:
                try:
                    pygame.mixer.music.fadeout(800)
                except Exception:
                    pass
                from src.scenes.game_over import GameOverScene
                self.app.scenes.set_scene(
                    GameOverScene(self.app),
                    map_id=self.map_id,
                    points=self._team_points(),
                    time_alive=self.elapsed,
                )
        else:
            if self._all_dead():
                try:
                    pygame.mixer.music.fadeout(800)
                except Exception:
                    pass
                from src.scenes.game_over import GameOverScene
                self.app.scenes.set_scene(
                    GameOverScene(self.app),
                    map_id=self.map_id,
                    points=self._team_points(),
                    time_alive=self.elapsed,
                )

    # =========================
    # Draw
    # =========================
    def draw(self, screen):
        screen.fill((8, 30, 55))

        if self.bg_world:
            screen.blit(self.bg_world, (-self.camera.offset.x, -self.camera.offset.y))

        for d in self.drops:
            d.draw(screen, self.camera, self.app.assets)

        for prey in self.preys:
            prey.draw(screen, self.camera, self.app.assets, self.font_small)

        for pr in self.predators:
            pr.draw(screen, self.camera, self.font_small)

        for p in self.players:
            if p.lives > 0:
                p.draw(screen, self.camera)

        for ft in self.floating:
            ft.draw(screen, self.camera, self.font_small)

        self.hud.draw(
            screen,
            assets=self.app.assets,
            lives=self.players[0].lives,
            points=self._team_points(),
            elapsed=self.elapsed,
            target=self.TARGET_POINTS,
            player=self.players[0],
            map_name=self.map.get("name", ""),
        )

        self.btn_pause.draw(screen)
