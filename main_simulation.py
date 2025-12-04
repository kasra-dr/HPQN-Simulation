import numpy as np
import matplotlib.pyplot as plt
from envs.city_env import CityEnv

def run_simulation():
    # Create the environment
    env = CityEnv()
    obs, _ = env.reset()

    # Lists to store statistical data required for the ARTICLE
    history = {
        "time_step": [],
        "total_reward": [],
        "avg_fatigue": [],
        "demand_count": []
    }

    print("...Simulation Started! (Duration: 24 hour - 288 5-minute steps)...")

    # Run the loop for 288 steps (24 hour * 12 to 5 minutes)
    max_steps = 288
    for step in range(max_steps):
        # Decision making
        action = env.action_space.sample()
        obs, reward, done, _, info = env.step(action)

        # Storing the data
        history["time_step"].append(step)
        history["total_reward"].append(reward) # the reward of this moment

        # Average driver fatigue at this moment
        avg_fatigue = np.mean(obs["driver_fatigues"])
        history["avg_fatigue"].append(avg_fatigue)

        # Number of existing demands in the city (demand density)
        total_demand = np.sum(obs["demand_density"])
        history["demand_count"].append(total_demand)

        if done:
            break
    
    print("Simulation completed.")
    return history

def plot_results(history):
    """
        Making scentific diagrams for the ARTICLE
    """

    steps = history["time_step"]
    plt.figure(figsize=(12, 10))

    # Chart 1: Cumulative system reward (Efficiency)
    plt.subplot(3, 1, 1)
    plt.plot(steps, np.cumsum(history["total_reward"]), color='green', label="Cumulative Reward")
    plt.title("Performance: Cumulative System Reward over 24h")
    plt.ylabel("Reward Value")
    plt.grid(True, alpha=0.3)
    plt.legend()

    # Chart 2: Fleet fatigue status (Innovation effect S_fatigue)
    plt.subplot(3, 1, 2)
    plt.plot(steps, history["avg_fatigue"], color='red', linestyle='--', label='Avg Fleet Fatigue')
    plt.title("Driver Welfare: Average Fatigue Score (0=Fresh, 1=Exhausted)")
    plt.ylabel("Fatigue Score")
    plt.ylim(0, 1)
    plt.grid(True, alpha=0.3)
    plt.legend()

    # Chart 3: Demand pattern (dynamics of the environment)
    plt.subplot(3, 1, 3)
    plt.plot(steps, history["demand_count"], color='blue', label='Passenger Demand')
    plt.title("Market Dynamics: Total Demand Density")
    plt.xlabel("Time Steps (5-min intervals)")
    plt.ylabel("Number of Waiting Passengers")
    plt.grid(True, alpha=0.3)
    plt.legend()

    plt.tight_layout()
    # Save the charts
    plt.savefig("simulation_result.png", dpi=300)
    print("ُThe charts seved on the 'simulation_results.png' file.")
    plt.show()

if __name__ == "__main__":
    data = run_simulation()
    plot_results(data)
