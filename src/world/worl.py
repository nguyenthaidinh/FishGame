# src/world/world.py

from src.world.camera import Camera
from src.world.spawner import Spawner

class World:
    def __init__(self, screen_w, screen_h, map_data):
        self.w, self.h = map_data["size"]

        self.camera = Camera(screen_w, screen_h, self.w, self.h)
        self.spawner = Spawner(self.w, self.h, map_data["prey_values"])

        self.preys = []

    def update(self, dt, player, map_id):
        self.camera.follow(player.pos)
        self.spawner.update(dt, player.points, self.preys, self.camera, map_id)

        for p in self.preys:
            p.update(dt, player)

    def draw(self, screen):
        for p in self.preys:
            p.draw(screen, self.camera)
