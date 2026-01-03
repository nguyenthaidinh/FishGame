# src/entities/ai_fish.py
import random
import pygame
from src.entities.animated_sprite import AnimatedSprite


class PredatorFish:
    """
    Cá săn mồi (AI độc lập) - Balanced:
    - scale theo points
    - aggro vừa phải (không nhìn quá xa)
    - chase có "burst" + nghỉ (đỡ dí liên tục)
    - slowdown xa -> vừa, gần -> nhanh
    - wander khi không thấy / khi đang nghỉ
    """

    def __init__(self, pos, fish_folder, points=80):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(0, 0)

        self.points = int(points)
        self.alive = True

        # =========================
        # SCALE + HITBOX theo points
        # =========================
        p = max(1, min(320, self.points))

        self.scale = 1.00 + (p / 320.0) * 0.95   # ~1.00 -> ~1.95
        self.scale = max(0.95, min(self.scale, 2.05))

        self.hit_radius = 18.0 * self.scale

        # =========================
        # SPEED theo points (GIẢM GẮT)
        # =========================
        # Trước: ~150 -> ~330 (gắt)
        # Mới:  ~125 -> ~245 (vẫn nguy hiểm nhưng né được)
        self.speed = 125.0 + (p / 320.0) * 120.0
        self.speed = max(120.0, min(self.speed, 255.0))

        # =========================
        # AGGRO theo points (GIẢM XA)
        # =========================
        # Trước: ~360 -> ~1200 (quá xa)
        # Mới:  ~260 -> ~540 (vừa)
        self.aggro_radius = 260.0 + min(280.0, p * 0.9)   # p=320 => +288 ~ 548
        self.aggro_radius = max(240.0, min(self.aggro_radius, 580.0))

        # =========================
        # Chase "burst" (đuổi 1 lúc rồi nghỉ)
        # =========================
        self._chase_on = 0.0
        self._chase_off = 0.0
        self._chase_on_cd = random.uniform(1.0, 1.6)   # thời gian đuổi
        self._chase_off_cd = random.uniform(0.5, 0.9)  # thời gian nghỉ

        # smoothing (quay đầu)
        self._steer_gain = 4.2  # càng cao càng bám
        self._wander_gain = 2.6

        # wander
        self._wander_t = 0.0
        self._wander_cd = random.uniform(0.9, 1.8)
        self._wander_dir = self._rand_dir()

        # sprite
        self.sprite = AnimatedSprite(
            [f"{fish_folder}/swim_01.png", f"{fish_folder}/swim_02.png"],
            fps=6
        )

    def _rand_dir(self):
        v = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        if v.length_squared() > 0.01:
            v = v.normalize()
        else:
            v = pygame.Vector2(1, 0)
        return v

    def rect(self):
        r = self.hit_radius
        return pygame.Rect(int(self.pos.x - r), int(self.pos.y - r), int(r * 2), int(r * 2))

    def _update_burst_state(self, dt):
        # đang đuổi
        if self._chase_on > 0:
            self._chase_on -= dt
            if self._chase_on <= 0:
                self._chase_off = self._chase_off_cd
                self._chase_off_cd = random.uniform(0.5, 0.9)
            return False  # không reset
        # đang nghỉ
        if self._chase_off > 0:
            self._chase_off -= dt
            if self._chase_off <= 0:
                self._chase_on = self._chase_on_cd
                self._chase_on_cd = random.uniform(1.0, 1.6)
            return False
        # init lần đầu
        self._chase_on = self._chase_on_cd
        return False

    def update(self, dt, world_w, world_h, players):
        if not self.alive:
            return

        # find nearest alive player
        target, best_d2 = None, 10**18
        for p in players or []:
            if getattr(p, "lives", 1) <= 0:
                continue
            d2 = (p.pos - self.pos).length_squared()
            if d2 < best_d2:
                best_d2 = d2
                target = p

        in_aggro = bool(target) and (best_d2 <= self.aggro_radius ** 2)

        if in_aggro:
            # bật burst state (đuổi / nghỉ)
            self._update_burst_state(dt)

            # nếu đang "nghỉ" thì chuyển sang wander nhẹ
            if self._chase_off > 0:
                desired = self._wander_dir * (self.speed * 0.55)
                self.vel += (desired - self.vel) * min(1.0, dt * self._wander_gain)
            else:
                v = target.pos - self.pos
                dist = v.length()

                if dist > 1:
                    dirv = v / dist

                    # ✅ slowdown hợp lý:
                    # xa -> chậm hơn, vừa -> vừa, sát -> nhanh
                    # (khác hẳn kiểu dist>150 chạy full)
                    slow = min(1.0, max(0.35, dist / 420.0))

                    # thêm "nút nhấn" khi cực gần để vẫn nguy hiểm
                    if dist < 120:
                        slow = min(1.0, slow + 0.10)

                    desired = dirv * (self.speed * slow)
                    self.vel += (desired - self.vel) * min(1.0, dt * self._steer_gain)
        else:
            # wander
            self._wander_t += dt
            if self._wander_t >= self._wander_cd:
                self._wander_t = 0.0
                self._wander_cd = random.uniform(0.9, 1.8)
                self._wander_dir = self._rand_dir()

            desired = self._wander_dir * (self.speed * 0.50)
            self.vel += (desired - self.vel) * min(1.0, dt * self._wander_gain)

        # clamp velocity
        if self.vel.length_squared() > 1:
            maxv = self.speed
            if self.vel.length() > maxv:
                self.vel = self.vel.normalize() * maxv

        # flip
        if self.vel.x != 0:
            self.sprite.flip_x = self.vel.x < 0

        # move
        self.pos += self.vel * dt
        self.pos.x = max(0, min(world_w, self.pos.x))
        self.pos.y = max(0, min(world_h, self.pos.y))

        self.sprite.update(dt)

    def draw(self, screen, camera, font):
        if not self.alive:
            return

        img = self.sprite.get_image(scale=self.scale)
        rect = img.get_rect(center=camera.world_to_screen(self.pos))
        screen.blit(img, rect)

        if font:
            p = camera.world_to_screen(self.pos)
            label = str(self.points)
            txt = font.render(label, True, (255, 255, 255))
            out = font.render(label, True, (0, 0, 0))
            y = int(p.y - rect.height // 2 - 12)
            screen.blit(out, out.get_rect(center=(int(p.x) + 1, y + 1)))
            screen.blit(txt, txt.get_rect(center=(int(p.x), y)))
