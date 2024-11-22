from dataclasses import dataclass, field
import math
from constants import *


@dataclass
class BallState:
    x: float = field(default_factory=lambda: SCREEN_WIDTH * 0.2)
    y: float = field(default_factory=lambda: GAME_HEIGHT / 2)
    vy: float = field(default_factory=lambda: 0)
    vy_abs_max: float = 350.0
    
    # def step(self, action):
    #     dt = 1 / FPS
    #     self.y = self.y + dt * self.vy
    #     self.vy = self.vy + dt * action * 1000
    
    def step(self, action):
        dt = 1 / FPS
        self.y = self.y + dt * self.vy
        self.vy = action * 200
    
    def clip(self):
        self.y = max(BALL_RADIUS, min(GAME_HEIGHT - BALL_RADIUS, self.y))
        self.vy = max(-self.vy_abs_max, min(self.vy_abs_max, self.vy))
        
        
@dataclass
class Reference:
    values: list = field(default_factory=lambda: [GAME_HEIGHT / 2] * SCREEN_WIDTH)
     
    def get(self, horizon=None):
        if horizon is None:
            horizon = len(self.values)
        return self.values[:horizon] if horizon > 1 else self.values[horizon]
    
    def get_error(self, ball_state):
        return self.values[int(ball_state.x)] - ball_state.y
    
    def step(self, time):
        frequency = 1 / 30
        amplitude = GAME_HEIGHT / 4
        y = (GAME_HEIGHT / 2) + amplitude * math.sin(frequency * time)
        self.values.pop(0)
        self.values.append(y)