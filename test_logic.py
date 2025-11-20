
from logic.entities import Driver, Passenger
from logic.rewards import calculate_composite_reward

driver_1 = Driver(d_id=0, loc=[0, 0])
driver_1.hours_driven_today = 10.0 # He or she is tired
print(f"Driver status: Fatigue Score = {driver_1.fatigue_score:.2f}")
# except the fatigue score to be around 10/12 = 0.83

passenger_1 = Passenger(p_id=500, loc=[3,4], dest_zone=2)
passenger_1.wait_time = 5 # wait time

l1_target_goal = 2

trip_distance_km = 10

total_reward, components = calculate_composite_reward(
    driver_1,
    passenger_1,
    trip_distance_km,
    l1_target_goal
)

print("### HPQN Bonus Calculation Report ###")
print(f"Reward profit: {components['profit']} ")
print(f"Waiting penalty: {components['wait']}")
print(f"Driver utility: {components['driver_util']:.2f}")
print(f"    -> Analysis: pickup distance was 5, but was penalized bacause he/she was tired: {components['driver_util']}")
print(f"Reward compliance: {components['compliance']}") # the passenger's destination was the same as L1's
print(f"-"*30)
print(f"The Total Reward: {", ".join(["{:.2f}".format(float(item)) for item in total_reward])}")