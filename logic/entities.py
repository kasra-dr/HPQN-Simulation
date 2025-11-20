
import numpy as np

class Passenger:
    def __init__(self, p_id, loc, dest_zone):
        self.id = p_id
        self.location = np.array(loc) # [x, y]
        self.destination_zone = dest_zone
        self.wait_time = 0

    def increment_wait(self):
        self.wait_time += 1

    
class Driver:
    def __init__(self, d_id, loc):
        self.id = d_id
        self.location = np.array(loc) # [x, y]
        self.status = "IDLE" # or "BUSY"

        self.hours_driven_today = 0.0
        self.consecutive_driving_hours = 0.0
        self.acceptance_rate = 1.0

    @property
    def fatigue_score(self):
        """
        Calculation of the evaluation score (S Fatigue) between 0 and 1. 
        """
        # normalization of driving hours (assumption: 12 hours of driving = complete fatigue)
        fatigue = self.hours_driven_today / 12.0
        
        # continuous driving effect (aggravation factor)
        if self.consecutive_driving_hours > 4:
            fatigue += 0.2

        # make sure the number stays between 0 and 1
        return np.clip(fatigue, 0.0, 1.0)
    def update_position(self, new_loc):
        self.location = np.array(new_loc)