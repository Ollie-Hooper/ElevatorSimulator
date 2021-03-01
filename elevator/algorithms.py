# Add your own algorithm here

class BasicAlgorithm:
    def __init__(self):
        # Drop parameters that you can modify here e.g. threshold for how many floors to move in one go without stopping
        # These are parameters that you would use to modify the behaviour of the next_floor function
        self.name = "BasicAlgorithm"
        self.only_pickup_directional_passengers = False

    def next_floor(self, building, elevator, origins, destinations):
        # All the properties of the elevator, passenger or building class can be used to determine the next floor along
        # with the origins and destinations dictionary.
        # These dictionaries have the floors of the building as keys and the values are a list of the passengers waiting
        # or wanting to go there

        if elevator.occupants:  # If there are people in the elevator
            return elevator.occupants[
                0].destination  # Just go to the floor of the destination of the first person in the list of occupants
        elif bool([x for x in destinations.values() if x != []]):  # If there are people waiting for the lift
            return [x for x in destinations.values() if x != []][0][0].origin  # Go to where the someone is waiting
        else:
            return round(building.floors / 2)  # Go to middle floor if no one is waiting/needs dropping off


class SimpleUpDown:  # Ollie
    def __init__(self):
        self.name = "SimpleUpDown"
        self.only_pickup_directional_passengers = False

    def next_floor(self, building, elevator, origins, destinations):
        current_direction = elevator.direction
        current_floor = elevator.position

        if not current_direction and current_floor == 0:
            return 1

        if current_floor == 0 or current_floor == building.floors - 1:
            return current_floor - current_direction
        else:
            return current_floor + current_direction


class ClosestFloor:  # Max
    def __init__(self):
        self.name = "ClosestFloor"
        self.only_pickup_directional_passengers = False

    def next_floor(self, building, elevator, origins, destinations):
        closest_floor_waiting = None
        current_closest = 1e10  # big number

        if not elevator.occupants and not bool([x for x in destinations.values() if x != []]):
            return 0

        if elevator.occupants:  # calculates closest drop off floor
            for passenger in elevator.occupants:
                closest_floor_destination = abs(elevator.position - passenger.destination)
                if closest_floor_destination < abs(elevator.position - current_closest):
                    current_closest = passenger.destination

        if len(elevator.occupants) != elevator.max_occupancy:  # Only go to pickup floor if lift is not full
            for floor, passengers_waiting in origins.items():  # calculates nearest passenger whos called the elevator
                if len(passengers_waiting) > 0:
                    closest_floor_waiting = abs(elevator.position - floor)
                    if closest_floor_waiting < abs(
                            elevator.position - current_closest):  # determines whether drop off or pick up is closer
                        current_closest = floor

        return current_closest


class NormalLift:  # Cameron
    def __init__(self):
        self.name = "NormalLift"
        self.only_pickup_directional_passengers = True

    def next_floor(self, building, elevator, origins, destinations):
        current_floor = elevator.position

        origins = {floor: [passenger for passenger in passengers if passenger.direction == elevator.direction] for
                   floor, passengers in origins.items() if passengers != []}
        destinations = {floor: [passenger for passenger in elevator.occupants if floor == passenger.destination] for
                        floor in range(building.floors)}
        destinations = {floor: passengers for floor, passengers in destinations.items() if passengers != []}

        if len(elevator.occupants) == elevator.max_occupancy:
            potentialStops = destinations
        else:
            potentialStops = {**origins, **destinations}

        if elevator.direction:
            current_direction = elevator.direction
        else:
            current_direction = 1

        try:
            lowestFloorAbove = min(i for i in potentialStops.keys() if i > current_floor)
        except:
            lowestFloorAbove = current_floor

        try:
            highestFloorBelow = max(i for i in potentialStops.keys() if i < current_floor)
        except:
            highestFloorBelow = current_floor

        if current_direction == 1:
            if any(a > current_floor for a in potentialStops.keys()):
                return lowestFloorAbove

            else:
                return highestFloorBelow

        elif current_direction == -1:
            if any(a < current_floor for a in potentialStops.keys()):
                return highestFloorBelow

            else:
                return lowestFloorAbove


class LongestWaited:  # Rachel
    def __init__(self):
        self.name = "LongestWaited"
        self.only_pickup_directional_passengers = False

    def next_floor(self, building, elevator, origins, destinations):
        # longest waited for elevator
        earliest_journey_start = 1e10
        longest_waited_floor = None

        for floor, passengers_waiting in origins.items():
            for passenger in passengers_waiting:
                if passenger.journey_start < earliest_journey_start:
                    earliest_journey_start = passenger.journey_start
                    longest_waited_floor = floor

        elevator_earliest_journey_start = 1e10
        elevator_longest_waited_floor = None

        for passenger in elevator.occupants:
            if passenger.journey_start < elevator_earliest_journey_start:
                elevator_earliest_journey_start = passenger.journey_start
                elevator_longest_waited_floor = passenger.destination

        if elevator.max_occupancy == len(elevator.occupants):
            return elevator_longest_waited_floor

        if not elevator.occupants and not bool([x for x in destinations.values() if x != []]):
            return 0

        if not elevator.occupants and bool([x for x in destinations.values() if x != []]):
            return longest_waited_floor
        else:
            if elevator_earliest_journey_start <= earliest_journey_start:
                return elevator_longest_waited_floor
            else:
                return longest_waited_floor


class PopularFloor:  # Conrad

    def __init__(self):
        self.name = "PopularFloor"
        self.only_pickup_directional_passengers = False

    def next_floor(self, building, elevator, origins, destinations):
        n_destinations_occupants = [0 for floor in range(
            building.floors)]  # Create an empty array of the correct length for the floors to be used for occupants of lift

        n_destinations_waiting_passengers = [0 for floor in range(
            building.floors)]  # Creates the same array as above, but to be used for passengers waiting for lift

        most_popular_destination_occupants = None  # Most Popular floor for passengers currently in the lift

        most_popular_destination_passengers = None  # Most Popular Floor for waiting passengers

        if not elevator.occupants and not bool([x for x in destinations.values() if x != []]):

            return round(
                building.floors / 2)  # If no one in elevator and no one waiting, go to middle floor ( i think )

        elif not elevator.occupants and bool(
                [x for x in destinations.values() if x != []]):  # If no occupants but people waiting then :

            for floor, passengers_waiting in origins.items():
                for passenger in passengers_waiting:
                    n_destinations_waiting_passengers[passenger.destination] += 1

            most_popular_destination_passengers = n_destinations_waiting_passengers.index(
                max(n_destinations_waiting_passengers))

            n_passengers_origin_for_destination = [0 for floor in range(building.floors)]

            for floor, passengers_waiting in origins.items():
                for passenger in passengers_waiting:
                    if passenger.destination == most_popular_destination_passengers:
                        n_passengers_origin_for_destination[passenger.origin] += 1

            most_popular_origin_for_destination = n_passengers_origin_for_destination.index(
                max(n_passengers_origin_for_destination))

            return most_popular_origin_for_destination
        else:  # Passengers in elevator
            for passenger in elevator.occupants:
                n_destinations_occupants[passenger.destination] += 1

            most_popular_destination_occupants = n_destinations_occupants.index(max(n_destinations_occupants))

            if elevator.max_occupancy == len(elevator.occupants):
                return most_popular_destination_occupants

            n_passengers_origin_for_destination = [0 for floor in range(building.floors)]

            for floor, passengers_waiting in origins.items():
                for passenger in passengers_waiting:
                    if passenger.destination == most_popular_destination_occupants:
                        n_passengers_origin_for_destination[passenger.origin] += 1

            for floor in range(elevator.position, most_popular_destination_occupants):
                if n_passengers_origin_for_destination[floor]:
                    return floor

            return most_popular_destination_occupants
