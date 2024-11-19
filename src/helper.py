import math
import os

import pandas as pd
from typing import List, Tuple, Dict
from dotenv import load_dotenv
import json

load_dotenv()

MINIMUM_POPULATION = int(os.getenv("MINIMUM_POPULATION"))
EXCLUDED_CITY = os.getenv("EXCLUDED_CITY")
COUNTRIES_DICT = os.getenv("COUNTRIES")


if COUNTRIES_DICT:
    try:
        countries = json.loads(COUNTRIES_DICT)
    except json.JSONDecodeError:
        print("The environment variable is not a valid JSON string.")
else:
    print("Environment variable 'MY_DICT' is not set.")

class CitiesDataset:
    def __init__(self, file_path, min_population=MINIMUM_POPULATION, exclude_city=EXCLUDED_CITY):
        self.file_path = file_path
        self.min_population = min_population
        self.exclude_city = exclude_city.lower()
        self.countries = countries
        self.data = None

    def load_data(self):
        """Load the dataset from a CSV file."""
        self.data = pd.read_csv(self.file_path, dtype={3: str})
        self.data = self.data.dropna()
        self.transform_columns()
        self.filter_data()

    def transform_columns(self):
        """Replace country codes with full country names."""
        self.data['Country'] = self.data['Country'].replace(self.countries)
        self.data['Population'] = self.data['Population'].astype('int')

    def filter_data(self):
        """Filter cities based on population and exclude specified city."""
        self.data = self.data[self.data['City'].str.lower() != self.exclude_city]
        self.data = self.data[self.data['Population'] > self.min_population]

    def get_data(self):
        """Return the processed dataset."""
        if self.data is None:
            self.load_data()
        return self.data


def haversine(lat1, lon1, lat2, lon2):
    radius = 6371  # Earth radius in kilometers

    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)

    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad

    # Haversine formula
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = radius * c
    return distance


def travel_time_calculator(from_city, to_city, neighbor_idx):

    base_time = {
        0: 2,
        1: 4,
        2: 8
    }

    if neighbor_idx not in base_time:
        raise ValueError(f"Invalid neighbor index: {neighbor_idx}")

    time = base_time[neighbor_idx]  # Expecting only 3 neighbors (0, 1, 2)

    if from_city.Country != to_city.Country:
        time += 2
    if to_city.Population > 200000:
        time += 2

    return time


def is_east(from_city: pd.Series, to_city: pd.Series) -> bool:
    """Check if travel is eastward, accounting for longitude wrap-around."""

    def antimeridean(longitude):
        if longitude >= 0:
            return longitude - 180
        elif longitude < 0:
            return longitude + 180

    lon1, lon2 = from_city['Longitude'], to_city['Longitude']

    if lon1 > 0 and lon1 < 90:
        if (lon2 > lon1 and lon2 < 180) or (lon2 > -180 and lon2 < antimeridean(lon1)):
            return True
        else:
            return False
    elif (lon1 > 90) and (lon1 < 180):
        if ((lon2 > lon1) and (lon2 < 180)) or ((lon2 < antimeridean(lon1)) and (lon2 > -180)):
            return True
        else:
            return False
    elif (lon1 > -180) and (lon1 < -90):
        if (lon2 > lon1 and lon2 < 0) or ((lon2 > 0) and (lon2 < antimeridean(lon1))):
            return True
        else:
            return False
    elif lon1 > -90 and lon1 < 0:
        if (lon2 > lon1 and lon2 < 0) or (lon2 > 0 and lon2 < antimeridean(lon1)):
            return True
        else:
            return False
    else:
        print("wrong calculation in finding eastward city")


def nearest_neighbors_algorithm(cities: pd.DataFrame) -> Dict[int, List[Tuple[pd.Series, float]]]:
    """Compute exactly 3 nearest eastward neighbors for each city."""
    neighbors = {}
    for idx, city in cities.iterrows():
        distances = []
        for other_idx, other_city in cities.iterrows():
            if idx != other_idx and is_east(city, other_city):
                dist = haversine(
                    city['Latitude'], city['Longitude'],
                    other_city['Latitude'], other_city['Longitude']
                )
                distances.append((other_city, dist))

        # Sort by distance and take exactly 3 eastward neighbors
        distances.sort(key=lambda x: x[1])
        neighbors[idx] = distances[:3]  # Limiting to only 3 neighbors
    return neighbors





