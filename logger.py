import csv
import os
from datetime import datetime


class Logger:
    def __init__(self):
        self.data = []
    
    def log(self, time_step, ball_state, reference_state, action):
        self.data.append({
            'time_step': time_step,
            'ball_y': ball_state.y,
            'ball_vy': ball_state.vy,
            'reference_y': reference_state,
            'action': action,
        })
    
    def write(self, directory=None, filename=None):
        if filename is None:
            filename = datetime.now().strftime('%Y-%m-%d-%H-%M-%S.csv')
        if directory is not None:
            filename = os.path.join(directory, filename)
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['time_step', 'ball_y', 'ball_vy', 'reference_y', 'action']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for entry in self.data:
                writer.writerow(entry)
