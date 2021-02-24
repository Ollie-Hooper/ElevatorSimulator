import numpy as np


class Elevator:
    def __init__(self, max_occupancy=10, directional_passengers=False, acceleration=1.5, speed=6.7,
                 embark_disembark_time=1):
        # These can all be used by the algorithm to determine the next floor
        self.position = 0  # Current floor of elevator
        self.previous_floor = 0  # Previous floor
        self.previous_stop_timestep = 0  # Timestep of previous stop
        self.dropped_off_passengers = 0  # Number of passengers dropped off in this stop
        self.floors_travelled = 0  # Total number of floors it has travelled up and down
        self.max_occupancy = max_occupancy  # Max occupancy of the lift
        self.directional_passengers = directional_passengers  # Whether to pick up passengers only going in the same direction or not
        self.acceleration = acceleration  # Acceleration/deceleration of the lift
        self.speed = speed  # Speed of the lift
        self.embark_disembark_time = embark_disembark_time
        self.occupants = []  # List of passengers (Passenger class) currently in the lift
        self.direction = 0  # Direction the lift last travelled (+1 up, -1 down)
        self.journey = [0]  # History of floors it has visited and stopped at
        self.stops = 0  # Number of stops made

        self.time = 0  # Tracking time in seconds

    def enter_passenger(self, passenger):
        if len(self.occupants) == self.max_occupancy:
            return "Max occupancy reached"

        self.occupants.append(passenger)

    def exit_passengers(self):
        exit_passengers = []
        for i, passenger in enumerate(self.occupants):
            if passenger.destination == self.position:
                exit_passengers.append(self.occupants.pop(i))
        self.dropped_off_passengers = len(exit_passengers)
        return exit_passengers

    def move(self, destination):
        self.previous_floor = self.position
        self.previous_stop_timestep = self.floors_travelled
        self.stops += 1
        self.direction = np.sign(destination - self.position)
        self.floors_travelled += abs(destination - self.position)
        self.position = destination
        self.journey.append(self.position)


class Building:
    def __init__(self, floors, storey_height=4):
        # These can all be used by the algorithm to determine the next floor
        self.floors = floors
        self.storey_height = storey_height


class Passenger:
    def __init__(self, origin, destination, journey_start):
        # These can all be used by the algorithm to determine the next floor
        self.origin = origin  # Floor they start on
        self.destination = destination  # Floor they want to get to
        self.direction = 1 if origin < destination else -1
        self.journey_start = journey_start  # How many floors the lift has travelled since the start of the simulation when this passenger is created
        self.journey_end = None  # How many floors the lift has travelled since the start of the simulation when this passenger reaches its destination
        self.journey_time = None  # Total journey time since "pressing button for lift" to destination
        self.get_on = None  # How many floors the lift has travelled since the start of the simulation when this passenger gets on the lift
        self.get_off = None  # How many floors the lift has travelled since the start of the simulation when this passenger gets off the lift - currently same as self.journey_end
        self.time_in_elevator = None  # Time spent in elevator (self.get_off - self.get_on)

    def complete_journey(self, journey_end):
        self.journey_end = journey_end
        self.journey_time = self.journey_end - self.journey_start
        self.time_in_elevator = self.get_off - self.get_on
