import math
import random
import numpy as np
from scipy.integrate import quad_vec
from scipy.linalg import expm
from constants import *


class BallState:
    def __init__(self):
        self.x: float = BALL_X_INIT
        self.vy_abs_max: float = BALL_VY_ABS_MAX

        # self.state = np.array([[BALL_Y_INIT, BALL_VY_INIT]]).T
        self.state = np.array([[0, 0]]).T
        self.A = np.array([
            [-3.1416, -2.4674],
            [1.00, 0.0],
        ])
        self.B = np.array([
            [2.0],
            [0.0],
        ])
    
    def step(self, action, max_error=0.01):
        dt = 1 / FPS

        Ad = expm(self.A * dt)

        integrand = lambda tau: expm(self.A * (dt - tau)) @ self.B
        Bd, error = quad_vec(integrand, 0, dt)

        if error > max_error:
            raise ValueError()
        
        self.state = Ad @ self.state + Bd * action
        
    def reset(self):
        self.x: float = BALL_X_INIT
        self.state = np.array([[0, 0]]).T
    
    def clip(self):
        # self.y = max(BALL_RADIUS, min(GAME_HEIGHT - BALL_RADIUS, self.y))
        # self.vy = max(-self.vy_abs_max, min(self.vy_abs_max, self.vy))
        pass
        
    def position(self):
        """Represents the h(x) in y_i = h(x_i).

        Returns:
            float: ball position
        """
        return (float(self.state[1]) * 500) + BALL_Y_INIT
    
    def velocity(self):
        return float(self.state[0])
        

class Reference:
    def __init__(self):
        self.values = []
        self.init_values()
            
    def init_values(self):
        self.values = [GAME_HEIGHT / 2] * SCREEN_WIDTH
    
    def y_ref(self):
        return self.values[int(BALL_X_INIT)]
    
    def get_error(self, ball_state):
        return self.y_ref() - ball_state.position()
    
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
        # self.freq_interval = np.array([0.25, 0.4]) * (2 * np.pi) / FPS
        # self.freq_interval = np.array([1.57, 2.51]) / FPS
        self.freq_interval = np.array([0.1, 1.0]) / FPS
        self.amplitude_interval = [GAME_HEIGHT / 2, GAME_HEIGHT / 10]
        
        self.frequency = random.uniform(*self.freq_interval)
        self.amplitude = random.uniform(*self.amplitude_interval)
        super().__init__()
        
    def reset(self):
        self.start_moving = False
        self.frequency = random.uniform(*self.freq_interval)
        self.amplitude = random.uniform(*self.amplitude_interval)
        super().reset()
        print(self.frequency)
        
    def next_value(self, time):
        return (GAME_HEIGHT / 2) + self.amplitude * math.sin(self.frequency * time)