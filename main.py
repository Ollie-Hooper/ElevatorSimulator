import json
import numpy as np
import os
import pandas as pd
import random
import time

from elevator.algorithms import BasicAlgorithm, SimpleUpDown, ClosestFloor, NormalLift, \
    LongestWaited  # Import your algorithm from the algorithms file here
from elevator.classes import Elevator, Passenger, Building
from elevator.functions import run_simulation, charts, run_iteration, generate_passenger, time_method


def main():
    algos = [SimpleUpDown(), ClosestFloor(), NormalLift(), LongestWaited()]  # Algorithms to test

    iterations = 100  # How many times to run the simulation - set to 0 to study the first algorithm in the algos list

    name = "morning_simulation"  # Name of test

    config = dict(
        mode="morning",  # Simulation mode - either morning, random or evening
        draw=False,  # Draw out each stage of the simulation in the console
        max_occupancy=10,  # Max occupancy of lift
        n_floors=10,  # Number of floors in the building
        n_passengers=100,  # Number of passengers to simulate
        generate_range=(0, 2),  # Range of passengers to spawn each iteration
        acceleration=1.5,  # Acceleration/deceleration of lift (ms^-2)
        max_speed=6.7,  # Max speed of lift (ms^-1)
        storey_height=4,  # Height of building storey (m)
        embark_disembark_time=1,  # Time for each passenger to get on/off (s)
    )

    if not iterations:
        config["draw"] = True
        run_simulation(config=config, algo=algos[0])
        exit()

    df_journey_times = pd.DataFrame(columns=[a.name for a in algos],
                                    index=[[i for i in range(iterations) for j in range(config['n_passengers'])],
                                           [i for j in range(iterations) for i in range(config['n_passengers'])]])

    df_in_elevator_times = pd.DataFrame(columns=[a.name for a in algos],
                                        index=[[i for i in range(iterations) for j in range(config['n_passengers'])],
                                               [i for j in range(iterations) for i in range(config['n_passengers'])]])

    for i in range(iterations):
        for algo in algos:
            ts = time.time()
            journey_times, in_elevator_times = run_simulation(config=config, algo=algo)
            ts_save = time.time()
            df_journey_times.loc[(i, list(range(config['n_passengers']))), algo.name] = journey_times
            df_in_elevator_times.loc[(i, list(range(config['n_passengers']))), algo.name] = in_elevator_times
            te = time.time()
            print(f"Save time - %2.3f seconds" % (te - ts_save))
            print(f"Total time - %2.3f seconds" % (te - ts))
            print()

    if not os.path.exists(f"output"):
        os.mkdir(f"output")
    if not os.path.exists(f"output/{name}"):
        os.mkdir(f"output/{name}")

    df_journey_times.to_csv(f"output/{name}/journey_times.csv")
    df_in_elevator_times.to_csv(f"output/{name}/elevator_times.csv")

    with open(f"output/{name}/config.json", 'w') as f:
        json.dump(config, f)

    charts(name, df_journey_times, df_in_elevator_times)


if __name__ == "__main__":
    main()
