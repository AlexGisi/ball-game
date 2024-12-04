from dataclasses import dataclass, field
import math
from constants import *


class BallState:
    def __init__(self):
        self.x: float = BALL_X_INIT
        self.y: float = BALL_Y_INIT
        self.vy: float = BALL_VY_INIT
        self.vy_abs_max: float = BALL_VY_ABS_MAX
    
    # def step(self, action):
    #     dt = 1 / FPS
    #     self.y = self.y + dt * self.vy
    #     self.vy = self.vy + dt * action * 1000
    
    def step(self, action):
        dt = 1 / FPS
        self.y = self.y + dt * self.vy
        self.vy = action * 200
        
    def reset(self):
        self.x: float = BALL_X_INIT
        self.y: float = BALL_Y_INIT
        self.vy: float = BALL_VY_INIT
    
    def clip(self):
        self.y = max(BALL_RADIUS, min(GAME_HEIGHT - BALL_RADIUS, self.y))
        self.vy = max(-self.vy_abs_max, min(self.vy_abs_max, self.vy))
        
    def output(self):
        """Represents the h(x) in y_i = h(x_i).

        Returns:
            float: ball position
        """
        return self.y
        

class Reference:
    def __init__(self):
        self.values = []
        self.init_values()
            
    def init_values(self):
        self.values = [GAME_HEIGHT / 2] * SCREEN_WIDTH
        
        warmup_steps = int(SCREEN_WIDTH - BALL_X_INIT - REF_WARMUP_LENGTH)
        for i in range(warmup_steps):
            self.step(-warmup_steps + i)
    
    def y_ref(self):
        return self.values[int(BALL_X_INIT)]
    
    def get_error(self, ball_state):
        return self.y_ref() - ball_state.output()
    
    def step(self, time):
        raise NotImplementedError()
        
    def reset(self):
        self.values.clear()
        self.init_values()
        
        
class SineReference(Reference):
    def __init__(self):
        self.start_moving = False
        super().__init__()
        
    def reset(self):
        self.start_moving = False
        super().reset()
        
    def step(self, time):
        frequency = 1 / 30
        amplitude = GAME_HEIGHT / 4
        
        if not self.start_moving and time % int((1/frequency)*2*3.14) == 0:
            self.start_moving = True
            
        if self.start_moving:
            y = (GAME_HEIGHT / 2) + amplitude * math.sin(frequency * time)
        else:
            y = GAME_HEIGHT / 2
            
        self.values.pop(0)
        self.values.append(y)
    