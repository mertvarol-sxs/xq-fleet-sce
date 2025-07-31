import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from fleet_data import initialize_fleet_data

st.set_page_config(layout="wide")

if 'fleet_df' not in st.session_state:
    st.session_state.fleet_df = initialize_fleet_data()

selected_tab = st.sidebar.radio("📂 Navigation", ["📥 Add", "❌ Remove", "📊 Fleet Age Overview", "📊 Fleet Breakdown"])

if selected_tab == "📥 Add":
    st.header("Add Aircraft")
    with st.form("add_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            reg = st.text_input("Registration")
            ac_type = st.selectbox("Aircraft Type", ['B737-800NG', 'B737-8', 'B737-10', 'A320neo', 'A321neo', 'Others'])
        with col2:
            dom = st.date_input("Date of Manufacture")
            doi = st.date_input("Date of Entry into Fleet")
            lease_type = st.selectbox("Lease Type", ['OWN', 'FIN', 'OPS'])
        with col3:
            lease_end = st.date_input("Lease End Date", disabled=(lease_type != 'OPS'))
            market_value = st.number_input("Market Value (USD)", min_value=0)
            monthly_lease = st.number_input("Monthly Lease (USD, if OPS)", min_value=0)

        submitted = st.form_submit_button("Add Aircraft")
        if submitted:
            if doi < dom:
                st.error("Date of Entry into Fleet cannot be earlier than Date of Manufacture!")
            else:
                new_row = {
                    'Reg.': reg,
                    'Aircraft Type': ac_type,
                    'Aircraft Variant': '',
                    'Date of Manufacture': pd.to_datetime(dom),
                    'DOI': pd.to_datetime(doi),
                    'DOE': pd.NaT,
                    'Lease Type': lease_type,
                    'Lease End Date': pd.to_datetime(lease_end) if lease_type == 'OPS' else pd.NaT,
                    'Market Value': market_value,
                    'Monthly Lease (OPS)': monthly_lease if lease_type == 'OPS' else pd.NA
                }
                st.session_state.fleet_df = pd.concat([st.session_state.fleet_df, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"{reg} added to the fleet.")

elif selected_tab == "❌ Remove":
    st.header("Remove Aircraft")

    df_active = st.session_state.fleet_df[st.session_state.fleet_df['DOE'].isna()]
    removal_option = st.radio("Select a removal option:", ["Remove oldest X aircraft", "Remove by registration"])
    removal_date = st.date_input("Select Exit Date", datetime.today())

    if removal_option == "Remove oldest X aircraft":
        count = st.number_input("Number of oldest aircraft to remove", min_value=1, max_value=len(df_active), step=1)
        if st.button("Remove Oldest Aircraft"):
            df_active = df_active.copy()
            df_active['Age'] = (removal_date - df_active['Date of Manufacture']).dt.days
            df_active = df_active.sort_values(by='Age', ascending=False)
            to_remove = df_active.head(count)
            st.session_state.fleet_df.loc[to_remove.index, 'DOE'] = removal_date

            own_contribution = to_remove[to_remove['Lease Type'] == 'OWN']['Market Value'].sum()
            st.success(f"Removed {count} aircraft. Financial contribution from OWN aircraft: ${own_contribution:,.0f}")

    elif removal_option == "Remove by registration":
        regs_to_remove = st.multiselect("Select registrations to remove", df_active['Reg.'].tolist())
        if st.button("Remove Selected Aircraft"):
            to_remove = df_active[df_active['Reg.'].isin(regs_to_remove)]
            st.session_state.fleet_df.loc[to_remove.index, 'DOE'] = removal_date

            own_contribution = to_remove[to_remove['Lease Type'] == 'OWN']['Market Value'].sum()
            st.success(f"Removed {len(to_remove)} aircraft. Financial contribution from OWN aircraft: ${own_contribution:,.0f}")

elif selected_tab == "📊 Fleet Age Overview":
    st.header("Fleet Age Overview")

    def calculate_avg_age_by_year(df, years=11, start_year=2025):
        avg_ages = {}
        for year in range(start_year, start_year + years):
            date = datetime(year, 1, 1)
            active = df[(df['DOI'] <= date) & ((df['DOE'].isna()) | (df['DOE'] > date))]
            if not active.empty:
                ages = (date - active['Date of Manufacture']).dt.days / 365.25
                avg_ages[year] = ages.mean()
            else:
                avg_ages[year] = 0
        return pd.Series(avg_ages)

    original_df = initialize_fleet_data()
    scenario_df = st.session_state.fleet_df

    original_avg_age = calculate_avg_age_by_year(original_df)
    scenario_avg_age = calculate_avg_age_by_year(scenario_df)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=original_avg_age.index, y=original_avg_age.values, mode='lines+markers', name='Original Fleet', line=dict(color='royalblue')))
    fig.add_trace(go.Scatter(x=scenario_avg_age.index, y=scenario_avg_age.values, mode='lines+markers', name='Scenario Fleet', line=dict(color='green')))
    fig.update_layout(title='Fleet Average Age Projection (2025–2035)', xaxis_title='Year', yaxis_title='Average Age (Years)', template='plotly_white')

    st.plotly_chart(fig, use_container_width=True)

elif selected_tab == "📊 Fleet Breakdown":
    st.header("Fleet Breakdown")

    selected_breakdown_date = st.date_input("Select Breakdown Date", datetime.today())
    scenario_df = st.session_state.fleet_df
    scenario_df = scenario_df[(scenario_df['DOI'] <= selected_breakdown_date) & ((scenario_df['DOE'].isna()) | (scenario_df['DOE'] > selected_breakdown_date))]

    st.subheader("✈️ Aircraft Type Distribution")
    type_counts = scenario_df['Aircraft Type'].value_counts()
    fig1 = go.Figure(data=[go.Pie(labels=type_counts.index, values=type_counts.values, hole=0.4)])
    fig1.update_layout(title="Aircraft Type Distribution", template="plotly_white")
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("💼 Lease Type Distribution")
    lease_counts = scenario_df['Lease Type'].value_counts()
    fig2 = go.Figure(data=[go.Pie(labels=lease_counts.index, values=lease_counts.values, hole=0.4)])
    fig2.update_layout(title="Lease Type Distribution", template="plotly_white")
    st.plotly_chart(fig2, use_container_width=True)