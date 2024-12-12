import csv
import os
from datetime import datetime
import constants


class Logger:
    def __init__(self, directory):
        self.data = []
        self.logged_constants = False
        self.directory = os.path.join(directory, datetime.now().strftime('%Y-%m-%d-%H-%M-%S.csv'))
        
    def log(self, game, action):
        self.data.append({
            'step': game.info.step,
            'episode': game.info.episode,
            'ball_y': game.ball.y,
            'ball_vy': game.ball.vy,
            'reference_y': game.reference.values[int(game.ball.x)],
            'action': action,
            'cost': game.info.episode_costs()[-1],
        })
    
    def write(self):
        assert(len(self.data) != 0)
        
        if not os.path.exists(self.directory):
                os.makedirs(self.directory)
        
        if not self.logged_constants:
            constants_fp = os.path.join(self.directory, 'constants.txt')
            constants_dict = {
                name: getattr(constants, name)
                for name in dir(constants)
                if name.isupper()
            }
            
            with open(constants_fp, 'w', newline='') as f:
                for k, v in constants_dict.items():
                    f.write(f"{k}\t\t{v}\n")
                        
        data_fp = os.path.join(self.directory, 'data.csv')
        with open(data_fp, 'w', newline='') as csvfile:
            fieldnames = list(self.data[0].keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for entry in self.data:
                writer.writerow(entry)
