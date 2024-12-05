import argparse
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def episode_costs(df):
    fig, ax = plt.subplots()
    eps = df.groupby('episode').sum().reset_index()
    plt.scatter(eps['episode'].to_numpy(), eps['cost'].to_numpy())
    cost_std = np.std(eps['cost'].to_numpy())
    
    plt.ylabel("total episode cost")
    plt.xlabel("episode number")
    plt.title(f"episode costs (std={cost_std:.2f})")
    
    return fig


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file')
    parser.add_argument('plot')
    args = parser.parse_args()

    if not os.path.exists(args.file):
        raise ValueError(f"No file at {args.file}")
    df = pd.read_csv(args.file)
    
    if args.plot == "episode_costs":
        episode_costs(df)
    else:
        raise ValueError(f"No function named {args.plot}")
    
    plt.show()
