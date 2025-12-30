import pygame
from src.core.settings import Settings
from src.core.assets import Assets
from src.core.scene_manager import SceneManager
from src.core.save import SaveManager
from src.scenes.boot import BootScene
from src.scenes.menu import MenuScene
from src.scenes.mode_select import ModeSelectScene
from src.scenes.map_select import MapSelectScene

class GameApp:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init()
        except Exception as e:
            print("Mixer init warning:", e)

        pygame.display.set_caption(Settings.TITLE)

        self.w, self.h = Settings.WIDTH, Settings.HEIGHT
        self.screen = pygame.display.set_mode((self.w, self.h))
        self.clock = pygame.time.Clock()
        self.running = True

        self.assets = Assets()
        self.save = SaveManager()
        self.save.load()

        self.runtime = {"mode": 1, "map": None}

        self.theme = {
            "btn": (28, 85, 145),
            "btn_hover": (45, 115, 190),
            "btn_disabled": (35, 45, 60),
            "stroke": (120, 190, 255),
            "text": (240, 245, 255),
            "muted": (180, 195, 210),
        }

        self.scenes = SceneManager(self)
        self.scenes.set_scene(BootScene(self))

    def back(self):
        cur = self.scenes.scene.__class__.__name__ if self.scenes.scene else ""
        if cur == "GameScene":
            self.scenes.set_scene(MapSelectScene(self))
        elif cur == "MapSelectScene":
            self.scenes.set_scene(ModeSelectScene(self))
        elif cur == "ModeSelectScene":
            self.scenes.set_scene(MenuScene(self))
        else:
            self.quit()

    def quit(self):
        self.running = False

    def run(self):
        while self.running:
            dt = self.clock.tick(Settings.FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                else:
                    self.scenes.handle_event(event)

            self.scenes.update(dt)
            self.scenes.draw(self.screen)
            pygame.display.flip()

        pygame.quit()
