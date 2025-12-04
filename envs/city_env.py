import gymnasium as gym
from gymnasium import spaces
import numpy as np
from logic.entities import Driver, Passenger
from logic.rewards import calculate_composite_reward
from config import Config

class CityEnv(gym.Env):
    def __init__(self):
        super(CityEnv, self).__init__()
        
        self.grid_size = 4
        self.num_zones = self.grid_size * self.grid_size # 4 * 4 city zones
        self.num_drivers = 50 # all the drivers
        self.current_time = 0 # from 0 to 1440m (24h)

        # Action Space
        self.action_space = spaces.Dict(
            {
                "l1_incentives": spaces.Box(low=0, high=10, shape=(self.num_zones,), dtype=np.float32),
                "l2_dispatch": spaces.Discrete(self.num_drivers) # Select a driver
            }
        )

        # Observation Space
        self.observation_space = spaces.Dict(
            {
                "driver_locations": spaces.Box(low=0, high=self.grid_size, shape=(self.num_drivers, 2), dtype=np.float32),
                "driver_fatigues": spaces.Box(low=0, high=1, shape=(self.num_drivers,), dtype=np.float32),
                "demand_density": spaces.Box(low=0, high=100, shape=(self.num_zones), dtype=np.float32),
                "time_of_day": spaces.Box(low=0, high=24, shape=(1,), dtype=np.float32)
            }
        )

        # Entitie lists
        self.drivers = []
        self.passengers = []
        self.l1_target_zones = np.zeros(self.num_zones) # currently incentives

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        # time reset
        self.current_time = 0

        # create first drivers
        self.drivers = []
        for item in range(self.num_drivers):
            # random position
            start_loc = np.random.rand(2) * self.grid_size
            d = Driver(d_id=item, loc=start_loc)
            self.drivers.append(d)
        
        self.passengers = []

        return self._get_observation(), {}
    
    def step(self, action):
        """
            Running a time step. (5 min eg.)
        """
        self.current_time += 5
        done = False
        if self.current_time >= 1440:
            done = True

        # L1 decision making
        if "l1_incentives" in action:
            self.l1_target_zones = action["l1_incentives"]
        
        # Generating new demand (passenger) - Poisson model
        self._generate_demand()

        # L2 logic (dispathcing)
        total_step_reward = 0
        info = {}

        if len(self.passengers) > 0:
            selected_driver_idx = action.get("l2_dispatch", 0)
            selected_driver_idx = selected_driver_idx % len(self.drivers)

            driver = self.drivers[selected_driver_idx]
            passenger = self.passengers[0] # the first passenger of queue

        if driver.status == "IDLE":
            trip_dist = np.linalg.norm(driver.loaction - passenger.location)
            dest_zone_idx = int(passenger.destination_zone)
            target_bonus = 0
            if 0 <= dest_zone_idx < len(self.l1_target_zones):
                # L1 target zone
                target_bonux = self.l1_target_zones[dest_zone_idx]
            
            reward, details = calculate_composite_reward(
               driver, passenger, trip_dist, l1_target_zone=dest_zone_idx
            )

            # Driver status update (trip simulation)
            driver.location = passenger.location
            driver.hours_driven_today += 0.5

            total_step_reward = reward
            
            # Delete serviced passenger
            self.passengers.pop(0)

        # Update fatigue for all drivers
        for driver in self.drivers:
            if driver.status == "IDLE":
                pass
            
        return self._get_observation(), total_step_reward, False, info
    
    def _get_observation(self):
        """
            Convert class state to NumPy format for AI section.
        """
        driver_locs = np.array([d.location for d in self.drivers], dtype=np.float32)
        driver_fatigues = np.array([d.fatigue_score for d in self.drivers], dtype=np.float32)

        # Calculation of demand density in regions
        demand_counts = np.zeros(self.num_zones, dtype=np.float32)
        for passenger in self.passengers:
            z = int(passenger.destination_zone)
            if 0 <= z < self.num_zones:
                demand_counts[z] += 1

        return {
            "driver_locations": driver_locs,
            "driver_fatigues": driver_fatigues,
            "demand_density": demand_counts,
            "time_of_day": np.array([self.current_time / 60.0], dtype=np.float32)
        }

    def _generate_demand(self):
        """
            Random passenger generation based on time of day. 
        """
        hour = (self.current_time / 60.0) % 24
        lambda_rate = 2.0 if (7 < hour < 10) or (17 < hour < 20) else 0.5

        num_new_passengers = np.random.poisson(lambda_rate)

        for _ in range(num_new_passengers):
            # Random position
            loc = np.random.rand(2) * self.grid_size

            # Random destination
            dest_zone = np.random.randint(0, self.num_zones)

            new_p = Passenger(p_id=len(self.passengers), loc=loc, dest_zone=dest_zone)
            self.passengers.append(new_p)
            
