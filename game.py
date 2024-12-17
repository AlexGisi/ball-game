from dataclasses import dataclass, field
import sim
from constants import *   


class Episode:
    def __init__(self):
        self.observations = []

@dataclass
class GameInfo:
    step: int = 0
    episode_step: int = 0
    episode: int = 0
    
    episodes = []
    current_episode = Episode()
    
    def reset(self):
        self.episodes.append(self.current_episode)
        self.current_episode = Episode()
        self.episode += 1
        self.episode_step = 0
    
    def episode_costs(self):
        return [obs.cost for obs in self.current_episode.observations]
    

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
        self.info.current_episode.observations.append(observation)
                
        self.info.last_action = action
        self.info.step += 1
        self.info.episode_step += 1
        
        return self.episode_done(), self.game_done()
        
    def reset(self):
        self.ball.reset()
        self.reference.reset()
        self.info.reset()
        
    def cost(self):
        return (self.reference.y_ref() - self.ball.position())**2 / 1_000
    
    def episode_done(self):
        return self.info.episode_step > EPISODE_MAX_LENGTH
    
    def game_done(self):
        return self.info.step > GAME_MAX_LENGTH


class TrainingObservation:
    def __init__(self, ball, ref, action, cost) -> None:
        self.y = ball.position()
        self.y_ref = ref.y_ref()
        self.action = action
        self.cost = cost
    
    
class OperationObservation:
    def __init__(self, game_state) -> None:
        self.y = game_state.ball.position()
    