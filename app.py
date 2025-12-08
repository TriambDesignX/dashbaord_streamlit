import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Page Config (Clean & Wide)
st.set_page_config(page_title="Executive Dashboard", layout="wide")
st.title("🏭 Plant Sustainability & Cost Dashboard")

# 2. Load Data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('processed_environment_data.csv')
        df['Month'] = pd.to_datetime(df['Month'])
        return df
    except: return None

df = load_data()
if df is None:
    st.error("⚠️ Data file missing. Run process_data.py first!")
    st.stop()

# 3. Sidebar Filter
st.sidebar.header("Filter")
dates = df['Month'].dt.date.unique()
if len(dates) > 0:
    start, end = st.sidebar.select_slider("Period", options=dates, value=(dates[0], dates[-1]))
    df = df[(df['Month'].dt.date >= start) & (df['Month'].dt.date <= end)]

# 4. TOP KPI ROW (The "Big Numbers")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Production", f"{df['Production_Pcs'].sum():,.0f} pcs")
k2.metric("Total Cost", f"₹ {df['Total_Cost'].sum():,.0f}")
k3.metric("Energy Intensity", f"{df['KPI_Energy_Pc'].mean():.2f} kWh/pc", delta_color="inverse")
k4.metric("Washing Eff.", f"{df['KPI_Wash_L_kg'].mean():.1f} L/kg", delta_color="inverse")

st.markdown("---")

# 5. ROW 1: FINANCIALS (Pie + Trend)
c1, c2 = st.columns([1, 2])

with c1:
    st.subheader("💸 Where is the money going?")
    # Pie Chart
    costs = df[['Cost_Grid', 'Cost_DG', 'Cost_Boiler']].sum()
    names = ['Grid Elec', 'Diesel Gen', 'Boiler Fuel']
    fig_pie = px.pie(values=costs.values, names=names, hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_pie, use_container_width=True)

with c2:
    st.subheader("💰 Monthly Cost Trend")
    # Stacked Bar
    fig_cost = px.bar(df, x='Month', y=['Cost_Grid', 'Cost_DG', 'Cost_Boiler'], 
                      labels={'value': 'Cost (INR)', 'variable': 'Expense'},
                      color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_cost, use_container_width=True)

st.markdown("---")

# 6. ROW 2: OPERATIONS & ENERGY
c3, c4 = st.columns(2)

with c3:
    st.subheader("⚡ Production vs Energy Efficiency")
    # Dual Axis Chart
    fig_eff = go.Figure()
    fig_eff.add_trace(go.Bar(x=df['Month'], y=df['Production_Pcs'], name='Production', marker_color='#636EFA', opacity=0.6))
    fig_eff.add_trace(go.Scatter(x=df['Month'], y=df['KPI_Energy_Pc'], name='kWh/pc', yaxis='y2', line=dict(color='red', width=3)))
    fig_eff.update_layout(yaxis2=dict(overlaying='y', side='right', title='Specific Energy (kWh/pc)'), showlegend=True)
    st.plotly_chart(fig_eff, use_container_width=True)

with c4:
    st.subheader("🔋 Energy Source Mix")
    # Calculate Grid
    df['Elec_Grid_kWh'] = df['Elec_Total_kWh'] - df['Elec_Renewable_kWh'] - df['Elec_DG_kWh']
    fig_mix = px.bar(df, x='Month', y=['Elec_Grid_kWh', 'Elec_Renewable_kWh', 'Elec_DG_kWh'],
                     labels={'value': 'kWh', 'variable': 'Source'},
                     color_discrete_map={'Elec_Grid_kWh': 'gray', 'Elec_Renewable_kWh': 'green', 'Elec_DG_kWh': 'red'})
    st.plotly_chart(fig_mix, use_container_width=True)

# 7. ROW 3: WATER & RESOURCES
c5, c6 = st.columns(2)

with c5:
    st.subheader("💧 Water: Fresh vs Recycled")
    fig_water = px.bar(df, x='Month', y=['Water_Fresh_KL', 'Water_Recycled_KL'], barmode='group')
    st.plotly_chart(fig_water, use_container_width=True)

with c6:
    st.subheader("🔥 Boiler Fuel Mix")
    fuel_totals = df[['Fuel_Wood_Kg', 'Fuel_Briquette_Kg']].sum()
    fig_fuel = px.pie(values=fuel_totals.values, names=['Firewood', 'Briquettes'], hole=0.4,
                      color_discrete_sequence=['#8B4513', '#D2691E'])
    st.plotly_chart(fig_fuel, use_container_width=True)
