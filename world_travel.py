import pandas as pd
import numpy as np
from typing import List, Tuple
from src.helper import nearest_neighbors_algorithm, is_east, travel_time_calculator

def dfs_travel(cities, current_city, start_city, visited, total_hours, max_hours, path):
    if total_hours > max_hours:
        return None  # Exceeded time limit

    # If we've returned to London and visited enough cities, we're done
    if current_city['City'] == start_city['City'] and len(visited) > 1:
        return path, total_hours

    nearest_neighbors = nearest_neighbors_algorithm(cities)[current_city.name]

    for idx, (neighbor, distance) in enumerate(nearest_neighbors):
        if neighbor['City'] not in visited and is_east(current_city, neighbor):
            travel_time = travel_time_calculator(current_city, neighbor, idx)
            if total_hours + travel_time <= max_hours:
                # Explore the next city
                new_path = path + [neighbor['City']]
                new_visited = visited | {neighbor['City']}
                result = dfs_travel(
                    cities, neighbor, start_city, new_visited, total_hours + travel_time, max_hours, new_path
                )
                if result is not None:
                    return result  # Found a valid path

    # Backtrack
    return None


def travel_around_the_world(cities: pd.DataFrame, start_city_name: str, start_country: str, max_days: int = 80):
    start_city = cities[(cities['City'].str.lower() == start_city_name.lower()) &
                        (cities['Country'].str.lower() == start_country.lower())].iloc[0]

    max_hours = max_days * 24
    visited = {start_city['City']}
    path = [start_city['City']]
    total_hours = 0

    result = dfs_travel(cities, start_city, start_city, visited, total_hours, max_hours, path)

    if result is None:
        print("Failed to complete the trip within the allowed time.")
        return [], 0
    else:
        travel_path, total_hours = result
        print("Successfully traveled around the world!")
        return travel_path, total_hours / 24

"""def travel_around_the_world(cities: pd.DataFrame, start_city_name: str, start_country: str, max_days: int = 80) -> Tuple[List[str], int]:

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

            if (neighbor['City'] not in travel_path) and is_east(current_city, neighbor):
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
    return travel_path, total_hours/24"""


def AROUND_THE_WORLD_IN_80_DAYS(cities: pd.DataFrame) -> None:
    result, min_time = travel_around_the_world(cities, 'london', 'gb', 80)

    print("Possible within 80 days:", result)
    print(f"Minimum time taken:{round(min_time,2)} days")
    print(f"Limit: {80} days, {80*24} hours")



