from elevator.algorithms import BasicAlgorithm, SimpleUpDown, ClosestFloor, NormalLift, \
    LongestWaited, PopularFloor  # Import your algorithm from the algorithms file here
from elevator.classes import Elevator, Passenger, Building
from elevator.functions import run_simulation, charts, run_iteration, generate_passenger, time_method, run_test, \
    batch_test


def main():
    config = dict(
        algos=[ClosestFloor, NormalLift, LongestWaited, PopularFloor],  # Algorithms to test
        iterations=100,  # How many times to run the simulation - set to 0 to study the first algorithm in the list
        mode="morning",  # Simulation mode - either morning, random or evening
        draw=False,  # Draw out each stage of the simulation in the console
        max_occupancy=12,  # Max occupancy of lift
        n_floors=20,  # Number of floors in the building
        n_passengers=100,  # Number of passengers to simulate
        generate_range=(0, 2),  # Range of passengers to spawn each iteration
        acceleration=1.5,  # Acceleration/deceleration of lift (ms^-2)
        max_speed=6.7,  # Max speed of lift (ms^-1)
        storey_height=4,  # Height of building storey (m)
        embark_disembark_time=1,  # Time for each passenger to get on/off (s)
    )

    batch_test(config)


if __name__ == "__main__":
    main()
