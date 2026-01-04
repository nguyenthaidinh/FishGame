# src/entities/ai_fish.py
import random
import pygame
from src.entities.animated_sprite import AnimatedSprite


class PredatorFish:
    """
    Cá săn mồi (AI độc lập) - Balanced + Boss:
    - scale theo points (giữ clamp để không quá to)
    - aggro vừa phải, nhưng boss sẽ xa hơn
    - chase có "burst" + nghỉ (đỡ dí liên tục)
    - boss có thêm "dash" ngắn khi áp sát -> kịch tính, có thể chết
    """

    def __init__(self, pos, fish_folder, points=80):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(0, 0)

        self.points = int(points)
        self.alive = True

        # =========================
        # BOSS FLAG
        # =========================
        self.is_boss = self.points >= 500  # boss m1(300-500) thì 500+ là boss rõ rệt

        # =========================
        # SCALE + HITBOX theo points (GIỮ CLAMP)
        # =========================
        p_vis = max(1, min(320, self.points))

        self.scale = 1.00 + (p_vis / 320.0) * 0.95   # ~1.00 -> ~1.95
        self.scale = max(0.95, min(self.scale, 2.05))
        self.hit_radius = 18.0 * self.scale

        # =========================
        # SPEED theo points (base)
        # =========================
        self.speed = 125.0 + (p_vis / 320.0) * 120.0
        self.speed = max(120.0, min(self.speed, 255.0))

        # boss nhanh hơn chút (không quá gắt)
        if self.is_boss:
            self.speed = min(self.speed * 1.15, 310.0)

        # =========================
        # AGGRO theo points (base)
        # =========================
        self.aggro_radius = 260.0 + min(280.0, p_vis * 0.9)  # ~260 -> ~548
        self.aggro_radius = max(240.0, min(self.aggro_radius, 580.0))

        # boss nhìn xa hơn rõ rệt
        if self.is_boss:
            self.aggro_radius = min(self.aggro_radius + 160.0, 820.0)

        # =========================
        # Chase "burst" (đuổi / nghỉ)
        # =========================
        # normal
        self._chase_on = 0.0
        self._chase_off = 0.0
        self._chase_on_cd = random.uniform(1.0, 1.6)   # thời gian đuổi
        self._chase_off_cd = random.uniform(0.5, 0.9)  # thời gian nghỉ

        # boss: đuổi lâu hơn, nghỉ ít hơn
        if self.is_boss:
            self._chase_on_cd = random.uniform(1.4, 2.1)
            self._chase_off_cd = random.uniform(0.28, 0.55)

        # steering gains
        self._steer_gain = 4.2
        self._wander_gain = 2.6
        if self.is_boss:
            self._steer_gain = 5.2   # bám hơn
            self._wander_gain = 3.0

        # wander
        self._wander_t = 0.0
        self._wander_cd = random.uniform(0.9, 1.8)
        self._wander_dir = self._rand_dir()

        # =========================
        # DASH (boss only)
        # =========================
        self._dash_cd = random.uniform(2.0, 3.2) if self.is_boss else 999.0
        self._dash_t = 0.0
        self._dash_left = 0.0
        self._dash_time = 0.18 if self.is_boss else 0.0
        self._dash_speed = 420.0 if self.is_boss else 0.0  # impulse speed

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
                # random lại CD
                if self.is_boss:
                    self._chase_off_cd = random.uniform(0.28, 0.55)
                else:
                    self._chase_off_cd = random.uniform(0.5, 0.9)
            return
        # đang nghỉ
        if self._chase_off > 0:
            self._chase_off -= dt
            if self._chase_off <= 0:
                self._chase_on = self._chase_on_cd
                if self.is_boss:
                    self._chase_on_cd = random.uniform(1.4, 2.1)
                else:
                    self._chase_on_cd = random.uniform(1.0, 1.6)
            return
        # init lần đầu
        self._chase_on = self._chase_on_cd

    def _update_dash(self, dt, in_aggro: bool, dist: float, dirv: pygame.Vector2):
        if not self.is_boss:
            return

        # dash đang diễn ra
        if self._dash_left > 0:
            self._dash_left -= dt
            # trong dash: kéo vel về dash hướng dirv
            desired = dirv * self._dash_speed
            self.vel += (desired - self.vel) * min(1.0, dt * 10.0)
            return

        # tick cooldown
        self._dash_t += dt
        if not in_aggro:
            return

        # chỉ dash khi khá gần để có cảm giác "lao vào"
        if dist < 260 and self._dash_t >= self._dash_cd and self._chase_off <= 0:
            self._dash_t = 0.0
            self._dash_cd = random.uniform(1.8, 3.0)
            self._dash_left = self._dash_time

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
            self._update_burst_state(dt)

            v = target.pos - self.pos
            dist = v.length()
            if dist > 1:
                dirv = v / dist
            else:
                dirv = pygame.Vector2(1, 0)

            # dash (boss)
            self._update_dash(dt, in_aggro, dist, dirv)
            if self.is_boss and self._dash_left > 0:
                # đang dash => đã set vel trong _update_dash
                pass
            else:
                # nếu đang "nghỉ" thì wander nhẹ
                if self._chase_off > 0:
                    desired = self._wander_dir * (self.speed * (0.58 if self.is_boss else 0.55))
                    self.vel += (desired - self.vel) * min(1.0, dt * self._wander_gain)
                else:
                    # slowdown:
                    # normal: min 0.35
                    # boss: min 0.48 (ít slowdown hơn -> khó né hơn)
                    slow_min = 0.48 if self.is_boss else 0.35
                    slow = min(1.0, max(slow_min, dist / (460.0 if self.is_boss else 420.0)))

                    # cực gần -> tăng thêm để nguy hiểm
                    if dist < (135 if self.is_boss else 120):
                        slow = min(1.0, slow + (0.16 if self.is_boss else 0.10))

                    desired = dirv * (self.speed * slow)
                    self.vel += (desired - self.vel) * min(1.0, dt * self._steer_gain)
        else:
            # wander
            self._wander_t += dt
            if self._wander_t >= self._wander_cd:
                self._wander_t = 0.0
                self._wander_cd = random.uniform(0.9, 1.8)
                self._wander_dir = self._rand_dir()

            desired = self._wander_dir * (self.speed * (0.55 if self.is_boss else 0.50))
            self.vel += (desired - self.vel) * min(1.0, dt * self._wander_gain)

        # clamp velocity
        if self.vel.length_squared() > 1:
            maxv = self.speed * (1.35 if (self.is_boss and self._dash_left > 0) else 1.0)
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
