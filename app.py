import streamlit as st
from world_travel import travel_around_the_world
import time
import plotly.graph_objects as go
import geopandas as gpd
import plotly.express as px
import os
from datetime import datetime
from src.helper import CitiesDataset

# Configure the page settings
st.set_page_config(layout="wide", page_title="Around the World Adventure", page_icon="🌍")

# Custom CSS for styling
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
menu_items = ["Welcome", "Experience the Journey", "See Your Travel on the Map", "Population Map"]
cols = st.columns(len(menu_items))
for idx, page in enumerate(menu_items):
    if cols[idx].button(page):
        st.session_state.current_page = page

# Load cities dataset
cities_dataset = CitiesDataset('./worldcitiespop.csv')
cities_dataset.load_data()
cities = cities_dataset.get_data()

# Page content
if st.session_state.current_page == "Welcome":
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("./wallpapers/world.webp");
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
            <p>Embark on an extraordinary journey around the globe, following in the footsteps of Phileas Fogg!</p>
            <p>Use the navigation menu above to:</p>
            <ul>
                <li>Experience your journey through city photos</li>
                <li>Track your route on an interactive map</li>
                <li>Explore population data across the world</li>
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

        start_city = st.text_input("Starting City", "London")
        start_country = st.text_input("Starting Country", "England")
        max_days = st.slider("Maximum Days", 1, 80, 80)

        if st.button("Start Journey"):
            st.session_state.journey_started = True
            st.session_state.journey_time = datetime.now()

    if st.session_state.journey_started:
        # Calculate journey
        result, min_time = travel_around_the_world(cities, start_city.lower(), start_country.lower(), max_days)

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
                photo_path = f"./city_photos/{city.lower()}.jpg"
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

elif st.session_state.current_page == "Population Map":
    # Population map implementation remains the same as your original code
    cities_dataset = CitiesDataset('./worldcitiespop.csv', min_population=100000)
    cities_dataset.load_data()
    cities = cities_dataset.get_data()

    world_geojson = gpd.read_file("./ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp")
    world_geojson = world_geojson.merge(cities, how="left", left_on="ADMIN", right_on="Country")

    fig = px.choropleth(
        world_geojson,
        geojson=world_geojson.geometry,
        locations=world_geojson.Country,
        color="Population",
        color_continuous_scale="Viridis",
        title="Population Distribution by Country",
        labels={'Population': 'Country Population'},
        projection="mercator"
    )

    fig.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Explore Population by Country")
    selected_country = st.selectbox("Select a Country", cities['Country'].unique())

    if selected_country:
        country_geojson = world_geojson[world_geojson['Country'] == selected_country]
        country_cities = cities[cities['Country'] == selected_country]

        fig_country = px.choropleth(
            country_geojson,
            geojson=country_geojson.geometry,
            locations=country_geojson.index,
            color="Population",
            color_continuous_scale="Viridis",
            labels={'Population': 'Country Population'},
            title=f"Population in {selected_country}"
        )

        fig_country.update_geos(fitbounds="locations", visible=False)

        fig_country.add_scattergeo(
            lon=country_cities['Longitude'],
            lat=country_cities['Latitude'],
            text=country_cities['City'] + ": " + country_cities['Population'].astype(str),
            marker=dict(
                size=country_cities['Population'] / country_cities['Population'].max() * 50,
                color=country_cities['Population'],
                colorscale="Reds",
                showscale=True,
                colorbar_title="City Population"
            ),
            name="Cities"
        )

        st.plotly_chart(fig_country, use_container_width=True)
        st.write(f"### Population Statistics for {selected_country}")
        country_population = cities[cities['Country'] == selected_country]['Population'].sum()
        st.metric(label="Total Population", value=f"{country_population:,}")