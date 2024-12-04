from dataclasses import dataclass, field
import copy
import sim
from constants import *   



@dataclass
class GameInfo:
    step: int = 0
    episode_step: int = 0
    episode: int = 0
    
    observations = []
    

class Game:
    def __init__(self, reference_type):
        self.ball = sim.BallState()
        self.reference = reference_type()
        self.info = GameInfo()
    
    def step(self, action):
        self.ball.step(action)
        self.ball.clip()
        self.reference.step(self.info.episode_step)
        
        observation = TrainingObservation(self.ball, self.reference, action, self.cost())
        self.info.observations.append(observation)
                
        self.info.last_action = action
        self.info.step += 1
        self.info.episode_step += 1
        
        return self.episode_done(), self.game_done()
        
    def reset(self):
        self.ball.reset()
        self.reference.reset()
        
        self.info.episode += 1
        self.info.episode_step = 0
        
    def cost(self):
        return self.reference.y_ref() - self.ball.output()
    
    def episode_done(self):
        return self.info.episode_step > EPISODE_MAX_LENGTH
    
    def game_done(self):
        return self.info.step > GAME_MAX_LENGTH


class TrainingObservation:
    def __init__(self, ball, ref, action, cost) -> None:
        self.y = ball.output()
        self.y_ref = ref.y_ref()
        self.action = action
        self.cost = cost
    
    
class OperationObservation:
    def __init__(self, game_state) -> None:
        self.y = game_state.ball.output()
    