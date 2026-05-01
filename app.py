import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="UK Road Accidents Dashboard",
    page_icon="🚗",
    layout="wide"
)

# =========================
# Load Data
# =========================
df = pd.read_csv("merged_road_safety_data.csv", low_memory=False)
df.columns = df.columns.str.strip()

# Heatmap file
try:
    acc_df = pd.read_csv("accidents_clean.csv", low_memory=False)
    acc_df.columns = acc_df.columns.str.strip()
except:
    acc_df = None

# =========================
# Prepare Year Column
# =========================
if "Year_x" in df.columns:
    df["Year"] = df["Year_x"]
elif "Year_y" in df.columns:
    df["Year"] = df["Year_y"]
elif "Year" not in df.columns:
    st.error("No Year column found.")
    st.write(df.columns.tolist())
    st.stop()

df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
df = df.dropna(subset=["Year"])
df["Year"] = df["Year"].astype(int)

# =========================
# Title
# =========================
st.title("🚗 UK Road Accidents Analysis Dashboard")

st.markdown("""
### 📊 Project Overview
This dashboard analyzes UK road accident patterns using historical road safety data.  
It highlights accident trends based on year, severity, weather, road surface, lighting, speed limit, driver age, and vehicle behavior.
""")

# =========================
# Sidebar Filters
# =========================
st.sidebar.header("Filters")

year_filter = st.sidebar.multiselect(
    "Select Year",
    sorted(df["Year"].dropna().unique()),
    default=sorted(df["Year"].dropna().unique())
)

severity_filter = st.sidebar.multiselect(
    "Select Severity",
    sorted(df["Severity_Label"].dropna().unique()),
    default=sorted(df["Severity_Label"].dropna().unique())
)

filtered_df = df[
    (df["Year"].isin(year_filter)) &
    (df["Severity_Label"].isin(severity_filter))
]

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# =========================
# KPIs
# =========================
most_common = filtered_df["Severity_Label"].mode()[0]
peak_year = filtered_df.groupby("Year").size().idxmax()
fatal_count = len(filtered_df[filtered_df["Severity_Label"] == "Fatal"])

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Records", f"{len(filtered_df):,}")
col2.metric("Fatal Accidents", f"{fatal_count:,}")
col3.metric("Most Common Severity", most_common)
col4.metric("Peak Accident Year", peak_year)

st.divider()

# =========================
# Main Charts
# =========================
col1, col2 = st.columns(2)

with col1:
    year_data = filtered_df.groupby("Year").size().reset_index(name="Accidents")
    fig = px.line(
        year_data,
        x="Year",
        y="Accidents",
        markers=True,
        title="Number of Accidents by Year"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    severity_data = filtered_df["Severity_Label"].value_counts().reset_index()
    severity_data.columns = ["Severity", "Accidents"]
    fig = px.bar(
        severity_data,
        x="Severity",
        y="Accidents",
        color="Severity",
        title="Accidents by Severity"
    )
    st.plotly_chart(fig, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    if "Weather_Conditions" in filtered_df.columns:
        weather_data = filtered_df["Weather_Conditions"].value_counts().head(10).reset_index()
        weather_data.columns = ["Weather", "Accidents"]
        fig = px.bar(
            weather_data,
            x="Accidents",
            y="Weather",
            orientation="h",
            title="Top Weather Conditions"
        )
        st.plotly_chart(fig, use_container_width=True)

with col4:
    if "Road_Surface_Conditions" in filtered_df.columns:
        surface_data = filtered_df["Road_Surface_Conditions"].value_counts().reset_index()
        surface_data.columns = ["Road Surface", "Accidents"]
        fig = px.bar(
            surface_data,
            x="Accidents",
            y="Road Surface",
            orientation="h",
            title="Accidents by Road Surface Conditions"
        )
        st.plotly_chart(fig, use_container_width=True)

col5, col6 = st.columns(2)

with col5:
    if "Light_Conditions" in filtered_df.columns:
        light_data = filtered_df["Light_Conditions"].value_counts().reset_index()
        light_data.columns = ["Light Conditions", "Accidents"]
        fig = px.bar(
            light_data,
            x="Accidents",
            y="Light Conditions",
            orientation="h",
            title="Accidents by Light Conditions"
        )
        st.plotly_chart(fig, use_container_width=True)

with col6:
    if "Urban_or_Rural_Area" in filtered_df.columns:
        area_data = filtered_df["Urban_or_Rural_Area"].value_counts().reset_index()
        area_data.columns = ["Area", "Accidents"]
        fig = px.bar(
            area_data,
            x="Area",
            y="Accidents",
            color="Area",
            title="Urban vs Rural Accidents"
        )
        st.plotly_chart(fig, use_container_width=True)

col7, col8 = st.columns(2)

with col7:
    if "Speed_limit" in filtered_df.columns:
        speed_data = filtered_df.groupby(
            ["Speed_limit", "Severity_Label"]
        ).size().reset_index(name="Accidents")

        fig = px.bar(
            speed_data,
            x="Speed_limit",
            y="Accidents",
            color="Severity_Label",
            barmode="group",
            title="Accident Severity by Speed Limit"
        )
        st.plotly_chart(fig, use_container_width=True)

with col8:
    if "Age_Band_of_Driver" in filtered_df.columns:
        age_data = filtered_df["Age_Band_of_Driver"].value_counts().head(10).reset_index()
        age_data.columns = ["Driver Age Band", "Accidents"]

        fig = px.bar(
            age_data,
            x="Accidents",
            y="Driver Age Band",
            orientation="h",
            title="Driver Age Band Involved in Accidents"
        )
        st.plotly_chart(fig, use_container_width=True)

# =========================
# Heatmap from accidents_clean.csv
# =========================
st.divider()
st.subheader("Accidents Heatmap by Day of Week and Hour")

if acc_df is not None and "Day_of_Week" in acc_df.columns and "Hour" in acc_df.columns:
    heatmap_data = acc_df.pivot_table(
        index="Day_of_Week",
        columns="Hour",
        values="Accident_Index",
        aggfunc="count",
        fill_value=0
    )

    fig = px.imshow(
        heatmap_data,
        title="Accidents Heatmap by Day of Week and Hour",
        labels=dict(x="Hour", y="Day of Week", color="Accidents"),
        aspect="auto"
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Heatmap needs accidents_clean.csv with Day_of_Week and Hour columns.")

# =========================
# Additional Notebook Charts
# =========================
st.divider()
st.subheader("Additional Analysis Charts")

col9, col10 = st.columns(2)

with col9:
    if "Vehicle_Manoeuvre" in filtered_df.columns:
        manoeuvre_data = filtered_df["Vehicle_Manoeuvre"].value_counts().head(10).reset_index()
        manoeuvre_data.columns = ["Vehicle Manoeuvre", "Count"]

        fig = px.bar(
            manoeuvre_data,
            x="Count",
            y="Vehicle Manoeuvre",
            orientation="h",
            title="Top Vehicle Manoeuvres Involved in Accidents"
        )
        st.plotly_chart(fig, use_container_width=True)

with col10:
    if "Vehicle_Type" in filtered_df.columns:
        vehicle_type_data = filtered_df["Vehicle_Type"].value_counts().head(10).reset_index()
        vehicle_type_data.columns = ["Vehicle Type", "Count"]

        fig = px.bar(
            vehicle_type_data,
            x="Count",
            y="Vehicle Type",
            orientation="h",
            title="Top Vehicle Types Involved in Accidents"
        )
        st.plotly_chart(fig, use_container_width=True)

col11, col12 = st.columns(2)

with col11:
    if "Sex_of_Driver" in filtered_df.columns:
        sex_data = filtered_df["Sex_of_Driver"].value_counts().reset_index()
        sex_data.columns = ["Sex of Driver", "Count"]

        fig = px.pie(
            sex_data,
            names="Sex of Driver",
            values="Count",
            title="Accidents by Sex of Driver"
        )
        st.plotly_chart(fig, use_container_width=True)

with col12:
    if "Skidding_and_Overturning" in filtered_df.columns:
        skid_data = filtered_df["Skidding_and_Overturning"].value_counts().head(10).reset_index()
        skid_data.columns = ["Skidding / Overturning", "Count"]

        fig = px.bar(
            skid_data,
            x="Count",
            y="Skidding / Overturning",
            orientation="h",
            title="Skidding and Overturning Cases"
        )
        st.plotly_chart(fig, use_container_width=True)

# =========================
# Top Accident Locations
# =========================
st.divider()

if "Junction_Location" in filtered_df.columns:
    st.subheader("Top Accident Locations")

    loc_data = filtered_df["Junction_Location"].value_counts().head(10).reset_index()
    loc_data.columns = ["Location", "Accidents"]

    fig = px.bar(
        loc_data,
        x="Accidents",
        y="Location",
        orientation="h",
        title="Top 10 Accident Locations"
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================
# Key Insights
# =========================
st.divider()
st.subheader("Key Insights")

st.write(f"""
- Total accident records analyzed: **{len(filtered_df):,}**
- The most common accident severity is **{most_common}**.
- The year with the highest number of accident records is **{peak_year}**.
- Fatal accident records in the selected data: **{fatal_count:,}**.
- Urban areas show higher accident counts than rural areas.
- Dry road surfaces have the highest number of accidents because they are the most common condition, not necessarily the most dangerous.
- Lighting, weather, road surface, speed limit, driver age, and vehicle manoeuvres are important factors in understanding accident patterns.
""")

# =========================
# Dataset Preview
# =========================
st.divider()
st.subheader("Dataset Preview")
st.dataframe(filtered_df.head(30))