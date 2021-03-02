import json
import math
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import random
import seaborn as sns
import time

from elevator.algorithms import SimpleUpDown
from elevator.classes import Elevator, Passenger, Building
from functools import wraps


def time_method(func):
    @wraps(func)
    def timed(*args, **kw):
        ts = time.time()
        result = func(*args, **kw)
        te = time.time()

        print("%r took %2.3f seconds to run." % (func.__name__, te - ts))

        return result

    return timed


def charts(name, df_journey_times, df_in_elevator_times):
    df_journey_times.reset_index(drop=True, inplace=True)
    for algo in df_journey_times:
        df_journey_times[algo] = df_journey_times[algo].sort_values(ignore_index=True)
    df_journey_times_95 = df_journey_times.head(round(len(df_journey_times) * 0.95))

    df_in_elevator_times.reset_index(drop=True, inplace=True)
    for algo in df_in_elevator_times:
        df_in_elevator_times[algo] = df_in_elevator_times[algo].sort_values(ignore_index=True)
    df_in_elevator_times_95 = df_in_elevator_times.head(round(len(df_in_elevator_times) * 0.95))

    for df_name, df in {'journey': df_journey_times, 'elevator': df_in_elevator_times,
                        'journey_95': df_journey_times_95,
                        'elevator95': df_in_elevator_times_95}.items():
        for plot in ['boxplot', 'violinplot', 'histogram']:
            if plot == 'histogram':
                for algo in df.columns:
                    sns.histplot(df[algo])
                    plt.savefig(f"output/{name}/{df_name}_{algo}_{df_name}.png")
                    plt.clf()
                continue
            elif plot == 'boxplot':
                sns.boxplot(data=df)
            elif plot == 'violinplot':
                sns.violinplot(data=df)
            plt.savefig(f"output/{name}/{plot}_{df_name}.png")
            plt.clf()


@time_method
def run_simulation(config, algo=SimpleUpDown()):
    try:
        elevator = Elevator(config['max_occupancy'], algo.only_pickup_directional_passengers, config['acceleration'],
                            config['max_speed'], config['embark_disembark_time'])
    except AttributeError:
        elevator = Elevator(config['max_occupancy'], False, config['acceleration'], config['max_speed'],
                            config['embark_disembark_time'])
    building = Building(config['n_floors'], config['storey_height'])

    origins = {i: [] for i in range(building.floors)}
    destinations = {i: [] for i in range(building.floors)}
    total_passengers = []
    n_passengers = config['n_passengers']

    while bool([x for x in destinations.values() if x != []]) or n_passengers:
        if n_passengers:
            n_gen_passengers = random.randint(config['generate_range'][0],
                                              min(config['generate_range'][1], n_passengers))
            for i in range(n_gen_passengers):
                passenger = generate_passenger(elevator.time, building, config['mode'])
                origins[passenger.origin].append(passenger)
                destinations[passenger.destination].append(passenger)
                total_passengers.append(passenger)
                n_passengers -= 1
        run_iteration(elevator, building, algo, origins, destinations, total_passengers, config['draw'])

    journey_times = [p.journey_time for p in total_passengers]
    in_elevator_times = [p.time_in_elevator for p in total_passengers]

    average_journey = np.mean(journey_times)
    average_time_in_elevator = np.mean(in_elevator_times)

    print(f"{algo.name}:")
    print(f"Average journey time (includes waiting time): {round(average_journey, 1)} (seconds)")
    print(f"Average time spent in lift: {round(average_time_in_elevator, 1)} (seconds)")

    return journey_times, in_elevator_times


def generate_passenger(time_step, building, mode="morning"):
    if mode == "random":
        origin, destination = random.sample(range(0, building.floors), 2)
    elif mode == "morning":
        origin = random.choice([*[0 for i in range(building.floors * 4)], *range(1, building.floors)])
        destination = random.choice([i for i in range(0, building.floors) if i != origin])
    elif mode == "evening":
        destination = random.choice([*[0 for i in range(building.floors * 9)], *range(1, building.floors)])
        origin = random.choice([i for i in range(0, building.floors) if i != destination])
    else:
        raise Exception("Incorrect mode supplied")
    return Passenger(origin, destination, time_step)


def run_iteration(elevator, building, algo, origins, destinations, total_passengers, draw_enabled):
    if draw_enabled:
        time.sleep(0.5)

    current_floor = elevator.position

    exit_passengers = elevator.exit_passengers()
    for p in exit_passengers:
        destinations[current_floor].remove(p)
        p.get_off = elevator.time
        p.complete_journey(elevator.time)

    enter_passengers = origins[current_floor].copy()

    occupant_destinations = [p.destination for p in elevator.occupants]

    take_all_passengers = False

    if len(set([p.direction for p in enter_passengers])) != 2:
        if not elevator.occupants:
            take_all_passengers = True
        else:
            for d in occupant_destinations:
                if np.sign(d - elevator.position) == -1 * elevator.direction:
                    take_all_passengers = True
                    break

    for p in enter_passengers:
        if len(elevator.occupants) == elevator.max_occupancy:
            break
        if elevator.directional_passengers:
            if p.direction == elevator.direction or elevator.position == 0 or elevator.position == building.floors - 1 or take_all_passengers:
                elevator.enter_passenger(p)
                p.get_on = elevator.time
                origins[current_floor].remove(p)
        else:
            elevator.enter_passenger(p)
            p.get_on = elevator.time
            origins[current_floor].remove(p)

    if draw_enabled:
        draw(building, origins, elevator, total_passengers)

    next_floor = algo.next_floor(building, elevator, origins, destinations)

    if next_floor == elevator.position:
        elevator.direction = -1 * elevator.direction

    elevator.move(next_floor)

    elevator.time += calculate_time(elevator, building, len(enter_passengers) + len(exit_passengers))


def calculate_time(elevator, building, n_passengers):
    storey_height = building.storey_height
    acceleration = elevator.acceleration
    max_speed = elevator.speed

    embark_disembark_time = n_passengers * elevator.embark_disembark_time

    distance_traveled = storey_height * abs(elevator.position - elevator.previous_floor)

    acceleration_distance = (max_speed ** 2) / (2 * acceleration)

    if acceleration_distance > distance_traveled:
        travel_time = 2 * math.sqrt((2 * distance_traveled) / acceleration)
    else:
        acceleration_time = (1 / 2) * (acceleration_distance) / max_speed
        max_speed_distance = distance_traveled - acceleration_distance
        max_speed_time = max_speed_distance / max_speed
        travel_time = 2 * acceleration_time + max_speed_time

    return embark_disembark_time + travel_time


def draw(building, origins, elevator, total_passengers):
    string = ""
    floors = building.floors

    for f in range(floors):
        string += "\n"
        if elevator.position == f:
            string += f"{''.join(' ' for i in range(elevator.max_occupancy - elevator.dropped_off_passengers))}{''.join('x' for i in range(elevator.dropped_off_passengers))}"
            if len(str(len(elevator.occupants))) == 2:
                string += f"|[{len(elevator.occupants)}]|"
            else:
                string += f"|[ {len(elevator.occupants)}]|"
        else:
            string += "".join(" " for i in range(elevator.max_occupancy))
            string += "|    |"
        string += "".join(["o" for i in range(len(origins[f]))])

    print(string)


def batch_test(config):
    tests = {}

    names = ["small_morning", "small_daytime", "small_evening", "large_morning", "large_daytime", "large_evening"]

    for name in names:
        test_config = config.copy()
        if "small" in name:
            test_config["max_occupancy"] = 6
            test_config["n_floors"] = 4
            test_config["n_passengers"] = 50
            if "daytime" in name:
                test_config["generate_range"] = (0, 1)
        elif "large" in name:
            test_config["max_occupancy"] = 12
            test_config["n_floors"] = 20
            test_config["n_passengers"] = 100
        tests[name] = test_config

    for name, test_config in tests.items():
        run_test(name, test_config)


def run_test(name, config):
    algos = [algo() for algo in config["algos"]]

    iterations = config["iterations"]

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

    save_config = config.copy()

    save_config["algos"] = [algo.__name__ for algo in config["algos"]]

    with open(f"output/{name}/config.json", 'w') as f:
        json.dump(save_config, f)

    charts(name, df_journey_times, df_in_elevator_times)
