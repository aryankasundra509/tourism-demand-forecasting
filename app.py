import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config("Tourism Analytics Dashboard", page_icon="🌍", layout="wide", initial_sidebar_state="expanded")

@st.cache_data  # data - for data like (CSV, DataFrame)
def load_data():
    df = pd.read_csv("travel_data.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = load_data()

with st.sidebar:
    st.header("🌍 Tourism Analytics")

    # Option Menu
    selected = option_menu(menu_title="Main Menu", 
                           options=["Dataset", "Overview", "Demand & Trends", "Overcrowding Risk", "Data Assistant"],
                           icons=["table", "bar-chart-fill", "graph-up-arrow", "exclamation-triangle-fill", "robot"],
                           menu_icon="cast",
                           styles={"nav-link-selected": {"background-color": "#1568d3"}},
                           default_index=0)
    
    st.divider()

    # Global Filtering
    if selected != "Dataset":
        st.header("🔽 Global Filters")

        # 1. Year fileter
        years = ["All"] + sorted(df["Year"].unique().tolist())
        sel_year = st.selectbox("📅 Year", years)

        # 2. Zone Filter
        zones = ["All"] + sorted(df["Zone"].unique().tolist())
        sel_zone = st.selectbox("🌍 Zone", zones)

        # 3. State filter - Based on zone
        if sel_zone == "All":
            states = ["All"] + sorted(df["Location_State"].unique().tolist())
        else:
            states = ["All"] + sorted(
                df[df["Zone"] == sel_zone]["Location_State"].unique().tolist())
        sel_state = st.selectbox("📍 State", states)

        # 4. Season Filter
        seasons = ["All"] + sorted(df["Season"].unique().tolist())
        sel_season = st.selectbox("🌤️ Season", seasons)

        # 5. Tourist Type
        tourist_types = ["All"] + sorted(df["Tourist_Type"].unique().tolist())
        sel_tourist = st.selectbox("👤 Tourist Type", tourist_types)

        # ── Filter Apply Logic ──
        filtered_df = df.copy()


        if sel_year != "All":
            filtered_df = filtered_df[filtered_df["Year"] == int(sel_year)]
        if sel_zone != "All":
            filtered_df = filtered_df[filtered_df["Zone"] == sel_zone]
        if sel_state != "All":
            filtered_df = filtered_df[filtered_df["Location_State"] == sel_state]
        if sel_season != "All":
            filtered_df = filtered_df[filtered_df["Season"] == sel_season]
        if sel_tourist != "All":
            filtered_df = filtered_df[filtered_df["Tourist_Type"] == sel_tourist]

        # Filter summary — user know which filters are active
        active = sum([
            sel_year != "All", sel_zone != "All",
            sel_state != "All", sel_season != "All", sel_tourist != "All"
        ])
        if active > 0:
            st.markdown(f"✅ `{active}` filter(s) active — `{len(filtered_df):,}` rows")
        else:
            st.markdown(f"📊 Showing all `{len(filtered_df):,}` rows")

    else:
        filtered_df = df.copy()  # Dataset page ko raw data chahiye


# Page Routing - Means each page have different files
if selected == "Dataset":
    st.title("🗺️ AI-Based Tourism Demand Forecasting & Overcrowding Predicition System")
    st.header("📂 Dataset Explorer")

    # ── SECTION 1: TOP METRICS ──────────────────────────
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Rows",  f"{df.shape[0]:,}")
    c2.metric("Total Columns",  df.shape[1])
    c3.metric("Missing Values", f"{df.isna().sum().sum():,}")
    c4.metric("Unique Places",  f"{df['Place_Name'].nunique():,}")

    st.divider()

    # ── SECTION 2: FILTERS ──────────────────────────────
    # User choose a colums
    st.markdown("#### 🗂️ Select Columns to Display")
    sel_cols = st.multiselect("Choose Columns", options = df.columns.tolist(), default= df.columns.tolist())
    
    if not sel_cols:
        st.warning("⚠️ Please select at least one column to display.")
        st.stop()

    work_df = df[sel_cols]

    # Search box to find any value from entire dataset
    st.markdown("#### 🔍 Search Dataset")
    search_val = st.text_input("Type any value to search across all columns")

    if search_val:
        work_df = work_df[
            work_df.astype(str).apply(lambda row: row.str.contains(search_val, case=False).any(), axis=1)]

    # Column Filter
    st.markdown("#### 🎚️ Column Filter")
    fc1, fc2 = st.columns(2)

    with fc1:
        filter_col = st.selectbox("Select Column to Filter", work_df.columns.tolist())
    with fc2:
        filter_val = st.selectbox("Select Value", ["--None--"] + work_df[filter_col].dropna().unique().tolist())
    
    if filter_val != "--None--":
        work_df = work_df[work_df[filter_col].astype(str) == str(filter_val)]

    st.divider()

    # ── SECTION 3: DATA TABLE ───────────────────────────

    st.markdown("#### 📋 Data Preview")

    row_count = st.slider("Number of rows to display", 10, min(500, len(work_df)), 20)
    st.dataframe(work_df.head(row_count), use_container_width=True, height=400)

    # Show full Dataset
    if st.checkbox("Show Full Dataset"):
        st.dataframe(work_df, use_container_width=True)

    st.divider()

    # ── SECTION 4: COLUMN STATISTICS ────────────────────
    st.markdown("#### 📊 Column Statistics")

    # Selected only numeric columns
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()

    stat_col = st.selectbox("Select Numeric Columns", numeric_cols)

    # Stats in cards
    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("Mean",    f"{work_df[stat_col].mean():,.2f}"   if stat_col in work_df.columns else "N/A")
    s2.metric("Median",  f"{work_df[stat_col].median():,.2f}" if stat_col in work_df.columns else "N/A")
    s3.metric("Min",     f"{work_df[stat_col].min():,.2f}"    if stat_col in work_df.columns else "N/A")
    s4.metric("Max",     f"{work_df[stat_col].max():,.2f}"    if stat_col in work_df.columns else "N/A")
    s5.metric("Std Dev", f"{work_df[stat_col].std():,.2f}"    if stat_col in work_df.columns else "N/A")

    st.divider()

    # ── SECTION 5: DOWNLOAD ─────────────────────────────
    st.markdown("#### ⬇️ Download Data")

    csv = work_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download Filtered Dataset as CSV", data=csv, file_name="filtered_tourism_data.csv", mime="text/csv"
    )

elif selected == "Overview":
    st.header("📊 Tourism Overview")

    if filtered_df.empty:
        st.warning("⚠️ No data for selected filters. Please adjust filters.")
        st.stop()

    # KPI Cards
    total_visitors = filtered_df["Visitors_Count"].sum()
    total_revenue  = filtered_df["Revenue"].sum()
    avg_ticket     = filtered_df[filtered_df["Ticket_Price"] > 0]["Ticket_Price"].mean()
    avg_rating     = filtered_df["Rating"].mean()
    unique_places  = filtered_df["Place_Name"].nunique()

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("🧳 Total Visitors",   f"{total_visitors:,.0f}")
    k2.metric("💰 Total Revenue",    f"₹{total_revenue:,.0f}")
    k3.metric("🎟️ Avg Ticket Price", f"₹{avg_ticket:,.0f}")
    k4.metric("⭐ Avg Rating",       f"{avg_rating:.2f} / 5.0")
    k5.metric("🏛️ Unique Places",    f"{unique_places:,}")

    st.divider()

    # Top Places and Zone PIE chart
    col1, col2 = st.columns([6, 4]) 

    with col1:
        st.markdown("#### 🏆 Top 10 Most Visited Places")
        top_places = (filtered_df.groupby("Place_Name")["Visitors_Count"].sum().sort_values(ascending=False).head(10).reset_index())

        fig_top = px.bar(top_places,
                         x = "Visitors_Count",
                         y = "Place_Name",
                         orientation="h",
                         color = "Visitors_Count",
                         color_continuous_scale="Blues",
                         labels={"Visitors_Count": "Total Visitors", "Place_Name": ""})

        fig_top.update_layout(height=400,
                              plot_bgcolor="rgba(0,0,0,0)",
                              paper_bgcolor="rgba(0,0,0,0)",
                              yaxis=dict(autorange="reversed"),  # highest on top
                              coloraxis_showscale=False,
                              margin=dict(l=0, r=10, t=10, b=10))
        
        st.plotly_chart(fig_top, use_container_width=True)

    with col2:
        st.markdown("#### 🌍 Visitors by Zone")
        zone_data = (filtered_df.groupby("Zone")["Visitors_Count"].sum().reset_index())
        
        fig_zone = px.pie(
            zone_data,
            values="Visitors_Count",
            names="Zone",
            hole=0.45,   # Inner circle radius
            color_discrete_sequence=px.colors.sequential.Blues_r)

        fig_zone.update_layout(height=380,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=25, r=0, t=10, b=10))
        
        fig_zone.update_traces(textposition="outside", textinfo="percent+label")
        st.plotly_chart(fig_zone, use_container_width=True)

    st.divider()

    # Domestic vs International + Season
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("#### 👤 Domestic vs International")
        tourist_data = (filtered_df.groupby("Tourist_Type")["Visitors_Count"].sum().reset_index())

        fig_tourist = px.pie(tourist_data,
                             values="Visitors_Count",
                             names="Tourist_Type",
                             hole = 0.5,
                             color_discrete_sequence=["#4fc3f7", "#1565c0"])
        
        fig_tourist.update_layout(height = 350,
                                  plot_bgcolor="rgba(0,0,0,0)",
                                  paper_bgcolor="rgba(0,0,0,0)",
                                  margin=dict(l=10, r=10, t=10, b=10))
        
        st.plotly_chart(fig_tourist, use_container_width=True)

    with col4:
        st.markdown("#### 🌤️ Season-wise Visitor Distribution")
        season_data = (filtered_df.groupby(["Season", "Tourist_Type"])["Visitors_Count"].sum().reset_index())
        
        fig_season = px.bar(
            season_data,
            x="Season",
            y="Visitors_Count",
            color="Tourist_Type",
            barmode="group",          # domestic vs international group chart side by side
            color_discrete_sequence=["#4fc3f7", "#1565c0"],
            labels={"Visitors_Count": "Total Visitors", "Tourist_Type": "Type"})
        
        fig_season.update_layout(
            height=380,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            margin=dict(l=10, r=10, t=30, b=10))
        
        st.plotly_chart(fig_season, use_container_width=True)

    st.divider()

    # REVENUE BY PLACE TYPE 
    st.markdown("#### 💰 Revenue by Place Type (Top 15)")
    rev_place = (
        filtered_df[filtered_df["Revenue"] > 0].groupby("Place_Type")["Revenue"].sum().sort_values(ascending=False).head(15).reset_index())

    fig_rev = px.bar(rev_place,
                        x="Place_Type",
                        y="Revenue",
                        color="Revenue",
                        color_continuous_scale="Teal",
                        labels={"Revenue": "Total Revenue (₹)", "Place_Type": "Place Type"})
                    
    fig_rev.update_layout(height=400,
                            plot_bgcolor="rgba(0,0,0,0)",
                            paper_bgcolor="rgba(0,0,0,0)",
                            coloraxis_showscale=False,
                            xaxis=dict(tickangle=-35),
                            margin=dict(l=10, r=10, t=10, b=80))
    
    st.plotly_chart(fig_rev, use_container_width=True)

    st.divider()

    # ZONE SUMMARY TABLE
    st.markdown("#### 📋 Zone-wise Performance Summary")

    zone_summary = (
        filtered_df.groupby("Zone").agg(
            Total_Visitors=("Visitors_Count", "sum"),
            Total_Revenue =("Revenue",        "sum"),
            Avg_Rating    =("Rating",         "mean"),
            Unique_Places =("Place_Name",     "nunique"),
            Total_Records =("Visitors_Count", "count")
        ).reset_index())
    
    zone_summary["Avg_Rating"] = zone_summary["Avg_Rating"].round(2)

    st.dataframe(
        zone_summary.style
        .format({
            "Total_Visitors": "{:,.0f}",
            "Total_Revenue" : "₹{:,.0f}",
            "Avg_Rating"    : "{:.2f} ⭐",
        }).background_gradient(subset=["Total_Visitors"], cmap="Blues"),
        use_container_width=True,
        hide_index=True)
    

elif selected == "Demand & Trends":
    st.header("📈 Demand & Trend Analytics")

    if filtered_df.empty:
        st.warning("⚠️ No data for selected filters. Please adjust filters.")
        st.stop()

    # 1. MONTH-WISE TREND 
    # Sorting months in correct order to avoid them auto sort in alphabeticsl order
    month_order = [
        "January","February","March","April","May","June",
        "July","August","September","October","November","December"
    ]

    st.markdown("#### 📅 Month-wise Visitor Trend")

    monthly = (filtered_df.groupby(["Month", "Year"])["Visitors_Count"].sum().reset_index())

    # Month column used as order column
    monthly["Month"] = pd.Categorical(monthly["Month"], categories=month_order, ordered= True)
    monthly = monthly.sort_values("Month")
    monthly["Year"] = monthly["Year"].astype(str) # Year in string for color legend

    fig_monthly = px.line(monthly,
                        x="Month",
                        y="Visitors_Count",
                        color="Year",              
                        markers=True,              
                        color_discrete_sequence=["#91cfdc", "#0055ff", "#12F1B6"],
                        labels={"Visitors_Count": "Total Visitors", "Month": ""})
    

    fig_monthly.update_layout(
        height=380,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, ),
        xaxis=dict(tickangle=-30),
        margin=dict(l=10, r=10, t=30, b=10))
    
    fig_monthly.update_traces(line=dict(width=2.5))
    st.plotly_chart(fig_monthly, use_container_width=True)

    st.divider()

    # 2. YEAR OVER YEAR COMPARISON 
    st.markdown("#### 📊 Year-over-Year Comparison by Season")

    yoy = (filtered_df.groupby(["Year", "Season"])["Visitors_Count"].sum().reset_index())
    yoy["Year"] = yoy["Year"].astype(str)

    fig_yoy = px.bar(yoy,
                    x="Season",
                    y="Visitors_Count",
                    color="Year",
                    barmode="group",
                    color_discrete_sequence=["#6ccefc", "#145caf", "#00e5ff"],
                    labels={"Visitors_Count": "Total Visitors", "Season": "Season"})
    
    fig_yoy.update_layout(height=360,
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        legend=dict(orientation="h", yanchor="bottom", y=1.02),
                        margin=dict(l=10, r=10, t=30, b=10))
    
    st.plotly_chart(fig_yoy, use_container_width=True)

    st.divider()

    # 3. DAY OF WEEK + WEEKEND vs WEEKDAY
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📆 Day of Week Analysis")

        day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

        day_data = (filtered_df.groupby("Day_of_Week")["Visitors_Count"].sum().reset_index())

        day_data["Day_of_Week"] = pd.Categorical(day_data["Day_of_Week"], categories=day_order, ordered=True)
        
        day_data = day_data.sort_values("Day_of_Week")

        fig_day = px.bar(day_data,
                        x="Day_of_Week",
                        y="Visitors_Count",
                        color="Visitors_Count",
                        color_continuous_scale="Blues",
                        labels={"Visitors_Count": "Total Visitors", "Day_of_Week": "Day"})
        
        fig_day.update_layout(height=360,
                            plot_bgcolor="rgba(0,0,0,0)",
                            paper_bgcolor="rgba(0,0,0,0)",
                            coloraxis_showscale=False,
                            xaxis=dict(tickangle=-30),
                            margin=dict(l=10, r=10, t=10, b=10))
        
        st.plotly_chart(fig_day, use_container_width=True)

    with col2:
        st.markdown("#### 🏖️ Weekend vs Weekday")

        wknd_data = (
            filtered_df.groupby("Is_Weekend")["Visitors_Count"].sum().reset_index())
        
        # Yes/No readable label 
        wknd_data["Is_Weekend"] = wknd_data["Is_Weekend"].map({"Yes": "Weekend", "No": "Weekday"})

        fig_wknd = px.pie(wknd_data,
                        values="Visitors_Count",
                        names="Is_Weekend",
                        hole=0.5,
                        color_discrete_sequence=["#4fc3f7", "#1c5094"])
        
        fig_wknd.update_layout(height=320,
                            plot_bgcolor="rgba(0,0,0,0)",
                            paper_bgcolor="rgba(0,0,0,0)",
                            margin=dict(l=10, r=10, t=10, b=10))
        
        fig_wknd.update_traces(textposition="outside", textinfo="percent+label")
        st.plotly_chart(fig_wknd, use_container_width=True)

    st.divider()

    # 4. WEATHER + HEATMAP 
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("#### 🌦️ Weather-wise Visitor Distribution")

        weather_data = (filtered_df.groupby("Weather_Type")["Visitors_Count"].sum().sort_values(ascending=False).reset_index())

        fig_weather = px.bar(weather_data,
                                x="Visitors_Count",
                                y="Weather_Type",
                                orientation="h",
                                color="Visitors_Count",
                                color_continuous_scale="Blues",
                                labels={"Visitors_Count": "Total Visitors", "Weather_Type": "Weather"})
        
        fig_weather.update_layout(height=380,
                                    plot_bgcolor="rgba(0,0,0,0)",
                                    paper_bgcolor="rgba(0,0,0,0)",
                                    yaxis=dict(autorange="reversed"),
                                    coloraxis_showscale=False,
                                    margin=dict(l=10, r=10, t=10, b=10))

        st.plotly_chart(fig_weather, use_container_width=True)

    with col4:
        st.markdown("#### 🔥 Season x Weather Heatmap")

        # pivot table — rows=Season, cols=Weather, values=avg visitors
        heatmap_data = (filtered_df.groupby(["Season", "Weather_Type"])["Visitors_Count"].mean().reset_index())
        
        heatmap_pivot = heatmap_data.pivot(
                                        index="Season",
                                        columns="Weather_Type",
                                        values="Visitors_Count").fillna(0)  

        fig_heat = px.imshow(heatmap_pivot,
                            color_continuous_scale="Blues",
                            aspect="auto",            
                            labels=dict(color="Avg Visitors"))
        
        fig_heat.update_layout(height=380,
                            plot_bgcolor="rgba(0,0,0,0)",
                            paper_bgcolor="rgba(0,0,0,0)",
                            xaxis=dict(tickangle=-35),
                            margin=dict(l=0, r=0, t=10, b=40))
        
        st.plotly_chart(fig_heat, use_container_width=True)

    st.divider()


    # 5. TOP STATES BY FOOTFALL 
    st.markdown("####  Top 10 States by Total Footfall")

    state_data = (filtered_df.groupby("Location_State")["Visitors_Count"].sum().sort_values(ascending=False).head(10).reset_index())
    
    fig_state = px.bar(state_data,
                        x="Location_State",
                        y="Visitors_Count",
                        color="Visitors_Count",
                        color_continuous_scale="Blues",
                        labels={"Visitors_Count": "Total Visitors", "Location_State": "State"})
    
    fig_state.update_layout(height=360,
                            plot_bgcolor="rgba(0,0,0,0)",
                            paper_bgcolor="rgba(0,0,0,0)",
                            coloraxis_showscale=False,
                            xaxis=dict(tickangle=-30),
                            margin=dict(l=10, r=10, t=10, b=80))
    
    st.plotly_chart(fig_state, use_container_width=True)


elif selected == "Overcrowding Risk":
    st.header("🚨 Overcrowding Risk Analysis")

    if filtered_df.empty:
        st.warning("⚠️ No data for selected filters. Please adjust filters.")
        st.stop()

    # Risk Classification
    def classify_risk(visitors):
        if visitors > 700:
            return "High"
        elif visitors >= 300:
            return "Medium"
        else:
            return "Low"
        
    # Apply function to each row
    risk_df = filtered_df.copy()
    risk_df["Risk_Level"] = risk_df["Visitors_Count"].apply(classify_risk)

    # 1. RISK KPI CARDS
    high_count   = len(risk_df[risk_df["Risk_Level"] == "High"])
    medium_count = len(risk_df[risk_df["Risk_Level"] == "Medium"])
    low_count    = len(risk_df[risk_df["Risk_Level"] == "Low"])
    total        = len(risk_df)

    k1, k2, k3, k4 = st.columns(4)

    k1.metric("🔴 High Risk Records",   f"{high_count:,}", f"{high_count/total*100:.1f}% of total")
    k2.metric("🟠 Medium Risk Records", f"{medium_count:,}", f"{medium_count/total*100:.1f}% of total")
    k3.metric("🟢 Low Risk Records",    f"{low_count:,}", f"{low_count/total*100:.1f}% of total")
    k4.metric("📊 Total Records",       f"{total:,}")

    st.divider()

    # 2. RISK DISTRIBUTION CHARTS 
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📊 Risk Level Distribution")

        risk_counts = risk_df["Risk_Level"].value_counts().reset_index()
        risk_counts.columns = ["Risk_Level", "Count"]

        # Manual color map — High=red, Medium=orange, Low=green
        color_map = {
            "High"   : "#fe1818",
            "Medium" : "#e36d0d",
            "Low"    : "#3cc04b"}

        fig_risk = px.pie(risk_counts,
                            values="Count",
                            names="Risk_Level",
                            hole=0.5,
                            color="Risk_Level",
                            color_discrete_map=color_map)
        
        fig_risk.update_layout(height=320,
                                plot_bgcolor="rgba(0,0,0,0)",
                                paper_bgcolor="rgba(0,0,0,0)",
                                margin=dict(l=10, r=10, t=10, b=10))
        
        fig_risk.update_traces(textposition="outside", textinfo="percent+label")
        st.plotly_chart(fig_risk, use_container_width=True)

    with col2:
        st.markdown("#### 🌍 Zone-wise Risk Breakdown")

        zone_risk = (risk_df.groupby(["Zone", "Risk_Level"]).size().reset_index(name="Count"))
        
        fig_zone_risk = px.bar(zone_risk,
                                x="Zone",
                                y="Count",
                                color="Risk_Level",
                                barmode="stack",
                                color_discrete_map=color_map,
                                labels={"Count": "Records", "Zone": "Zone"})
        
        fig_zone_risk.update_layout(height=360,
                                    plot_bgcolor="rgba(0,0,0,0)",
                                    paper_bgcolor="rgba(0,0,0,0)",
                                    legend=dict(orientation="h", yanchor="bottom", y=1.02),
                                    margin=dict(l=10, r=10, t=30, b=10))
        
        st.plotly_chart(fig_zone_risk, use_container_width=True)

    st.divider()   

    # 3. TOP OVERCROWDED PLACES
    st.markdown("#### 🏆 Top 10 Most Overcrowded Places")

    top_crowded = (
        risk_df[risk_df["Risk_Level"] == "High"]
        .groupby(["Place_Name", "Location_State", "Zone"])["Visitors_Count"].sum().sort_values(ascending=False).head(10).reset_index())

    fig_crowded = px.bar(top_crowded,
                            x="Visitors_Count",
                            y="Place_Name",
                            orientation="h",
                            color="Visitors_Count",
                            color_continuous_scale="Reds",
                            hover_data=["Location_State", "Zone"],
                            labels={"Visitors_Count": "Total Visitors", "Place_Name": ""})
                        
    fig_crowded.update_layout(height=380,
                                plot_bgcolor="rgba(0,0,0,0)",
                                paper_bgcolor="rgba(0,0,0,0)",
                                yaxis=dict(autorange="reversed"),
                                coloraxis_showscale=False,
                                margin=dict(l=10, r=10, t=10, b=10))
    
    st.plotly_chart(fig_crowded, use_container_width=True)

    st.divider()

    # 4. ALERT CARDS
    st.markdown("#### 🚨 High Risk Destination Alerts")

    alert_places = (
    risk_df[risk_df["Risk_Level"] == "High"]
    .groupby(["Place_Name", "Location_State", "Zone", "Place_Type"])
    .agg(
        Peak_Visitors     =("Visitors_Count", "max"),   # ek din mein max
        Avg_Daily_Visitors=("Visitors_Count", "mean"),  # average per day
        High_Risk_Days    =("Risk_Level",     "count"), # kitne din high risk
        Avg_Rating        =("Rating",         "mean")
    )
    .sort_values("Peak_Visitors", ascending=False)  # peak se sort karo
    .head(5)
    .reset_index())

    # Card mein bhi update karo:
    for _, row in alert_places.iterrows():
        st.markdown(f"""
                    <div class="risk-high">
                        <div style="font-size:18px; font-weight:700; margin-bottom:5px; margin-top:10px ">
                            🔴 {row['Place_Name']}
                        </div>
                        <div style="font-size:16px; color:#d8cece; margin-bottom:12px;">
                            📍 {row['Location_State']} &nbsp;   |   &nbsp;
                            🌍 {row['Zone']} Zone &nbsp;   |   &nbsp;
                            🏛️ {row['Place_Type']}
                        </div>
                        <div style="display:flex; gap:40px;">
                            <span style="color:#fc8181; font-size:13px;">
                                📈 Peak Day Visitors<br>
                                <b style="font-size:18px;">{row['Peak_Visitors']:,.0f}</b>
                            </span>
                            <span style="color:#fbd38d; font-size:13px;">
                                👥 Avg Daily Visitors<br>
                                <b style="font-size:18px;">{row['Avg_Daily_Visitors']:,.0f}</b>
                            </span>
                            <span style="color:#90cdf4; font-size:13px;">
                                ⚠️ High Risk Days<br>
                                <b style="font-size:18px;">{row['High_Risk_Days']:,} days</b>
                            </span>
                            <span style="color:#9ae6b4; font-size:13px;">
                                ⭐ Avg Rating<br>
                                <b style="font-size:18px;">{row['Avg_Rating']:.2f} / 5.0</b>
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    st.divider()

    # 5. RISK SUMMARY TABLE
    st.markdown("#### 📋 Place-wise Risk Summary Table")

    # Filters for table
    tf1, tf2 = st.columns(2)

    with tf1:
        risk_filter = st.selectbox("Filter by Risk Level", ["All", "High", "Medium", "Low"])
        
    with tf2:
        top_n = st.slider("Show Top N Places", 10, 100, 20)

    table_df = (
        risk_df.groupby(["Place_Name", "Location_State", "Zone", "Place_Type"])
        .agg(
            Total_Visitors=("Visitors_Count", "sum"),
            Avg_Visitors  =("Visitors_Count", "mean"),
            Risk_Level    =("Risk_Level",     lambda x: x.mode()[0]),  # most common risk
            Avg_Rating    =("Rating",         "mean")
        )
        .sort_values("Total_Visitors", ascending=False).reset_index())

    if risk_filter != "All":
        table_df = table_df[table_df["Risk_Level"] == risk_filter]

    table_df = table_df.head(top_n)
    table_df["Avg_Visitors"] = table_df["Avg_Visitors"].round(0)
    table_df["Avg_Rating"]   = table_df["Avg_Rating"].round(2)

    st.dataframe(
        table_df.style.format({
            "Total_Visitors" : "{:,.0f}",
            "Avg_Visitors"   : "{:,.0f}",
            "Avg_Rating"     : "{:.2f} ⭐"
        }).apply(
            # Color Risk_Level column
            lambda col: [
                "background-color: #3d1515; color: #fc8181" if v == "High"
                else "background-color: #3d2c10; color: #fbd38d" if v == "Medium"
                else "background-color: #1a3028; color: #9ae6b4"
                for v in col] 
                if col.name == "Risk_Level" else [""] * len(col),
                axis=0),
                use_container_width=True, hide_index=True)
    
elif selected == "Data Assistant":
    st.header("🤖 Tourism Risk Predictor")

    import joblib
    import numpy as np

    # ── MODEL LOAD ────────────────────────────────────
    @st.cache_resource  # Resource - for heavy objects like(ML model)
    def load_model():
        model = joblib.load("model.pkl")
        encoders = joblib.load("encoders.pkl")
        model_info = joblib.load("model_info.pkl")
        return model, encoders, model_info
    
    model, encoders, model_info = load_model()
    
    # ── MODEL INFO CARDS ──────────────────────────────
    st.markdown("#### 📊 Model Performance")

    m1, m2, m3, m4 = st.columns(4)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🎯 R² Score",        f"{round(model_info['r2'], 2) * 100:.2f}%")
    m2.metric("📉 MAE",             f"±{model_info['mae']:.0f} visitors")
    m3.metric("📈 Peak Cap Value",   f"{model_info['cap_value']:.0f} visitors")
    m4.metric("🌲 Algorithm",        "Random Forest")

    st.divider()

    # ── USER INPUT FORM ──────────────────────────────

    st.markdown("#### 🔮 Predict Visitor Demand & Risk")
    st.caption("Fill in the details below to predict expected visitors and overcrowding risk")
    
    col1, col2 = st.columns(2)

    with col1:
        inp_season = st.selectbox("🌤️ Season", encoders["Season"].classes_)

        inp_weather = st.selectbox("🌦️ Weather Type", encoders["Weather_Type"].classes_)
        
        inp_zone    = st.selectbox("🌍 Zone", encoders["Zone"].classes_)
        
        inp_month   = st.selectbox("📅 Month", encoders["Month"].classes_)
        
        inp_year    = st.selectbox("📆 Year", [2023, 2024, 2025])

    with col2:
        inp_place_type   = st.selectbox("🏛️ Place Type", encoders["Place_Type"].classes_)
        
        inp_tourist_type = st.selectbox("👤 Tourist Type", encoders["Tourist_Type"].classes_)
        
        inp_weekend   = st.selectbox("🏖️ Is Weekend?", ["No", "Yes"])
        
        inp_ticket    = st.slider("🎟️ Ticket Price (₹)", 0, 8228, 200)
        
        inp_rating    = st.slider("⭐ Google Rating", 1.0, 5.0, 4.0, step=0.1)
        
        inp_reviews   = st.slider("📝 Review Count (Lakhs)", 0.01, 7.4, 0.5, step=0.01)

    st.divider()

    # ── PREDICT BUTTON ────────────────────────────────
    if st.button("🔮 Predict Visitor Demand & Risk", use_container_width=True):

        # ── INPUT PREPARE ─────────────────────────────
        input_data = {
                    "Month" : encoders["Month"].transform([inp_month])[0],
                    "Year" : inp_year,
                    "Is_Weekend" : 1 if inp_weekend == "Yes" else 0,
                    "Season" : encoders["Season"].transform([inp_season])[0],
                    "Weather_Type" : encoders["Weather_Type"].transform([inp_weather])[0],
                    "Zone" : encoders["Zone"].transform([inp_zone])[0],
                    "Place_Type" : encoders["Place_Type"].transform([inp_place_type])[0],
                    "Tourist_Type" : encoders["Tourist_Type"].transform([inp_tourist_type])[0],
                    "Ticket_Price" : inp_ticket,
                    "Google_Rating" : inp_rating,
                    "Review_Count_Lakhs" : inp_reviews}
        
        input_df = pd.DataFrame([input_data])

        # ── PREDICTION ────────────────────────────────
        predicted_visitors = model.predict(input_df)[0]
        predicted_visitors = max(0, predicted_visitors)

        # ── RISK CLASSIFICATION ───────────────────────
        if predicted_visitors > 700:
            risk_level  = "HIGH"
            risk_emoji  = "🔴"
            risk_color  = "#e53e3e"
            risk_bg     = "#3d1515"
            risk_border = "#e53e3e"
            visitor_range = f"700 - {int(model_info['cap_value']):,}"

        elif predicted_visitors >= 300:
            risk_level  = "MEDIUM"
            risk_emoji  = "🟠"
            risk_color  = "#ed8936"
            risk_bg     = "#3d2c10"
            risk_border = "#ed8936"
            visitor_range = "300 - 700"

        else:
            risk_level  = "LOW"
            risk_emoji  = "🟢"
            risk_color  = "#48bb78"
            risk_bg     = "#1a3028"
            risk_border = "#48bb78"
            visitor_range = "8 - 299"

        # ── RECOMMENDATIONS ───────────────────────────
        recommendations = {
            "HIGH": [
                "⛔ Implement strict visitor entry limits immediately",
                "👮 Deploy additional security and management staff",
                "🅿️ Arrange extra parking and transport facilities",
                "📢 Promote alternative nearby destinations to tourists",
                "⏰ Restrict entry during peak hours of the day",
                "📋 Activate emergency crowd control protocols"],

            "MEDIUM": [
                "👁️ Increase real-time crowd monitoring",
                "🎟️ Consider mandatory advance booking system",
                "🚗 Review parking capacity and visitor facilities",
                "📊 Track and report daily visitor count",
                "⚠️ Keep backup crowd management plan ready"],

            "LOW": [
                "📣 Launch targeted tourism marketing campaigns",
                "🏗️ Focus on infrastructure maintenance and upgrades",
                "🌟 Enhance overall tourist experience and amenities",
                "📸 Boost social media and digital promotion",
                "🤝 Collaborate with local businesses to attract visitors"]
            }
        
        # ── RESULT DISPLAY ────────────────────────────
        st.markdown("### 📊 Prediction Result")

        # Main result card
        st.markdown(f"""
        <div style="
            background : {risk_bg};
            border     : 2px solid {risk_border};
            border-radius: 12px;
            padding    : 24px;
            margin     : 16px 0;
        ">
            <div style="font-size:28px; font-weight:800; color:{risk_color};">
                {risk_emoji} {risk_level} RISK
            </div>
            <div style="margin-top:20px; display:flex; gap:50px;">
                <span style="color:#e2e8f0;">
                    <div style="font-size:15px; color:#a0aec0;">
                        🧳 Expected Visitors/Day
                    </div>
                    <div style="font-size:28px; font-weight:700;">
                        {predicted_visitors:,.0f}
                    </div>
                </span>
                <span style="color:#e2e8f0;">
                    <div style="font-size:15px; color:#a0aec0;">
                        📊 Visitor Range
                    </div>
                    <div style="font-size:28px; font-weight:700;">
                        {visitor_range}
                    </div>
                </span>
                <span style="color:#e2e8f0;">
                    <div style="font-size:15px; color:#a0aec0;">
                        📉 Model MAE
                    </div>
                    <div style="font-size:28px; font-weight:700;">
                        ±{model_info['mae']:.0f}
                    </div>
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── RECOMMENDATIONS DISPLAY ───────────────────
        st.markdown("#### 📋 Recommendations")
        for rec in recommendations[risk_level]:
            st.markdown(f"""
            <div style="
                background   : #1e2130;
                border-left  : 3px solid {risk_border};
                border-radius: 6px;
                padding      : 10px 16px;
                margin       : 6px 0;
                color        : #e2e8f0;
                font-size    : 14px;
            ">
                {rec}
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        # ── FEATURE IMPORTANCE CHART ──────────────────
        st.markdown("#### 📊 Feature Importance")
        st.caption("Which factor affect the most to the visitors")

        importance_df = pd.DataFrame({
            "Feature"   : model_info["features"],
            "Importance": model.feature_importances_}).sort_values("Importance", ascending=True)

        fig_imp = px.bar(
                    importance_df,
                    x="Importance",
                    y="Feature",
                    orientation="h",
                    color="Importance",
                    color_continuous_scale="Blues",
                    labels={"Importance": "Importance Score", "Feature": ""})
        
        fig_imp.update_layout(height=380,
                            plot_bgcolor ="rgba(0,0,0,0)",
                            paper_bgcolor="rgba(0,0,0,0)",
                            coloraxis_showscale=False,
                            margin=dict(l=10, r=10, t=10, b=10))
        
        st.plotly_chart(fig_imp, use_container_width=True)