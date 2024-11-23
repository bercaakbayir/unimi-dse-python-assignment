import os
import time
import numpy as np
import streamlit as st
import plotly.express as px
from datetime import datetime
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from dotenv import load_dotenv

from src.helper import CitiesDataset
from world_travel import travel_around_the_world

load_dotenv()

DATA_FILE_PATH = os.getenv("DATA_FILE_PATH")
START_CITY = os.getenv("START_CITY")
START_COUNTRY = os.getenv("START_COUNTRY")
MAX_DAY_THRESHOLD = int(os.getenv("MAX_DAY_THRESHOLD"))


st.set_page_config(layout="wide", page_title="Around the World Adventure", page_icon="🌍")

st.markdown("""
    <style>
    .stButton button {
        background-color: #1E88E5;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        border: none;
        transition: background-color 0.3s ease;
    }
    .stButton button:hover {
        background-color: #1565C0;
    }
    .stProgress > div > div > div {
        background-color: #1E88E5;
    }
    .welcome-text {
        text-align: center;
        color: white;
        padding: 20px;
        border-radius: 10px;
        background-color: rgba(0, 0, 0, 0.5);
        margin: 20px;
    }
    .city-card {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .journey-summary {
        background-color: rgba(30, 136, 229, 0.1);
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for navigation if not exists
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Welcome"
if 'journey_started' not in st.session_state:
    st.session_state.journey_started = False


# Helper functions
def create_progress_bar(current, total):
    progress_bar = st.progress(0)
    progress_text = st.empty()
    progress_percentage = (current + 1) / total
    progress_bar.progress(progress_percentage)
    progress_text.text(f"Journey Progress: {current + 1}/{total} cities visited")
    return progress_bar, progress_text


def create_city_card(city_name, country, duration):
    st.markdown(f"""
        <div class="city-card">
            <h2 style='color: #1E88E5; margin: 0;'>{city_name.title()}</h2>
            <p style='color: #666; margin: 5px 0;'>{country.title()}</p>
            <p style='color: #333; margin: 5px 0;'>Time spent: {duration:.1f} days</p>
        </div>
    """, unsafe_allow_html=True)


def create_journey_summary(total_time, total_cities, start_city):
    st.markdown(f"""
        <div class="journey-summary">
            <h3 style='color: #1E88E5; margin: 0;'>Journey Summary</h3>
            <p style='font-size: 1.2em; margin: 10px 0;'>Starting from: {start_city.title()}</p>
            <p>Total Cities: {total_cities}</p>
            <p>Estimated Duration: {total_time:.1f} days</p>
        </div>
    """, unsafe_allow_html=True)


def create_transition_animation(animation_container):
    for _ in range(3):
        animation_container.markdown("🛫 Flying...")
        time.sleep(0.3)
        animation_container.markdown("✈️ Flying...")
        time.sleep(0.3)
        animation_container.markdown("🛬 Flying...")
        time.sleep(0.3)
        animation_container.empty()


# Navigation menu
menu_items = ["Welcome", "Experience the Journey", "See Your Travel on the Map", "General Statistics"]
cols = st.columns(len(menu_items))
for idx, page in enumerate(menu_items):
    if cols[idx].button(page):
        st.session_state.current_page = page

# Load cities dataset
cities_dataset = CitiesDataset(DATA_FILE_PATH)
cities_dataset.load_data()
cities = cities_dataset.get_data()

# Page content
if st.session_state.current_page == "Welcome":

    st.logo(
        "./images/logos/unimi-dse.png",
        size="large",
        link="https://www.unimi.it/en/education/master-programme/data-science-economics-dse",
    )

    st.markdown(
        """
        <style>
        .stApp {
            background-size: cover;
            background-position: center;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown("""
        <div class="welcome-text">
            <h1>Welcome to Around the World in 80 Days 🌍</h1>
            <p>Have you ever placed a bet on whether it is possible to travel around the world in 80 days? Your answer is on this website!</p>
            <p>Learn about the cities you will visit while creating the most suitable route for your world tour!</p>
            <p>Use the navigation menu above to:</p>
            <ul>
                <li>Experience your journey while creating your world tour route!</li>
                <li>Track your route on an interactive map</li>
                <li>Explore general statistics across the world</li>
            </ul>
            <p>Begin your adventure by selecting "Experience the Journey" above!</p>
        </div>
    """, unsafe_allow_html=True)

elif st.session_state.current_page == "Experience the Journey":
    st.title("Around the World Adventure 🌍")

    # Sidebar configuration
    with st.sidebar:
        st.markdown("""
            <div style='background-color: rgba(30, 136, 229, 0.1); padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
                <h2 style='color: #1E88E5; margin: 0;'>Journey Settings</h2>
            </div>
        """, unsafe_allow_html=True)

        start_city = st.text_input("Starting City", START_CITY)
        start_country = st.text_input("Starting Country", START_COUNTRY)
        max_days = st.slider("Maximum Days", 1, 80, MAX_DAY_THRESHOLD)

        if st.button("Start Journey"):
            st.session_state.journey_started = True
            st.session_state.journey_time = datetime.now()

    if st.session_state.journey_started:
        # Calculate journey

        try:
            result, min_time = travel_around_the_world(cities, start_city.lower(), start_country.lower(), max_days)
        except IndexError:
            st.error('You entered the Starting City and/or Starting Country parameter incorrectly.')
        except Exception as e:
            st.error('Sorry, we are not able to service you right now! Thank you for your patience.')


        # Create display containers
        journey_container = st.container()
        animation_container = st.empty()
        info_container = st.container()

        with journey_container:
            create_journey_summary(min_time, len(result), start_city)

        # Display journey progress
        progress_bar, progress_text = create_progress_bar(0, len(result))

        # Animate through cities
        for idx, city in enumerate(result):
            # Update progress
            progress_bar.progress((idx + 1) / len(result))
            progress_text.text(f"Journey Progress: {idx + 1}/{len(result)} cities visited")

            create_transition_animation(animation_container)

            # Display city image
            try:
                photo_path = f"./images/city_photos/{city.lower()}.jpg"
                if os.path.exists(photo_path):
                    animation_container.image(photo_path, caption=f"Welcome to {city.title()}",
                                              use_container_width=True)
                else:
                    st.write(city.lower())
                    continue
            except Exception as e:
                animation_container.error(f"Error displaying image: {str(e)}")

            time.sleep(2)

        if result[-1].lower() == start_city.lower():
            st.session_state.journey = result  # Store the journey data in session state
            st.success(f"""
                🎉 Congratulations! Journey Complete!
                Total time: {min_time:.1f} days
                Cities visited: {len(result)}
                Starting point: {start_city.title()}
            """)
            journey_duration = datetime.now() - st.session_state.journey_time
            st.info(f"Real-time journey presentation duration: {journey_duration.seconds} seconds")
        else:
            st.error(f"☹️Journey completed in the given time...")

        # In "See Your Travel on the Map" section
elif st.session_state.current_page == "See Your Travel on the Map":
    st.title("Travel Path Map")
    st.write("View the journey across the world on a map.")

    if st.session_state.journey_started and 'journey' in st.session_state and st.session_state.journey:
        journey = st.session_state.journey  # Retrieve journey data from session state
        ordered_travel_data = cities[cities['City'].isin(journey)]
        ordered_travel_data = ordered_travel_data.set_index('City').loc[journey].reset_index()

        fig = go.Figure(go.Scattermapbox(
            mode="markers+lines",
            lon=ordered_travel_data['Longitude'].tolist(),
            lat=ordered_travel_data['Latitude'].tolist(),
            marker={'size': 8},
            line=dict(width=2, color='blue'),
            text=ordered_travel_data['City'],
            hoverinfo="text"
        ))

        fig.update_layout(
            mapbox_style="carto-positron",
            mapbox_zoom=3,
            mapbox_center={"lat": ordered_travel_data['Latitude'].iloc[0],
                            "lon": ordered_travel_data['Longitude'].iloc[0]},
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Please start a journey from the 'Experience the Journey' page first to see the travel path.")


elif st.session_state.current_page == "General Statistics":

    cities_dataset = CitiesDataset(DATA_FILE_PATH, min_population=0)
    cities_dataset.load_data()
    cities = cities_dataset.get_data()

    st.title("City Population Statistics")

    st.header("Summary Statistics")
    selected_country = st.selectbox("Select Country", options=cities['Country'].unique())
    country_data = cities[cities['Country'] == selected_country]

    total_cities = len(country_data)
    sum_population = np.sum(country_data['Population'])
    max_population = np.max(country_data['Population'])
    min_population = np.min(country_data['Population'])
    median_population = np.median(country_data['Population'])
    std_population = np.std(country_data['Population'])
    top_cities = country_data.sort_values('Population', ascending=False).head(3)


    # Display metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Settlements", f"{total_cities}")
    col2.metric("Total Population", f"{sum_population}")
    col3.metric("Max Population", f"{max_population}")

    col4, col5 = st.columns(2)
    col4.metric("Median Population", f"{median_population:.2f}")
    col5.metric("Std. Deviation", f"{std_population:.2f}")

    st.subheader("Top 3 Most Populous Cities")
    for index, city in top_cities.iterrows():
        st.write(f"{city['AccentCity']} : {city['Population']:,}")

    # Filters
    st.sidebar.header("Filters")
    countries = st.sidebar.multiselect("Select Country", options=cities['Country'].unique(),
                                       default=cities['Country'].unique())
    population_range = st.sidebar.slider(
        "Population Range",
        int(np.min(cities['Population'])),
        int(np.max(cities['Population'])),
        (int(np.min(cities['Population'])), int(np.max(cities['Population'])))
    )

    filtered_data = cities[(cities['Country'].isin(countries)) & (cities['Population'].between(*population_range))]

    # Data Overview
    st.header("Filtered Data Overview")
    st.write(f"Filtered Cities: {len(filtered_data)}")
    st.dataframe(filtered_data)

    # Population Distribution
    st.header("Population Distribution")
    fig = px.histogram(filtered_data, x='Population', nbins=50, title="Population Distribution")
    st.plotly_chart(fig)

    # Top Cities by Population
    st.header("Top Cities by Population")
    top_cities = filtered_data.sort_values('Population', ascending=False).head(10)
    fig = px.bar(top_cities, x='City', y='Population', title="Top 10 Cities by Population")
    st.plotly_chart(fig)

    # Geographic Distribution
    st.header("City Locations")
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot the scatter points for city locations
    ax.scatter(
        filtered_data['Longitude'],
        filtered_data['Latitude'],
        s=filtered_data['Population'] / filtered_data['Population'].max() * 100,  # Normalize size
        alpha=0.6,
        c='red',
        label='Cities'
    )

    # Add grid, labels, and title
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Geographic Distribution of Cities", fontsize=14)
    ax.grid(True)

    # Add legend
    ax.legend(loc='lower left')

    # Display the static map
    st.pyplot(fig)




