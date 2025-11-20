
import numpy as np
from config import Config

def calculate_distance(loc1, loc2):
    """ 
    the Euclidean distance between two points
    """
    return np.linalg.norm(loc1 - loc2)

def calculate_composite_reward(driver, passenger, trip_distance, l1_target_zone):
    """
    the HPQN multi-objective reward according to the formula.
    """
    # R_profit
    fare = Config.BASE_FARE + (trip_distance * Config.PER_KM_RATE)
    cost = trip_distance * Config.DRIVER_COST_PER_KM
    r_profit = fare - cost

    # R_wait
    r_wait = -1 * (Config.WAIT_PENALTY_FACTOR * (passenger.wait_time ** 2))

    # R_driver_utility
    pickup_dist = calculate_distance(driver.location, passenger.location)
    s_fatigue = driver.fatigue_score

    # D_pickup
    r_driver = -1 * (pickup_dist * (1 + s_fatigue))

    # R_system_compliance
    r_system = 0
    if passenger.destination_zone == l1_target_zone:
        r_system = Config.COMPLIANCE_BONUS    
        print(f"Strategic match! Drvier goes to target zone {l1_target_zone}.")

    r_total = (
        (Config.W1_PROFIT * r_profit),
        (Config.W2_WAIT_TIME * r_wait),
        (Config.W3_DRIVER_UTIL * r_driver),
        (Config.W4_COMPLIANCE * r_system),
    )

    return r_total, {
        "profit": r_profit,
        "wait": r_wait,
        "driver_util": r_driver,
        "compliance": r_system,
    }

