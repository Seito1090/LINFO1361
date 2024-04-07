import matplotlib.pyplot as plt
import pandas as pd

def plot_graph(datacsv):
    # get the data
    data = pd.read_csv(datacsv)

    # Count the occurrences of each winner (0 or 1)
    win_counts = data['Winner'].value_counts()

    # Calculate win rates
    total_games = len(data)
    win_rate_0 = win_counts.get(0, 0) / total_games
    win_rate_1 = win_counts.get(1, 0) / total_games

    # Plot win rates
    plt.bar(['Random', 'Alphabeta'], [win_rate_0, win_rate_1])
    plt.xlabel('Player')
    plt.ylabel('Win Rate')
    plt.title('Win Rate of Players')
    plt.show()

    # Compute and display the average number of moves
    average_moves = data['Moves'].mean()

    # Compute and display the average time
    average_time = data['Time'].mean()
    print(f'Average Number of Moves: {average_moves:.2f}')
    print(f'Average Time: {average_time:.2f} seconds')

if __name__ == '__main__':
    plot_graph('alphabeta_vs_random.csv')
