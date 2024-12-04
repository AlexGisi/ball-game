import csv
import os
from datetime import datetime
from constants import *


class Logger:
    def __init__(self):
        self.data = []
        
    def log(self, game, action):
        self.data.append({
            'step': game.info.step,
            'episode': game.info.episode,
            'ball_y': game.ball.y,
            'ball_vy': game.ball.vy,
            'reference_y': game.reference.values[int(game.ball.x)],
            'action': action,
        })
    
    def write(self, directory=None, filename=None):
        assert(len(self.data) != 0)
        if filename is None:
            filename = datetime.now().strftime('%Y-%m-%d-%H-%M-%S.csv')
    
        if directory is not None:
            filename = os.path.join(directory, filename)
            if not os.path.exists(directory):
                os.makedirs(directory)
        
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = list(self.data[0].keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for entry in self.data:
                writer.writerow(entry)
