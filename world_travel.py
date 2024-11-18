import pandas as pd
import numpy as np
from typing import List, Tuple
from src.helper import nearest_neighbors_algorithm, is_east, travel_time_calculator



def travel_around_the_world(cities: pd.DataFrame, start_city_name: str, start_country: str, max_days: int = 80) -> Tuple[List[str], int]:

    start_city = cities[(cities['City'].str.lower() == start_city_name.lower()) &
                        (cities['Country'].str.lower() == start_country.lower())].iloc[0]

    current_city = start_city
    travel_path = []

    max_hours = max_days * 24
    total_hours = 0

    while True:
        nearest_neighbors = nearest_neighbors_algorithm(cities)[current_city.name]

        next_city = None
        for idx, (neighbor, distance) in enumerate(nearest_neighbors):

            if (neighbor['City'] not in travel_path):
                travel_time = travel_time_calculator(current_city, neighbor, idx)
                if total_hours + travel_time <= max_hours:
                    next_city = neighbor
                    total_hours += travel_time
                    travel_path.append(neighbor['City'])
                    print(f"from {current_city.City} to {neighbor.City} took {travel_time} hours")
                    break

        if next_city is None or (next_city['City'] == start_city['City']):
            break

        current_city = next_city

    if travel_path[-1] != start_city['City']:
        print("Failed to complete the trip within the allowed time.")
    else:
        print("Successfully traveled around the world!")

    travel_path.insert(0, str(start_city.City))
    return travel_path, total_hours/24






