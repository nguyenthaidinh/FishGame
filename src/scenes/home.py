import pygame
from src.core.scene import Scene
from src.ui.button import Button
from src.scenes.mode_select import ModeSelectScene
from src.scenes.leaderboard import LeaderboardScene
from src.scenes.history import HistoryScene

class HomeScene(Scene):
    def on_enter(self, **kwargs):
        self.title_font = self.app.assets.font(None, 62)
        self.sub_font = self.app.assets.font(None, 22)
        self.btn_font = self.app.assets.font(None, 28)

        cx = self.app.width // 2
        y = 300
        gap = 72
        theme = getattr(self.app, "theme", {"text": (240,245,255), "muted": (200,215,235)})

        self.buttons = [
            Button((cx-190, y,       380, 62), "PLAY NOW",     lambda: self.app.scenes.set_scene(ModeSelectScene(self.app)), self.btn_font, theme),
            Button((cx-190, y+gap,   380, 62), "LEADERBOARD",  lambda: self.app.scenes.set_scene(LeaderboardScene(self.app)), self.btn_font, theme),
            Button((cx-190, y+gap*2, 380, 62), "HISTORY",      lambda: self.app.scenes.set_scene(HistoryScene(self.app)), self.btn_font, theme),
            Button((cx-190, y+gap*3, 380, 62), "SETTINGS",     lambda: None, self.btn_font, theme),
            Button((cx-190, y+gap*4, 380, 62), "QUIT",         self.app.quit, self.btn_font, theme),
        ]

    def handle_event(self, event):
        for b in self.buttons:
            b.handle_event(event)

    def draw(self, screen):
        screen.fill((6, 22, 44))
        pygame.draw.circle(screen, (40, 110, 190), (240, 160), 220)
        pygame.draw.circle(screen, (20, 70, 140), (240, 160), 300, width=10)

        title = self.title_font.render("BIG FISH", True, self.app.theme["text"])
        sub = self.sub_font.render("Eat, grow, survive. Unlock maps & fish.", True, self.app.theme["muted"])
        screen.blit(title, title.get_rect(center=(self.app.width //2, 190)))
        screen.blit(sub, sub.get_rect(center=(self.app.width //2, 240)))

        for b in self.buttons:
            b.draw(screen)
