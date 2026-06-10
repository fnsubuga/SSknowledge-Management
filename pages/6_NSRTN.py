# -*- coding: utf-8 -*-
"""
Created on Thu Apr  2 15:13:54 2026

@author: HP
"""

import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import plotly.express as px
import matplotlib.pyplot as plt
import altair as alt
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

# -----------------------------------------------------
# Streamlit Page Config
# -----------------------------------------------------
st.set_page_config(
    page_title="NSRTN",
    page_icon="D:/CPHL-MOH/pics/MoH_logo.png",
    layout="wide"
)

# %% Fix the heading 
st.markdown("""
    <style>
    .sticky-header {
        position: fixed;
        top: 3.5rem;   /* pushes below Streamlit top bar */
        left: 0;
        right: 0;
        width: 100%;
        background-color: #f9f9f9;
        padding: 12px;
        font-size: 18px;
        font-weight: bold;
        text-align: center;
        z-index: 9999;
        border-bottom: 2px solid #ccc;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }
   .content {
        margin-top: 90px;  /* prevents overlap */
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="sticky-header">National Sample and Results Transport Network (NSRTN)<b> </div>', unsafe_allow_html=True)

# Content spacing
st.markdown('<div class="content">', unsafe_allow_html=True)



# %% Functions
# Function:  extract value from mixed cell, e.g. 45% (2/5)
def extract_percent(x):
    if pd.isna(x) or x == "":
        return np.nan
    return float(x.split("%")[0])


# Fucntion:  Color coding - lowest to highest
def col_rag(val):
    if pd.isna(val):
        return ""
    elif val < 50:
        return "color:green; font-weight: bold;"
    elif val < 80:
        return "color:#BA8E23; font-weight: bold;"
    else:
        return "color: red; font-weight: bold;"
    
# Fucntion:  Color coding for normal highest to lowest
def col_rag1(val):
    if pd.isna(val):
        return ""
    elif val < 50:
        return "color:red; font-weight: bold;"
    elif val < 80:
        return "color:#BA8E23; font-weight: bold;"
    else:
        return "color: green; font-weight: bold;"
    

# Fucntion:  Color coding for Y or n
def col_rag2(val):
    if pd.isna(val):
        return ""
    elif val == "Y": # Use == for comparison
        return "color: green; font-weight: bold;"
    elif val == "Partial": # Use == for comparison
        return "color: #BA8E23; font-weight: bold;"
    else:
        return "color: red; font-weight: bold;"

# %% Load the data frames

# NSRTN KPIs
file_path21 = "Data/nsrtn/nsrtn_kpis_rrh.xls"
NSRTN_KPIs  =  pd.read_excel(file_path21)

# NSRTN Details
file_path20 = "Data/nsrtn/health_facility_KPIs.xls"
NSRTN_Details  =  pd.read_excel(file_path20)

# NSRTN gaps
file_path2122 = "Data/nsrtn/rrhnsrtn_gaps.xls"
NSRTN_gaps  =  pd.read_excel(file_path2122)

# NSRTN action tracker
file_path2032 = "Data/nsrtn/rrhnsrtn_gapsDetail.xls"
NSRTN_action  =  pd.read_excel(file_path20)



# %% Common filter (RRH)
# Sidebar Filter for all tables

# Apply the filter for all table

# Define Hub Name
RRH_list = sorted(NSRTN_KPIs["RRH"].dropna().unique().tolist())
Yr_list  = sorted(NSRTN_KPIs["Yr"].dropna().unique().tolist())
Qtr_list  = sorted(NSRTN_KPIs["Qtr"].dropna().unique().tolist())

with st.sidebar:
    st.header("Filters")
    selected_RRH = st.selectbox("RRH:", ["All"] + RRH_list)
    selected_Yr = st.selectbox("Yr:", ["All"] + Yr_list)
    selected_Qtr = st.selectbox("Qtr:", ["All"] + Qtr_list)

# -----------------------------------------------------
# Reusable filter function
# -----------------------------------------------------
def apply_filters(df, rrh, yr, qtr):
    df_filtered = df.copy()
    
    # Filter by RRH if column exists and not "All"
    if "RRH" in df_filtered.columns and rrh != "All":
        df_filtered = df_filtered[df_filtered["RRH"] == rrh]
        
    # Filter by Year if column exists and not "All"
    if "Yr" in df_filtered.columns and yr != "All":
        df_filtered = df_filtered[df_filtered["Yr"] == yr]
        
    # Filter by Quarter if column exists and not "All"
    if "Qtr" in df_filtered.columns and qtr != "All":
        df_filtered = df_filtered[df_filtered["Qtr"] == qtr]
        
    return df_filtered


# -----------------------------------------------------
# Apply filter to ALL tables
# -----------------------------------------------------
# 1. Define the dictionary of original tables FIRST
tables = {
    "RRH_NSRTNKpis": NSRTN_KPIs,
    "NSRTN_Detail":  NSRTN_Details,
    "NSRTN_gaps"   :  NSRTN_gaps,
    "NSRTN_ActionTracker"  : NSRTN_action
}

# apply the filter to that dictionary
filtered_tables = {
    name: apply_filters(table, selected_RRH, selected_Yr, selected_Qtr)
    for name, table in tables.items()
}

# 3. Access the results
filter_NSRTN_KPIs = filtered_tables["RRH_NSRTNKpis"]
filter_NSRTN_Detail = filtered_tables["NSRTN_Detail"]
filter_NSRTN_gaps = filtered_tables["NSRTN_gaps"]
filter_NSRTN_ActionTracker = filtered_tables["NSRTN_ActionTracker"]


# %% NSRTN KPI list, by RRH Region
# apply the styling

st.markdown(
       """
       <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
           NSRTN KPI Status, by RRH
       </h2>
       """, 
       unsafe_allow_html=True
   )
# apply the styling

gb = GridOptionsBuilder().from_dataframe(filter_NSRTN_KPIs)

# Enable filtering
gb.configure_default_column(filter = True, sortable=True)

# Freeze RRH column
gb.configure_column("RRH", pinned="left")

# wrap columns
for col in [
    "RRH",
    "Yr",
    "Qtr",
    "%age of labs visited by sample transporter as scheduled", 
    "%age of hubs with M/bikes timely fueled, serviced as required",
    "%age of BSBS audit gaps addressed",
    "%age of labs with acceptable rejection rates",
    "% of labs with samples ready for pick-up",
    "% of labs with adequate cold chain",
    "% of labs with access to TB DST referral services"
 ]:
    gb.configure_column(
    col,
    wrapHeaderText=True,
    autoHeaderHeight=True,
    headerClass="small-header"
)




# -----------------------------
# Conditional Coloring 
# -----------------------------
cellstyle_jscode = JsCode("""
function(params) {
    if (params.value === null || params.value === undefined) return {};

    let valueStr = params.value.toString().trim();

    // Extract ONLY the first number (handles "40% (2/5)")
    let match = valueStr.match(/^\\d+(\\.\\d+)?/);
    if (!match) return {};

    let val = parseFloat(match[0]);

    // 🔴 High downtime = BAD
    if (val >= 80) {
        return {backgroundColor: '#28a745', color: 'white'};
    } else if (val >= 50) {
        return {backgroundColor: '#ffc107', color: 'black'};
    } else {
        return {backgroundColor: '#dc3545', color: 'white'};
    }
}
""")  

# Columns to color
target_cols = ["%age of labs visited by sample transporter as scheduled", 
               "%age of hubs with M/bikes timely fueled, serviced as required", 
               "%age of labs with acceptable rejection rates",
               "% of labs with samples ready for pick-up",
               "% of labs with adequate cold chain",
               "% of labs with access to TB DST referral services"
               ]


for col in target_cols:
    if col in filter_NSRTN_KPIs.columns:
        gb.configure_column(col, cellStyle=cellstyle_jscode)
        
# Wrap long column headers

# column: %age labs with all the required lab cadres
gb.configure_column(
    "%age of labs visited by sample transporter as scheduled",
    headerName="%age of labs visited by sample transporter as scheduled",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# column: %age labs with all the required lab cadres
gb.configure_column(
    "%age of hubs with M/bikes timely fueled, serviced as required",
    headerName="%age of hubs with bikes timely serviced and fueled",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# column: %age labs with all the required lab cadres
gb.configure_column(
    "%age of labs with acceptable rejection rates",
    headerName="%age of labs with acceptable rejection rates",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# column: %age labs with all the required lab cadres
gb.configure_column(
    "% of labs with samples ready for pick-up",
    headerName="%age of labs with samples ready for pick-up at time sample transporter visits",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# column: %age labs with all the required lab cadres
gb.configure_column(
    "% of labs with adequate cold chain",
    headerName="%age of labs with with adequate cold chain",
    wrapHeaderText=True,
    autoHeaderHeight=True
)


# column: %age labs with all the required lab cadres
gb.configure_column(
    "% of labs with access to TB DST referral services",
    headerName="%age of labs with access to TB DST referral services",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# Configure default column behavior
gb.configure_default_column(
    wrapText=True,              # Enable text wrapping
    autoHeight=True,            # Adjust row height to fit wrapped text
    cellStyle={
        'font-size': '10px',
        'line-height': '12px',  # Forces lines closer together (try 1.0 or 1.2 as well)
        'padding-top': '2px',   # Optional: reduces space at the top of the cell
        'padding-bottom': '2px' # Optional: reduces space at the bottom of the cell
          } 
)
gb.configure_grid_options(domLayout='normal') 
grid_options = gb.build()

# changing font size in the row formated rows
custom_css = {
    # Data cells
    ".ag-cell": {
        "font-size": "10px !important",
        "line-height": "12px !important",
        "padding-top": "0px !important",
        "padding-bottom": "0px !important"
    },

    # Headers for columns with headerClass="small-header"
    ".small-header .ag-header-cell-text": {
        "font-size": "10px !important",
        "line-height": "12px !important",
        "font-weight": "bold"
    }
}



# display
  
# Display the grid and capture the response
grid_response = AgGrid(
       filter_NSRTN_KPIs,
       gridOptions=grid_options,
       custom_css=custom_css,
       # for downloading
       data_return_mode="FILTERED_AND_SORTED", 
       update_mode=GridUpdateMode.MODEL_CHANGED,
       fit_columns_on_grid_load=True,
       theme='alpine',
       allow_unsafe_jscode=True
   )

# Add the Download Button
# Extract the data currently shown in the grid (post-filter/sort)
if grid_response and 'data' in grid_response:
    df_to_download = pd.DataFrame(grid_response['data'])

result = st.download_button(
    label="📥 Download Table",
    data=df_to_download.to_csv(index=False).encode("utf-8"),
    file_name="nstrn_kpi_byrrh.csv",
    mime="text/csv"
)


# %% NSRTN Detailed table

st.markdown(
       """
       <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
           NSRTN Health Facility Line List, NSRTN Status, by RRH
       </h2>
       """, 
       unsafe_allow_html=True
   )
# apply the styling

gb = GridOptionsBuilder().from_dataframe(filter_NSRTN_Detail)

# Enable filtering
gb.configure_default_column(filter = True, sortable=True)

# Freeze RRH column
gb.configure_column("RRH", pinned="left")

# wrap columns
for col in [
    "RRH",
    "District",
    "HFacility",
    "LEVEL",
    "VDate",
    "Yr",
    "Qtr",
    "scheduledVst", 
    "bike_service_fueled", 
    "TAT_withinTarget",
    "Refer_timely",
    "RejtRate",
    "SampleReady_Pickup",
    "Adequate_ColdChain",
    "Access_to_TB_DST_ref"
    
    
 ]:
    gb.configure_column(
    col,
    wrapHeaderText=True,
    autoHeaderHeight=True,
    headerClass="small-header"
)



# -----------------------------
# Conditional Coloring 
# -----------------------------
cellstyle_jscode = JsCode("""
function(params) {
    if (params.value === null || params.value === undefined) {
        return {fontSize: '8px'};
    }

    let val = params.value.toString().trim();

     if (val === "Y" || val === "Yes") {
        return {backgroundColor: '#28a745', color: 'white', fontSize: '8px'};
    } else if (val === "Partial") {
        return {backgroundColor: '#ffc107', color: 'black', fontSize: '8px'};
    } else if (val === "N" || val === "No") {
        return {backgroundColor: '#dc3545', color: 'white', fontSize: '8px'};
    }

    return {fontSize: '8px'};
}
""")

# Columns to color
target_cols = ["scheduledVst", "bike_service_fueled", "TAT_withinTarget", "Refer_timely", "RejtRate",
               "SampleReady_Pickup", "Adequate_ColdChain", "Access_to_TB_DST_ref"
               ]


for col in target_cols:
    if col in filter_NSRTN_Detail.columns:
        gb.configure_column(col, cellStyle=cellstyle_jscode)
        
# Wrap long column headers
# column: scheduledVst
gb.configure_column(
    "District",
    headerName="District",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# column: bike_service_fueled
gb.configure_column(
    "HFacility",
    headerName="Health Facility",
    wrapHeaderText=True,
    autoHeaderHeight=True
)


# column: bike_service_fueled
gb.configure_column(
    "VDate",
    headerName="Visit Date",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# column: scheduledVst
gb.configure_column(
    "scheduledVst",
    headerName="Scheduled Transporter Visits done",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# column: bike_service_fueled
gb.configure_column(
    "bike_service_fueled",
    headerName="Bikes fueled as serviced as required",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# column: TAT_withinTarget
gb.configure_column(
    "TAT_withinTarget",
    headerName="Timely sample receipt TAT",
    wrapHeaderText=True,
    autoHeaderHeight=True
)


# column: Refer_timely
gb.configure_column(
    "Refer_timely",
    headerName="Timely Sample Referral TAT",
    wrapHeaderText=True,
    autoHeaderHeight=True
)


# column: RejtRate
gb.configure_column(
    "RejtRate",
    headerName="Sample rejection rate",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# column: TAT_withinTarget
gb.configure_column(
    "SampleReady_Pickup",
    headerName="samples ready for pickup",
    wrapHeaderText=True,
    autoHeaderHeight=True
)


# column: Refer_timely
gb.configure_column(
    "Adequate_ColdChain",
    headerName="Lab has adequate cold chain",
    wrapHeaderText=True,
    autoHeaderHeight=True
)


# column: RejtRate
gb.configure_column(
    "Access_to_TB_DST_ref",
    headerName="Lab has access to TB DST testing",
    wrapHeaderText=True,
    autoHeaderHeight=True
)


# Configure default column behavior
gb.configure_default_column(
    wrapText=True,              # Enable text wrapping
    autoHeight=True,            # Adjust row height to fit wrapped text
    
    headerClass="small-header",
    cellStyle={
        'font-size': '10px',
        'line-height': '12px',  # Forces lines closer together (try 1.0 or 1.2 as well)
        'padding-top': '2px',   # Optional: reduces space at the top of the cell
        'padding-bottom': '2px' # Optional: reduces space at the bottom of the cell
          } 
)
gb.configure_grid_options(domLayout='normal') 
grid_options = gb.build()

# changing font size in the row formated rows
custom_css = {
    # Data cells
    ".ag-cell": {
        "font-size": "10px !important",
        "line-height": "12px !important",
        "padding-top": "0px !important",
        "padding-bottom": "0px !important"
    },

    # Headers for columns with headerClass="small-header"
    ".small-header .ag-header-cell-text": {
        "font-size": "8px !important",
        "line-height": "12px !important",
        "font-weight": "bold"
    }
}

# display
  
# Display the grid and capture the response
grid_response = AgGrid(
       filter_NSRTN_Detail,
       gridOptions=grid_options,
       custom_css=custom_css,
       # for downloading
       data_return_mode="FILTERED_AND_SORTED", 
       update_mode=GridUpdateMode.MODEL_CHANGED,
       fit_columns_on_grid_load=True,
       theme='alpine',
       allow_unsafe_jscode=True
   )

# Add the Download Button
# Extract the data currently shown in the grid (post-filter/sort)
df_download = grid_response['data']

st.download_button(
       "📥 Download Table",
       df_download.to_csv(index=False).encode('utf-8'),
       "nsrtn_detail.csv",
       "text/csv"
   )

# %% Gaps
st.markdown(
       """
       <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
           NSRTN Gaps/challenges identified
       </h2>
       """, 
       unsafe_allow_html=True
   )
# apply the styling

gb = GridOptionsBuilder.from_dataframe(filter_NSRTN_gaps)

# Enable filtering
gb.configure_default_column(filter = True, sortable=True, resizable=True, suppressSizeToFit=True)

# Freeze key columns
gb.configure_column(
    "RRH",
    pinned="left",
    width=120
)

gb.configure_column("Yr", width=80)
gb.configure_column("Qtr", width=100)


# Configure all non-pinned columns
for col in filter_NSRTN_gaps.columns:
    if col not in ["RRH", "Yr", "Qtr"]:
        gb.configure_column(
            col,
            width=180,
            wrapText=True,
            autoHeight=True,
            headerClass="small-header"
        )

# Configure grid BEFORE build()
gb.configure_grid_options(
    domLayout="normal",
    suppressHorizontalScroll=False,
    alwaysShowHorizontalScroll=True,
    alwaysShowVerticalScroll=True,
    ensureDomOrder=True,
    headerHeight=150,
    rowHeight=40,
    animateRows=True
)

grid_options = gb.build()

custom_css = {

    # Data cells
    ".ag-cell": {
        "font-size": "12px !important",
        "line-height": "12px !important",
        "padding-top": "2px !important",
        "padding-bottom": "2px !important",
        "white-space": "normal !important"
    },

    # Header text
    ".small-header .ag-header-cell-text": {
        "font-size": "12px !important",
        "line-height": "11px !important",
        "font-weight": "bold",
        "white-space": "normal !important"
    },

    # Header cells
    ".ag-header-cell": {
        "padding-top": "2px !important",
        "padding-bottom": "2px !important"
    }
}

grid_response = AgGrid(
    filter_NSRTN_gaps,
    gridOptions=grid_options,
    custom_css=custom_css,
    data_return_mode="FILTERED_AND_SORTED",
    update_mode=GridUpdateMode.MODEL_CHANGED,
    theme="alpine",
    allow_unsafe_jscode=True,
    height=650,
    fit_columns_on_grid_load=False
)

# Add the Download Button
# Extract the data currently shown in the grid (post-filter/sort)
if grid_response and 'data' in grid_response:
    df_to_download = pd.DataFrame(grid_response['data'])

result = st.download_button(
    label="📥 Download Table",
    data=df_to_download.to_csv(index=False).encode("utf-8"),
    file_name="nsrtn_gaps.csv",
    mime="text/csv"
)

# %% Detailed Gaps
st.markdown(
       """
       <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
           NSRTN Action Tracker
       </h2>
       """, 
       unsafe_allow_html=True
   )
# apply the styling

gb = GridOptionsBuilder.from_dataframe(filter_NSRTN_ActionTracker)

# Enable filtering
gb.configure_default_column(filter = True, sortable=True, resizable=True, suppressSizeToFit=True)

# Freeze key columns
gb.configure_column(
    "RRH",
    pinned="left",
    width=120
)

gb.configure_column("District", width=80)

gb.configure_column(
    "HFacility",
    pinned="left",
    width=180
)

gb.configure_column("VDate", width=120)
gb.configure_column("Section", width=120)

# Configure all non-pinned columns
for col in filter_NSRTN_ActionTracker.columns:
    if col not in ["RRH", "HFacility"]:
        gb.configure_column(
            col,
            width=180,
            wrapText=True,
            autoHeight=True,
            headerClass="small-header"
        )

# Configure grid BEFORE build()
gb.configure_grid_options(
    domLayout="normal",
    suppressHorizontalScroll=False,
    alwaysShowHorizontalScroll=True,
    alwaysShowVerticalScroll=True,
    ensureDomOrder=True,
    headerHeight=150,
    rowHeight=40,
    animateRows=True
)

grid_options = gb.build()

custom_css = {

    # Data cells
    ".ag-cell": {
        "font-size": "10px !important",
        "line-height": "12px !important",
        "padding-top": "2px !important",
        "padding-bottom": "2px !important",
        "white-space": "normal !important"
    },

    # Header text
    ".small-header .ag-header-cell-text": {
        "font-size": "12px !important",
        "line-height": "11px !important",
        "font-weight": "bold",
        "white-space": "normal !important"
    },

    # Header cells
    ".ag-header-cell": {
        "padding-top": "2px !important",
        "padding-bottom": "2px !important"
    }
}

grid_response = AgGrid(
    filter_NSRTN_ActionTracker,
    gridOptions=grid_options,
    custom_css=custom_css,
    data_return_mode="FILTERED_AND_SORTED",
    update_mode=GridUpdateMode.MODEL_CHANGED,
    theme="alpine",
    allow_unsafe_jscode=True,
    height=650,
    fit_columns_on_grid_load=False
)

# Add the Download Button
# Extract the data currently shown in the grid (post-filter/sort)
if grid_response and 'data' in grid_response:
    df_to_download = pd.DataFrame(grid_response['data'])

result = st.download_button(
    label="📥 Download Table",
    data=df_to_download.to_csv(index=False).encode("utf-8"),
    file_name="nsrtn_tracker.csv",
    mime="text/csv"
)
