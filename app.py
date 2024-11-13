import streamlit as st
from world_travel import travel_around_the_world
import time
import plotly.graph_objects as go
import geopandas as gpd
import plotly.express as px

from src.helper import CitiesDataset

# Configure the page settings
st.set_page_config(layout="wide")

# Initialize session state for navigation if not exists
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Welcome"

# Custom CSS for styling
st.markdown("""
    <style>
    .stButton button {
        width: 100%;
        background-color: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 10px;
        border-radius: 5px;
    }
    .welcome-text {
        text-align: center;
        color: white;
        padding: 20px;
        border-radius: 10px;
        background-color: rgba(0, 0, 0, 0.5);
        margin: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Navigation menu at the top
menu_items = ["Welcome", "Experience the Journey", "See Your Travel on the Map", "Population Map"]
cols = st.columns(len(menu_items))
for idx, page in enumerate(menu_items):
    if cols[idx].button(page):
        st.session_state.current_page = page

cities_dataset = CitiesDataset('./worldcitiespop.csv')
cities_dataset.load_data()
cities = cities_dataset.get_data()

# Only show sidebar and calculate result if on Experience the Journey page
if st.session_state.current_page == "Experience the Journey":
    # Show sidebar only on Experience the Journey page
    with st.sidebar:
        st.title("Travel Around the World in 80 Days 🌍")
        start_city = st.text_input("Starting City", "London")
        start_country = st.text_input("Starting Country", "England")
        max_days = st.slider("Maximum Days", 1, 80, 80)

        # todo: add here st error messages regarding to start city and country options

    result, min_time = travel_around_the_world(cities, start_city.lower(), start_country.lower(), max_days)
    journey = result
else:
    # Default values for other pages if needed
    result = []
    min_time = 0

# Page content
if st.session_state.current_page == "Welcome":
    st.markdown(
        f"""
            <style>
            .stApp {{
                background-image: url("./wallpapers/world.webp");
                background-size: cover;
                background-position: center;
            }}
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
    st.title("Around the World in 80 Days 🌍")

    if st.sidebar.button("Start Journey"):
        # Calculate journey result and save it to session state
        result, min_time = travel_around_the_world(cities, start_city.lower(), start_country.lower(), max_days)
        st.session_state['journey'] = result
        st.session_state['min_time'] = min_time

        # Display the journey with animations
        image_placeholder = st.empty()
        plane_placeholder = st.empty()
        for city in result:
            plane_placeholder.image("./animations/plane.gif", caption="Flying to the next city...",
                                    use_container_width=True)
            time.sleep(1.5)
            plane_placeholder.empty()
            photo_url = f"./city_photos/{city}.jpg"
            image_placeholder.image(photo_url, caption=f"{city} photo", use_container_width=True)
            time.sleep(2)
            image_placeholder.empty()

        if result[-1] == start_city.lower():
            st.write("Journey complete!")
            st.write(f"Total travel time: {round(min_time, 2)} days")
            st.image("./situations/happy.jpg", use_container_width=True)
        else:
            st.write("Failed to travel the world.")
            st.image("./situations/unhappy.jpg", use_container_width=True)

elif st.session_state.current_page == "See Your Travel on the Map":
    st.title("Travel Path Map")
    st.write("View the journey across the world on a map.")
    journey = st.session_state.get('journey', None)  # Retrieve journey from session state
    if journey:
        ordered_travel_data = cities[cities['City'].isin(journey)]
        ordered_travel_data = ordered_travel_data.set_index('City').loc[journey].reset_index()
        lats = ordered_travel_data['Latitude'].tolist()
        lons = ordered_travel_data['Longitude'].tolist()

        fig = go.Figure(go.Scattermapbox(
            mode="markers+lines",
            lon=lons,
            lat=lats,
            marker={'size': 8},
            line=dict(width=2, color='blue'),
            text=ordered_travel_data['City'],
            hoverinfo="text"
        ))
        fig.update_layout(
            mapbox_style="carto-positron",
            mapbox_zoom=3,
            mapbox_center={"lat": lats[0], "lon": lons[0]},
            height=600
        )
        st.plotly_chart(fig)
    else:
        st.info("Please start a journey from the 'Experience the Journey' page first to see the travel path.")

elif st.session_state.current_page == "Population Map":
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