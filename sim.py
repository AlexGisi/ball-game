from dataclasses import dataclass, field
import math
import random
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
        y = self.next_value(time)
        self.values.pop(0)
        self.values.append(y)
        
    def next_value(self, time):
        raise NotImplementedError()
        
    def reset(self):
        self.values.clear()
        self.init_values()
        
        
class StepReference(Reference):
    def __init__(self, segment_length=200):
        self.segment_length = segment_length
        self.segment_height = GAME_HEIGHT / 2
        self.segment_height_min = 100
        self.segment_height_max = SCREEN_HEIGHT - 150
        super().__init__()
        
    def next_value(self, time):
        if time % self.segment_length == 0:
            self.segment_height = random.randint(self.segment_height_min, self.segment_height_max)
        return self.segment_height
    

class RampReference(Reference):
    def __init__(self, segment_length=50):
        self.segment_length = segment_length
        self.slope = 0
        super().__init__()
        
    def next_value(self, time):
        if time % self.segment_length == 0:
            # Encourage it to not saturate
            self.slope = random.uniform(-1, 5) if self.values[-1] < (GAME_HEIGHT / 2) else random.uniform(-5, 1)
        y = self.values[-1] + self.slope
        y = max(BALL_RADIUS, min(GAME_HEIGHT - BALL_RADIUS, y))
        
        return y
        
class SineReference(Reference):
    def __init__(self):
        self.start_moving = False
        self.freq_interval = [1 / 30, 1/25]
        self.amplitude_interval = [GAME_HEIGHT / 2, GAME_HEIGHT / 10]
        
        self.frequency = random.uniform(*self.freq_interval)
        self.amplitude = random.uniform(*self.amplitude_interval)
        super().__init__()
        
    def reset(self):
        self.start_moving = False
        self.frequency = random.uniform(*self.freq_interval)
        self.amplitude = random.uniform(*self.amplitude_interval)
        super().reset()
        
    def next_value(self, time):
        if not self.start_moving and time % int((1/self.frequency)*2*3.14) == 0:
            self.start_moving = True
            
        if self.start_moving:
            y = (GAME_HEIGHT / 2) + self.amplitude * math.sin(self.frequency * time)
        else:
            y = GAME_HEIGHT / 2
            
        return y