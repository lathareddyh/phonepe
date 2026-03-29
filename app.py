import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import json
from pathlib import Path

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="PhonePe Pulse Dashboard",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------
# PREMIUM DARK UI
# -------------------------------------------------
st.markdown("""
<style>
   .stApp {
        background: linear-gradient(180deg, #020817 0%, #030b1a 100%);
        color: #ffffff;
        font-family: "Segoe UI", sans-serif;
    }

    .stAppHeader {
        background: linear-gradient(180deg, #020817 0%, #030b1a 100%);
    }
            
    /* Closed selectbox */
    .stSelectbox > div > div {
        background-color: #060b18 !important;
        color: white !important;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.08) !important;
    }

    /* Selected value text */
    .stSelectbox div[data-baseweb="select"] > div {
        color: white !important;
        background-color: #060b18 !important;
    }

    /* Dropdown menu container */
    div[data-baseweb="popover"] {
        background-color: #060b18 !important;
        color: white !important;
    }

    /* Dropdown list */
    ul {
        background-color: #060b18 !important;
        color: white !important;
    }

    /* Each dropdown option */
    li[role="option"] {
        background-color: #060b18 !important;
        color: white !important;
    }

    /* Hovered option */
    li[role="option"]:hover {
        background-color: #1e293b !important;
        color: white !important;
    }
    /* Main content padding */
    .block-container {
        padding-top: 2.5rem;
        padding-left: 3rem;
        padding-right: 3rem;
        padding-bottom: 2rem;
        max-width: 95%;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #232733 0%, #1d2230 100%);
        border-right: 1px solid rgba(255,255,255,0.05);
        min-width: 290px !important;
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 3rem;
    }

    /* Text */
    h1, h2, h3, h4, h5, h6, p, div, span, label, .legendtext {
        color: #ffffff !important;
    }

    /* Title block */
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: 0.5rem;
        color: #f8fafc;
    }

    .hero-sub {
        font-size: 1.15rem;
        color: #cbd5e1 !important;
        margin-bottom: 2rem;
    }

    .section-title {
        font-size: 2rem;
        font-weight: 700;
        margin-top: 1rem;
        margin-bottom: 1.5rem;
        color: #ffffff;
    }

    .divider {
        border: none;
        border-top: 1px solid rgba(255,255,255,0.12);
        margin: 2rem 0 2.2rem 0;
    }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 18px;
        padding: 18px 16px;
        box-shadow: 0 4px 18px rgba(0,0,0,0.18);
    }

    /* Selectbox */
    .stSelectbox > div > div {
        background-color: #060b18;
        color: white;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.08);
    }

    /* Slider */
    .stSlider {
        padding-top: 0.4rem;
    }

    /* Dataframe */
    .stDataFrame {
        border-radius: 14px;
        overflow: hidden;
    }

    /* Plotly chart container feel */
    .chart-card {
        background: rgba(255,255,255,0.02);
        padding: 18px;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.05);
    }
            
            /* Tabs container */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    font-size:20px !important
}

.stTabs p {
    font-size:20px !important
}
            
/* Individual tab */
.stTabs [data-baseweb="tab"] {
    background-color: #2b2b2b;
    color: white;
    padding: 10px 18px;
    border-radius: 8px 8px 0 0;
    border: 1px solid #444;
    border-bottom: none;
    font-weight: 500;
}

/* Active tab */
.stTabs [aria-selected="true"] {
    background-color: #1f77b4;
    color: white;
    border-bottom: 2px solid #1f77b4;
}

/* Tab hover */
.stTabs [data-baseweb="tab"]:hover {
    background-color: #3a3a3a;
    color: white;
}
            
.postal-list {
    list-style: none;
    padding: 0;
    margin: 0;
    font-family: Arial, sans-serif;
    color: white;
    font-size: 18px;
    max-width: 300px;
}
.postal-list li {
    display: flex;
    justify-content: space-between;
    padding: 6px 0;
    font-weight: 600;
    opacity: 1;
}
.postal-list li:nth-child(n+7) {
    opacity: 0.4;  /* dim from 7th item */
}
.rank {
    width: 20px;
    color: #888;
    user-select: none;
}
.postal-code {
    flex: 1;
    padding-left: 10px;
}
.amount {
    font-weight: 700;
    color: #00cfff; /* bright cyan */
    user-select: none;
}


</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# COLORS
# -------------------------------------------------
SAGE = "#A8BC96"
SAGE_LIGHT = "#C7D7B8"
BG = "#111111"
CARD = "#191919"
TEXT = "#FFFFFF"

# -------------------------------------------------
# DATABASE
# -------------------------------------------------
DB_PATH = "phonepay.db"

@st.cache_data
def run_query(query: str):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# -------------------------------------------------
# LOAD TABLES
# -------------------------------------------------
#  Aggregation tables
agg_tran = run_query("SELECT * FROM aggreated_transaction")
agg_user = run_query("SELECT * FROM aggreated_user")
agg_ins = run_query("SELECT * FROM aggreated_insurance")

# Map tables
map_tran = run_query("SELECT * FROM map_transactions")
map_user = run_query("SELECT * FROM map_user")
map_ins = run_query("SELECT * FROM map_insurance")

# Top tables
top_trans_districs = run_query("SELECT * FROM top_transaction_districs")
top_trans_pincodes = run_query("SELECT * FROM top_transaction_pincodes")

top_user_districts = run_query("SELECT * FROM top_user_districs")
top_user_pincodes = run_query("SELECT * FROM top_user_pincodes")

top_ins_dist = run_query("SELECT * FROM top_insurance_districs")
top_ins_pincodes = run_query("SELECT * FROM top_insurance_pincodes")

# -------------------------------------------------
# NORMALIZE COLUMN NAMES
# -------------------------------------------------
def normalize_columns(df):
    df.columns = [c.strip() for c in df.columns]
    return df

agg_tran = normalize_columns(agg_tran)
agg_user = normalize_columns(agg_user)
agg_ins = normalize_columns(agg_ins)

map_tran = normalize_columns(map_tran)
map_user = normalize_columns(map_user)
map_ins = normalize_columns(map_ins)

top_tran = normalize_columns(top_trans_districs)
top_trans_pincodes = normalize_columns(top_trans_pincodes)

top_user = normalize_columns(top_user_districts)
top_user_pincodes = normalize_columns(top_user_pincodes)

top_ins_dist = normalize_columns(top_ins_dist)
top_ins_pincodes = normalize_columns(top_ins_pincodes)


# -------------------------------------------------
# SIDEBAR FILTERS
# -------------------------------------------------
st.sidebar.title("📌 Dashboard Filters")

years = sorted(agg_tran["year"].dropna().unique().tolist(), reverse=True) if "year" in agg_tran.columns else []
quarters = sorted(agg_tran["quarter"].dropna().unique().tolist()) if "quarter" in agg_tran.columns else []
states = sorted(agg_tran["state"].dropna().unique().tolist()) if "state" in agg_tran.columns else []

selected_year = st.sidebar.selectbox("Select Year", years)
selected_quarter = st.sidebar.selectbox("Select Quarter", quarters)
selected_state = st.sidebar.selectbox("Select State", ["All States"] + states)

# -------------------------------------------------
# FILTER LOGIC
# -------------------------------------------------
def apply_filters(df):
    temp = df.copy()
    if "year" in temp.columns:
        temp = temp[temp["year"] == selected_year]
    if "quarter" in temp.columns:
        temp = temp[temp["quarter"] == selected_quarter]
    if selected_state != "All States" and "state" in temp.columns:
        temp = temp[temp["state"] == selected_state]
    return temp

def format_cash(amount):
    def truncate_float(number, places):
        return int(number * (10 ** places)) / 10 ** places

    if amount < 1e3:
        return amount

    if 1e3 <= amount < 1e5:
        return str(truncate_float((amount / 1e5) * 100, 2)) + " K"

    if 1e5 <= amount < 1e7:
        return str(truncate_float((amount / 1e7) * 100, 2)) + " L"

    if amount > 1e7:
        return str(truncate_float(amount / 1e7, 2)) + " Cr"


f_agg_tran = apply_filters(agg_tran)
f_agg_user = apply_filters(agg_user)
f_agg_ins = apply_filters(agg_ins)

f_map_tran = apply_filters(map_tran)
f_map_user = apply_filters(map_user)
f_map_ins = apply_filters(map_ins)

f_top_tran = apply_filters(top_tran)
f_top_tran_pincode = apply_filters(top_trans_pincodes)

f_top_user = apply_filters(top_user)
f_top_user_pin = apply_filters(top_user_pincodes)

f_top_ins_dis = apply_filters(top_ins_dist)
f_top_ins_pin = apply_filters(top_ins_pincodes)

# -------------------------------------------------
# TITLE
# -------------------------------------------------
st.title("📱 PhonePe Pulse: Analytics Dashboard")
st.caption("Interactive insights on digital payments, users, states, districts, and transaction trends")

# -------------------------------------------------
# KPI SECTION
# -------------------------------------------------
total_amount = f_agg_tran["amount"].sum() if "amount" in f_agg_tran.columns else 0

total_count = f_agg_tran["count"].sum() if "count" in f_agg_tran.columns else 0
registered_users = f_map_user["registered_users"].sum() if "registered_users" in f_map_user.columns else 0
avg_value = total_amount / total_count if total_count else 0
total_amount = total_amount // 1e7

# k1, k2, k3, k4 = st.columns(4)
# k1.metric("Total Transaction Amount", f"₹{total_amount:,.0f}")
# k2.metric("Total Transaction Count", f"{total_count:,.0f}")
# k3.metric("Registered Users", f"{registered_users:,.0f}")
# k4.metric("Average Transaction Value", f"₹{avg_value:,.2f}")

def format_international(num):
    if num >= 1_000_000_000_000:   # Trillion
        return f"{num/1_000_000_000_000:.2f} T"
    elif num >= 1_000_000_000:     # Billion
        return f"{num/1_000_000_000:.2f} B"
    elif num >= 1_000_000:         # Million
        return f"{num/1_000_000:.2f} M"
    elif num >= 1_000:             # Thousand
        return f"{num/1_000:.2f} K"
    else:
        return f"{num:.0f}"


def format_indian(num):
    s = str(num)

    if len(s) <= 3:
        return s

    last_three = s[-3:]
    rest = s[:-3]

    parts = []
    while len(rest) > 2:
        parts.insert(0, rest[-2:])
        rest = rest[:-2]

    if rest:
        parts.insert(0, rest)

    return ",".join(parts) + "," + last_three


k1, k2, k3, k4 = st.columns(4)

k1.metric("Total Transaction Amount", f"₹{total_amount:,.0f} Cr")
k2.metric("PhonePe transaction count", format_international(total_count))
k3.metric("Registered Users", format_international(registered_users))
k4.metric("Average Transaction Value", f"₹{avg_value:,.0f}")

st.markdown("")


# State names should match standard names for better display.
state_corrections = {
    "andaman-&-nicobar-islands":"Andaman & Nicobar",
    "andhra-pradesh":"Andhra Pradesh",
    "arunachal-pradesh":"Arunachal Pradesh",
    "dadra-&-nagar-haveli-&-daman-&-diu":"Dadra and Nagar Haveli and Daman and Diu",
    "himachal-pradesh":"Himachal Pradesh",
    "jammu-&-kashmir":"Jammu & Kashmir",
    "madhya-pradesh":"Madhya Pradesh",
    "tamil-nadu":"Tamil Nadu",
    "uttar-pradesh":"Uttar Pradesh",
    "west-bengal":"West Bengal"}


# -------------------------------------------------
# TABS
# -------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Transactions",
    "Users",
    "Insurance",
    "Overview",
    "Raw Data"
])


# -------------------------------------------------
# TAB 1: TRANSACTIONS
# -------------------------------------------------
with tab1:

    st.markdown(
        f"""
        <div style="
            background-color:#2d0b4e;
            padding:12px 20px;
            border-radius:10px;
            color:white;
            font-size:20px;
            font-weight:600;
            width: fit-content;
        ">
            📅 {selected_year} • Q{selected_quarter} - {selected_state.replace('-',' ').title()}
        </div>
        """,
        unsafe_allow_html=True
    )

    if selected_state == "All States":

        
        st.subheader("Top 10 States by Transaction Amount")
        
        top_states = agg_tran[
            (agg_tran["year"] == selected_year) &
            (agg_tran["quarter"] == selected_quarter)
        ].groupby("state", as_index=False)["amount"].sum().sort_values(
            by="amount", ascending=False
        ).head(10)

        fig_states = px.bar(
            top_states,
            x="amount",
            y="state",
            orientation="h",
            text_auto=".2s",
            color_discrete_sequence=[SAGE]
        )
        fig_states.update_layout(
            plot_bgcolor=BG,
            paper_bgcolor=BG,
            font_color=TEXT,
            # xaxis_tickangle=-35
            xaxis=dict(tickfont=dict(color="white")),
            yaxis=dict(autorange="reversed", tickfont=dict(color="white"))
        )
        st.plotly_chart(fig_states, use_container_width=True)

        ##########################################################

        st.subheader("Top 10 States by Transaction Count")

        top_states = f_agg_tran.groupby("state", as_index=False)["count"].sum().sort_values(
            by="count", ascending=False
        ).head(10)
        
        fig_states = px.bar(
            top_states,
            x="count",
            y="state",
            orientation="h",
            text_auto=".2s",
            color_discrete_sequence=[SAGE]
        )
        fig_states.update_layout(
            plot_bgcolor=BG,
            paper_bgcolor=BG,
            font_color=TEXT,
            xaxis=dict(tickfont=dict(color="white")),
            yaxis=dict(autorange="reversed", tickfont=dict(color="white"))
        )
        st.plotly_chart(fig_states, use_container_width=True)




        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Transaction Count by Type")
            if "transaction_type" in f_agg_tran.columns:
                tx_type_count = f_agg_tran.groupby("transaction_type", as_index=False)["count"].sum().sort_values(by="count", ascending=False)
                fig_tc = px.bar(
                    tx_type_count,
                    x="count",
                    y="transaction_type",
                    orientation="h",
                    text_auto=".2s",
                    color_discrete_sequence=[SAGE_LIGHT]
                )
                fig_tc.update_layout(
                    plot_bgcolor=BG, 
                    paper_bgcolor=BG, 
                    font_color=TEXT, 
                    xaxis=dict(title="", tickfont=dict(color="white")),
                    yaxis=dict(autorange="reversed", tickfont=dict(color="white")),)
                st.plotly_chart(fig_tc, use_container_width=True)

        with col2:
            st.subheader("Transaction Amount by Type")
            if "transaction_type" in f_agg_tran.columns:
                tx_type_amt = f_agg_tran.groupby("transaction_type", as_index=False)["amount"].sum().sort_values(by="amount", ascending=False)
                fig_ta = px.bar(
                    tx_type_amt,
                    x="amount",
                    y="transaction_type",
                    orientation="h",
                    text_auto=".2s",
                    color_discrete_sequence=[SAGE]
                )
                fig_ta.update_layout(
                    plot_bgcolor=BG, 
                    paper_bgcolor=BG, 
                    font_color=TEXT,
                    xaxis=dict(title="", tickfont=dict(color="white")),
                    yaxis=dict(autorange="reversed", tickfont=dict(color="white")),)
                st.plotly_chart(fig_ta, use_container_width=True)

    

        ##################### Top 10 Districts #####################################

        st.subheader("Top 10 Districts by Transaction Count")
        
        top_dist = f_map_tran.groupby("district", as_index=False)["count"].sum().sort_values(
            by="count", ascending=False
        ).head(10)

        fig_states = px.bar(
            top_dist,
            x="count",
            y="district",
            orientation = "h",
            text_auto=".2s",
            color_discrete_sequence=[SAGE]
        )
        fig_states.update_layout(
            plot_bgcolor=BG,
            paper_bgcolor=BG,
            font_color=TEXT,
            xaxis=dict(tickfont=dict(color="white")),
            yaxis=dict(autorange="reversed", tickfont=dict(color="white"))
        )
        st.plotly_chart(fig_states, use_container_width=True)


        st.subheader("Top 10 Districts by Transaction Amount")
        
        top_dist = f_map_tran.groupby("district", as_index=False)["amount"].sum().sort_values(
            by="amount", ascending=False
        ).head(10)

        fig_states = px.bar(
            top_dist,
            x="amount",
            y="district",
            orientation = "h",
            text_auto=".2s",
            color_discrete_sequence=[SAGE]
        )
        fig_states.update_layout(
            plot_bgcolor=BG,
            paper_bgcolor=BG,
            font_color=TEXT,
            xaxis=dict(tickfont=dict(color="white")),
            yaxis=dict(autorange="reversed", tickfont=dict(color="white"))
        )
        st.plotly_chart(fig_states, use_container_width=True)



        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Top 10 Postal by Transaction Amount")
            top_pin_trans = f_top_tran_pincode.groupby("pincode_entity_name", as_index=False)["pincode_amount"].sum().sort_values(
                by="pincode_amount", ascending=False
            ).head(10).reset_index(drop=True)
            # Set index starting from 1
            top_pin_trans.index = top_pin_trans.index + 1
            top_pin_trans['pincode_amount'] = top_pin_trans['pincode_amount'].apply(format_cash)
            st.write(top_pin_trans)

        with col2:
            st.subheader("Top 10 Postal codes by Transaction Count")
            
            top_pin_count = f_top_tran_pincode.groupby("pincode_entity_name", as_index=False)["pincode_count"].sum().sort_values(
                by="pincode_count", ascending=False
            ).head(10).reset_index(drop=True)
            # Set index starting from 1
            top_pin_count.index = top_pin_count.index + 1
            top_pin_count['pincode_count'] = top_pin_count['pincode_count'].apply(lambda x: format_indian(int(x)))
            st.write(top_pin_count)

       
        ############################## 
        # State wise Transaction Amount
        ##############################

        st.subheader("State-wise Transaction Amount Map")

        # map_df = agg_tran[
        #     (agg_tran["year"] == selected_year) &
        #     (agg_tran["quarter"] == selected_quarter)
        # ].groupby("state", as_index=False)["amount"].sum()

        state_df = f_agg_tran.groupby("state", as_index=False)["amount"].sum()

        # This uses Plotly's India geographic rendering.
        
        state_df["state"]=state_df["state"].str.strip().replace(state_corrections)
        state_df["state"]=state_df["state"].str.title()
        
        fig=px.choropleth(state_df,
                        geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
                        featureidkey="properties.ST_NM",
                        locations="state",
                        color="amount",
                        color_continuous_scale=[[0, "#4da7d4"], [1, SAGE]],
                        
                        )    
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(
            geo_bgcolor=BG,
            paper_bgcolor=BG,
            plot_bgcolor=BG,
            font_color=TEXT,
            title=dict(
                            text="Transaction Amount Across States",
                            font=dict(color="white", size=20)
                        ),
            margin=dict(l=0, r=0, t=40, b=0)
        )

        st.plotly_chart(fig, use_container_width=True)



        st.subheader("Top 10 States by Transaction Amount")

        
        top_states = f_agg_tran.groupby("state", as_index=False)["amount"].sum().sort_values(
            by="amount", ascending=False
        )

        fig_states = px.bar(
            top_states,
            x="amount",
            y="state",
            orientation="h",
            text_auto=".2s",
            color_discrete_sequence=[SAGE]
        )
        fig_states.update_layout(
            plot_bgcolor=BG,
            paper_bgcolor=BG,
            font_color=TEXT,
            height=800,
            xaxis=dict(tickfont=dict(color="white")),
            yaxis=dict(autorange="reversed", tickfont=dict(color="white"))
        )
        st.plotly_chart(fig_states, use_container_width=True)



    else :
        if "district_entity_name" in f_top_tran.columns and "district_amount" in f_top_tran.columns:
    
            # Plot 1
            st.subheader("Districts by Transaction Amount")
            top_districts = f_top_tran.groupby("district_entity_name", as_index=False)["district_amount"].sum().sort_values(
                by="district_amount", ascending=False
            )

            fig_dist = px.bar(
                top_districts,
                x="district_amount",
                y="district_entity_name",
                orientation="h",
                text_auto=".2s",
                color_discrete_sequence=[SAGE]
            )
            fig_dist.update_layout(
                plot_bgcolor=BG,
                paper_bgcolor=BG,
                font_color=TEXT,
                xaxis=dict(title="", tickfont=dict(color="white")),
                yaxis=dict(autorange="reversed", tickfont=dict(color="white")),
            )
            st.plotly_chart(fig_dist, use_container_width=True)

            # Plot 2
                
            st.subheader(" Districts by Transaction Count")

            top_dist = f_top_tran.groupby("district_entity_name", as_index=False)["district_count"].sum().sort_values(
                by="district_count", ascending=False
            )

            fig_states = px.bar(
                top_dist,
                x="district_count",
                y="district_entity_name",
                orientation = "h",
                text_auto=".2s",
                color_discrete_sequence=[SAGE]
            )
            fig_states.update_layout(
                plot_bgcolor=BG,
                paper_bgcolor=BG,
                font_color=TEXT,
                xaxis=dict(tickfont=dict(color="white")),
                yaxis=dict(autorange="reversed", tickfont=dict(color="white"))
            )
            st.plotly_chart(fig_states, use_container_width=True)

# -------------------------------------------------
# TAB 2: USERS
# -------------------------------------------------
with tab2:

    if selected_state == "All States":
        st.subheader("Registered Users by State")

        if "registered_users" in map_user.columns:
            user_state = f_map_user.groupby("state", as_index=False)["registered_users"].sum().sort_values(
                by="registered_users", ascending=False
            ).head(10)

            fig_user_state = px.bar(
                user_state,
                x="registered_users",
                y="state",
                orientation="h",
                text_auto=".2s",
                color_discrete_sequence=[SAGE]
            )
            fig_user_state.update_layout(
                plot_bgcolor=BG,
                paper_bgcolor=BG,
                font_color=TEXT,
                xaxis=dict(title="",tickfont=dict(color="white")),
                yaxis=dict(title="", autorange="reversed", tickfont=dict(color="white"))
            )
            
            st.plotly_chart(fig_user_state, use_container_width=True)
    else:
        st.subheader("Registered Users by District")
        
        if "registeredUsers" in f_top_user.columns:
            user_dist = f_top_user.groupby("district_name", as_index=False)["registeredUsers"].sum().sort_values(
                by="registeredUsers", ascending=False
            ).head(10)

            fig_user_state = px.bar(
                user_dist,
                x="registeredUsers",
                y="district_name",
                orientation="h",
                text_auto=".2s",
                color_discrete_sequence=[SAGE]
            )
            fig_user_state.update_layout(
                plot_bgcolor=BG,
                paper_bgcolor=BG,
                font_color=TEXT,
                xaxis=dict(title="",tickfont=dict(color="white")),
                yaxis=dict(title="", autorange="reversed", tickfont=dict(color="white"))
            )
            
            st.plotly_chart(fig_user_state, use_container_width=True)




    if "app_opens" in f_map_user.columns and "district" in f_map_user.columns:
        
        app_df = f_map_user.groupby("district", as_index=False)["app_opens"].sum().sort_values(
            by="app_opens", ascending=False
        ).head(10)
        if len(app_df['app_opens'].unique()) > 1:
            st.subheader("App Opens by District")
            
            app_df = f_map_user.groupby("district", as_index=False)["app_opens"].sum().sort_values(
                by="app_opens", ascending=False
            ).head(10)
            fig_app = px.bar(
                app_df,
                x="app_opens",
                y="district",
                orientation="h",
                text_auto=".2s",
                color_discrete_sequence=[SAGE_LIGHT]
            )
            fig_app.update_layout(
                plot_bgcolor=BG,
                paper_bgcolor=BG,
                font_color=TEXT,
                xaxis=dict(tickfont=dict(color="white")),
                yaxis=dict(autorange="reversed", tickfont=dict(color="white"))
            )
            st.plotly_chart(fig_app, use_container_width=True)

    if "brand" in agg_user.columns and "count" in agg_user.columns:
        
        brand_df = f_agg_user.groupby("brand", as_index=False)["count"].sum().sort_values(
            by="count", ascending=False
        ).head(10)
        if len(brand_df) > 0: 
            st.subheader("Mobile Brand Usage")

            fig_brand = px.bar(
                brand_df,
                x="count",
                y="brand",
                orientation="h",
                text_auto=".2s",
                color_discrete_sequence=[SAGE]
            )
            fig_brand.update_layout(
                plot_bgcolor=BG,
                paper_bgcolor=BG,
                font_color=TEXT,
                xaxis=dict(tickfont=dict(color="white")),
                yaxis=dict(autorange="reversed", tickfont=dict(color="white"))
            )
            st.plotly_chart(fig_brand, use_container_width=True)

# -------------------------------------------------
# TAB 3: Insurance
# -------------------------------------------------
with tab3:
    # st.text(agg_ins.columns) - Index(['state', 'year', 'quarter', 'transaction_type', 'count', 'amount'], dtype='object')
    # st.text(f_map_ins.columns) - 'state', 'year', 'quarter', 'distric', 'insurance_count',        'insurance_amount'
    # st.text(f_top_ins_dis.columns) - 'state', 'year', 'quater', 'district_entity_name', 'district_count', 'district_amount'
    # st.text(f_top_ins_pin.columns) - state', 'year', 'quater', 'pincode_entity_name', 'pincode_count',   'pincode_amount'

    if selected_state == "All States":
        
            
        top_ins_states = f_agg_ins.groupby("state", as_index=False)["amount"].sum().sort_values(
            by="amount", ascending=False
        ).head(10)

        if len(top_ins_states)>0:
            st.subheader("Top 10 States by Insurance Amount")
            fig_states = px.bar(
                top_ins_states,
                x="amount",
                y="state",
                orientation="h",
                text_auto=".2s",
                color_discrete_sequence=[SAGE]
            )
            fig_states.update_layout(
                plot_bgcolor=BG,
                paper_bgcolor=BG,
                font_color=TEXT,
                # xaxis_tickangle=-35
                xaxis=dict(tickfont=dict(color="white")),
                yaxis=dict(autorange="reversed", tickfont=dict(color="white"))
            )
            st.plotly_chart(fig_states, use_container_width=True)

        # Plot 2


        top_ins_states = f_agg_ins.groupby("state", as_index=False)["count"].sum().sort_values(
            by="count", ascending=False
        ).head(10)

        if len(top_ins_states)>0:
            st.subheader("Top 10 States by Insurance Count")
            fig_states = px.bar(
                top_ins_states,
                x="count",
                y="state",
                orientation="h",
                text_auto=".2s",
                color_discrete_sequence=[SAGE]
            )
            fig_states.update_layout(
                plot_bgcolor=BG,
                paper_bgcolor=BG,
                font_color=TEXT,
                # xaxis_tickangle=-35
                xaxis=dict(tickfont=dict(color="white")),
                yaxis=dict(autorange="reversed", tickfont=dict(color="white"))
            )
            st.plotly_chart(fig_states, use_container_width=True)

    # Plot 3

    top_ins_dist = f_map_ins.groupby("distric", as_index=False)["insurance_amount"].sum().sort_values(
        by="insurance_amount", ascending=False
    ).head(10)

    if len(top_ins_dist)>0:
        st.subheader("Top 10 Districts by Insurance Amount")
        fig_states = px.bar(
            top_ins_dist,
            x="insurance_amount",
            y="distric",
            orientation="h",
            text_auto=".2s",
            color_discrete_sequence=[SAGE]
        )
        fig_states.update_layout(
            plot_bgcolor=BG,
            paper_bgcolor=BG,
            font_color=TEXT,
            # xaxis_tickangle=-35
            xaxis=dict(tickfont=dict(color="white")),
            yaxis=dict(autorange="reversed", tickfont=dict(color="white"))
        )
        st.plotly_chart(fig_states, use_container_width=True)

    # Plot 4


    top_ins_dist = f_map_ins.groupby("distric", as_index=False)["insurance_count"].sum().sort_values(
        by="insurance_count", ascending=False
    ).head(10)

    if len(top_ins_dist)>0:
        st.subheader("Top 10 Districts by Insurance Count")
        fig_states = px.bar(
            top_ins_dist,
            x="insurance_count",
            y="distric",
            orientation="h",
            text_auto=".2s",
            color_discrete_sequence=[SAGE]
        )
        fig_states.update_layout(
            plot_bgcolor=BG,
            paper_bgcolor=BG,
            font_color=TEXT,
            # xaxis_tickangle=-35
            xaxis=dict(tickfont=dict(color="white")),
            yaxis=dict(autorange="reversed", tickfont=dict(color="white"))
        )
        st.plotly_chart(fig_states, use_container_width=True)

#  Pincodes  
    # st.text(f_top_ins_pin.columns) - state', 'year', 'quater', 'pincode_entity_name', 'pincode_count',   'pincode_amount'

    top_ins_pin_amt = f_top_ins_pin.groupby("pincode_entity_name", as_index=False)["pincode_amount"].sum().sort_values(
        by="pincode_amount", ascending=False
    ).head(10).reset_index(drop=True)

    # Plot 2


    top_ins_pin_cnt = f_top_ins_pin.groupby("pincode_entity_name", as_index=False)["pincode_count"].sum().sort_values(
        by="pincode_count", ascending=False
    ).head(10).reset_index(drop=True)

    if len(top_ins_pin_amt)>0:
        

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Top 10 Postal by Insurance Amount")

            # Set index starting from 1
            top_ins_pin_amt.index = top_ins_pin_amt.index + 1
            top_ins_pin_amt['pincode_amount'] = top_ins_pin_amt['pincode_amount'].apply(format_cash)
            st.write(top_ins_pin_amt)

        with col2:
            st.subheader("Top 10 Postal codes by Insurance Count")
            
            # Set index starting from 1
            top_ins_pin_cnt.index = top_ins_pin_cnt.index + 1
            top_ins_pin_cnt['pincode_count'] = top_ins_pin_cnt['pincode_count'].apply(lambda x: format_indian(int(x)))
            st.write(top_ins_pin_cnt)
      
# -------------------------------------------------
# TAB 4: Overview
# -------------------------------------------------
with tab4:

    total_overall_amount = agg_tran["amount"].sum() if "amount" in agg_tran.columns else 0
    total_transaction_count = agg_tran["count"].sum() if "count" in agg_tran.columns else 0
    total_registered_users = map_user["registered_users"].sum() if "registered_users" in map_user.columns else 0
    total_avg_value = total_overall_amount / total_transaction_count if total_transaction_count else 0

    total_registered_users = total_registered_users/1e7
    # total_overall_amount = total_overall_amount/1e7


    # HTML + CSS for a single KPI card
    def kpi_card(title, value, bar_color):
        return f"""
        <div style="
            background-color: grey;
            padding: 20px 25px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgb(0 0 0 / 0.1);
            width: 250px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            border-left: 8px solid {bar_color};
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #222;
            ">
            <div style="font-size: 16px; font-weight: 600;">{title}</div>
            <div style="font-size: 16px; font-weight: 700; margin-top: 8px;">{value}</div>

        </div>
        """

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(kpi_card("Total Registered Users", f"{total_registered_users:.2f} Cr", "#60a5fa"), unsafe_allow_html=True)

    with col2:
        st.markdown(kpi_card("Total payment value", f"₹{format_international(total_overall_amount)}", "#38bdf8"), unsafe_allow_html=True)

    with col3:
        st.markdown(kpi_card("All PhonePe transactions", f"{format_international(total_transaction_count)}", "#7dd3fc"), unsafe_allow_html=True)
    with col4:
        st.markdown(kpi_card("Average Transaction Value", f"₹{format_international(total_avg_value)}", "#7dd3fc"), unsafe_allow_html=True)

    st.subheader("Yearly Transaction Trend")

    col1, col2 = st.columns(2)

    with col1:
        
        yearly = agg_tran.groupby("year", as_index=False).agg({
            "amount": "sum",
            "count": "sum"
        })

        fig_year = px.bar(
            yearly,
            x="year",
            y="amount",
            text_auto=".2s",
            color_discrete_sequence=[SAGE]
        )
        fig_year.update_layout(
            plot_bgcolor=BG,
            paper_bgcolor=BG,
            font_color=TEXT,
            title=dict(
                        text="Transaction Amount by Year",
                        font=dict(color="white", size=20)
                        ),
        )
        st.plotly_chart(fig_year, use_container_width=True)

    with col2:
        fig_year = px.bar(
            yearly,
            x="year",
            y="count",
            text_auto=".2s",
            color_discrete_sequence=[SAGE]
        )
        fig_year.update_layout(
            plot_bgcolor=BG,
            paper_bgcolor=BG,
            font_color=TEXT,
            title=dict(
                        text="Transaction Count by Year",
                        font=dict(color="white", size=20)
                        ),
        )
        st.plotly_chart(fig_year, use_container_width=True)



    # Line chart 
    trend = agg_tran.groupby(["year", "quarter"], as_index=False).agg({
            "amount": "sum",
            "count": "sum"
        })
    col1, col2 = st.columns(2)
    with col1:
        fig = px.line(
            trend,
            x="quarter",
            y="amount",
            color="year",   # separate line for each year
            markers=True
        )

        fig.update_layout(
            template="plotly_dark",
            xaxis=dict(tickmode="linear"),
            yaxis=dict(showgrid=False),
            height=500,
            plot_bgcolor=BG,
            paper_bgcolor=BG,
            font_color=TEXT,
            title=dict(
                            text="Transaction Amount by Year and Quarter",
                            font=dict(color="white", size=20)
                        ),
            legend=dict(font=dict(color="white"))

        )

        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.line(
            trend,
            x="quarter",
            y="count",
            color="year",   # separate line for each year
            markers=True
        )

        fig.update_layout(
            template="plotly_dark",
            xaxis=dict(tickmode="linear"),
            yaxis=dict(showgrid=False),
            height=500,

            plot_bgcolor=BG,
            paper_bgcolor=BG,
            font_color=TEXT,
            title=dict(
                            text="Transaction Count by Year and Quarter",
                            font=dict(color="white", size=20)
                        ),
            legend=dict(font=dict(color="white"))

        )

        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Transaction Type")
    if "transaction_type" in agg_tran.columns:
        pie_df = agg_tran.groupby("transaction_type", as_index=False).agg({
            "amount": "sum",
            "count": "sum"
        })
        col1, col2 = st.columns(2)
        with col1:
                
            fig_pie = px.pie(
                pie_df,
                names="transaction_type",
                values="amount",
                hole=0.5
            )
            fig_pie.update_traces(textinfo="percent+label")
            fig_pie.update_layout(
                plot_bgcolor=BG,
                paper_bgcolor=BG,
                font_color=TEXT,
                legend=dict(
                    font=dict(color="white")
                    ),
                title=dict(
                            text="Transaction Amount",
                            font=dict(color="white", size=20)
                        ),
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        with col2:
            fig_pie = px.pie(
                pie_df,
                names="transaction_type",
                values="count",
                hole=0.5
            )
            fig_pie.update_traces(textinfo="percent+label")
            fig_pie.update_layout(
                plot_bgcolor=BG,
                paper_bgcolor=BG,
                font_color=TEXT,
                legend=dict(
                    font=dict(color="white")
                    ),
                title=dict(
                            text="Transaction Count",
                            font=dict(color="white", size=20)
                        ),
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    ############################## 
    # State wise Transaction Amount
    ##############################

    st.subheader("State-wise Transaction Amount Map")

    map_df = agg_tran.groupby("state", as_index=False)["amount"].sum()

    # This uses Plotly's India geographic rendering.

    
    map_df["state"]=map_df["state"].str.strip().replace(state_corrections)
    map_df["state"]=map_df["state"].str.title()
    
    fig=px.choropleth(map_df,
                      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
                      featureidkey="properties.ST_NM",
                      locations="state",
                      color="amount",
                      color_continuous_scale=[[0, "#4da7d4"], [1, SAGE]],
                      
                      )    
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
        geo_bgcolor=BG,
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font_color=TEXT,
        title=dict(
                        text="Transaction Amount Across States",
                        font=dict(color="white", size=20)
                      ),
        margin=dict(l=0, r=0, t=40, b=0)
    )

    st.plotly_chart(fig, use_container_width=True)


    st.subheader("Top 10 States by Transaction Amount")

    top_states = agg_tran.groupby("state", as_index=False)["amount"].sum().sort_values(
        by="amount", ascending=False
    ).head(10)

    fig_states = px.bar(
        top_states,
        x="amount",
        y="state",
        orientation="h",
        text_auto=".2s",
        color_discrete_sequence=[SAGE]
    )
    fig_states.update_layout(
        plot_bgcolor=BG,
        paper_bgcolor=BG,
        font_color=TEXT,
        xaxis=dict(tickfont=dict(color="white")),
        yaxis=dict(autorange="reversed", tickfont=dict(color="white"))
    )
    st.plotly_chart(fig_states, use_container_width=True)

    #### Users

    st.subheader("Total Registered Users by State")

        
    state_users = map_user.groupby("state", as_index=False).agg({
            "registered_users": "sum",
            "app_opens": "sum"
        })
    
    fig_users = px.bar(
        state_users.sort_values(
        by="registered_users", ascending=False
    ),
        x="registered_users",
        y="state",
        orientation="h",
        text_auto=".2s",
        color_discrete_sequence=[SAGE]
    )
    fig_users.update_layout(
        plot_bgcolor=BG,
        paper_bgcolor=BG,
        font_color=TEXT,
        height = 1000,
        xaxis=dict(tickfont=dict(color="white")),
        yaxis=dict(autorange="reversed", tickfont=dict(color="white"))
    )
    st.plotly_chart(fig_users, use_container_width=True)

# -------------------------------------------------
# TAB 5: RAW DATA
# -------------------------------------------------
with tab5:

    # Custom CSS
    st.markdown("""
    <style>
    div.stDownloadButton > button {
        background-color: #2d0b4e;
        color: white;
        border-radius: 8px;
        padding: 8px 18px;
        border: 1px solid #00cfff;
        font-weight: 600;
    }
    div.stDownloadButton > button:hover {
        background-color: #00cfff;
        color: black;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

    # Transaction Data 
    st.subheader("Filtered Transaction Data")

    f_agg_tran_csv = f_agg_tran.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇ Download Data",
        data=f_agg_tran_csv,
        file_name="filtered_transaction_data.csv",
        mime="text/csv",
    )


    f_agg_tran["year"] = f_agg_tran["year"].astype(str)
    st.dataframe(f_agg_tran, use_container_width=True)


    #  User Data
    st.subheader("Filtered Map User Data")
    # Convert dataframe
    f_map_user_csv = f_map_user.to_csv(index=False).encode('utf-8')

    # Button
    st.download_button(
        label="⬇ Download Data",
        data=f_map_user_csv,
        file_name="filtered_users_data.csv",
        mime="text/csv"
    )

    f_map_user["year"] = f_map_user["year"].astype(str)
    st.dataframe(f_map_user, use_container_width=True)


    #  District Transaction 
    st.subheader("Filtered Map District Data")
    # Convert dataframe
    f_map_tran_csv = f_map_tran.to_csv(index=False).encode('utf-8')

    # Button
    st.download_button(
        label="⬇ Download Data",
        data=f_map_tran_csv,
        file_name="filtered_district_data.csv",
        mime="text/csv"
    )

    f_map_tran["year"] = f_map_tran["year"].astype(str)
    st.dataframe(f_map_tran, use_container_width=True)


# # f_agg_user = apply_filters(agg_user)
# # f_agg_ins = apply_filters(agg_ins)

# f_map_ins = apply_filters(map_ins)

# f_top_tran = apply_filters(top_tran)
# f_top_tran_pincode = apply_filters(top_trans_pincodes)

# f_top_user = apply_filters(top_user)
# f_top_user_pin = apply_filters(top_user_pincodes)

# f_top_ins_dis = apply_filters(top_ins_dist)
# f_top_ins_pin = apply_filters(top_ins_pincodes)

