# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 11:18:10 2026

@author: HP
"""

import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import plotly.express as px
import matplotlib.pyplot as plt
import altair as alt
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode, ColumnsAutoSizeMode 

# -----------------------------------------------------
# Streamlit Page Config
# -----------------------------------------------------
st.set_page_config(
    page_title="Radiology",
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
st.markdown('<div class="sticky-header">Radiology<b> </div>', unsafe_allow_html=True)

# Content spacing
st.markdown('<div class="content">', unsafe_allow_html=True)



# %% Functions
# Function:  extract value from mixed cell, e.g. 45% (2/5)
def extract_percent(x):
    if pd.isna(x):
        return np.nan
    
    x = str(x).strip()
    
    # Handle common non-numeric cases
    if x in ["", "NA", "NA%", "N/A", "N/A%"]:
        return np.nan
    
    try:
        return float(x.replace("%", ""))
    except ValueError:
        return np.nan


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

# Radiology equipment in place
file_path40 = "D:/CPHL-MOH/Support Supervision/2026/May 2025/radiology/rrh_radgy_kpis.xls"
radgy  =  pd.read_excel(file_path40)

# Microbiology Details
file_path41 = "D:/CPHL-MOH/Support Supervision/2026/May 2025/radiology/radgy_QA.xls"
radgy_Details  =  pd.read_excel(file_path41)


# Gaps
file_path4054 = "D:/CPHL-MOH/Support Supervision/2026/May 2025/radiology/rrhradgy_gaps.xls"
radgygaps  =  pd.read_excel(file_path4054)

# Action tracker
file_path4154 = "D:/CPHL-MOH/Support Supervision/2026/May 2025/radiology/rrhradgy_gapsdetail.xls"
radgyActionTracker  =  pd.read_excel(file_path4154)


# %% Common filters
# Sidebar Filter for all tables

# Define Hub Name
RRH_list = sorted(radgy["RRH"].dropna().unique().tolist())

Yr_list  = sorted(radgy["Yr"].dropna().unique().tolist())
Qtr_list  = sorted(radgy["Qtr"].dropna().unique().tolist())

with st.sidebar:
    st.header("Filters", divider=True)
    
    selected_RRH = st.selectbox("RRH Region:", ["All"] + RRH_list, key="select_rrh")
    
    selected_Yr = st.selectbox("Yr:", ["All"] + Yr_list, key="select_yr")
    selected_Qtr = st.selectbox("Qtr:", ["All"] + Qtr_list, key="select_qtr")
  
# -----------------------------------------------------
# Reusable filter function
# -----------------------------------------------------
def apply_filters(df, rrh, yr, qtr):
    df_filtered = df.copy()
    
    # Filter by RRH if column exists and not "All"
    if "RRH" in df_filtered.columns and rrh != "All":
        df_filtered = df_filtered[df_filtered["RRH"] == rrh]
        
        
    # Filter by Yr if column exists and not "All"
    if "Yr" in df_filtered.columns and yr != "All":
        df_filtered = df_filtered[df_filtered["Yr"] == yr]
        
    # Filter by Qtr if column exists and not "All"
    if "Qtr" in df_filtered.columns and qtr != "All":
        df_filtered = df_filtered[df_filtered["Qtr"] == qtr]
        
        
    return df_filtered

# -----------------------------------------------------
# Apply filter to ALL tables
# -----------------------------------------------------
# 1. Define the dictionary of original tables FIRST
tables = {
    "RRH_radgy": radgy,
    "RRHradgy_Details":  radgy_Details,
    "Radgy_gapsRRH"  : radgygaps,
    "Radgy_actionTracker"  : radgyActionTracker
}

# Apply the filter to that dictionary
filtered_tables = {
    name: apply_filters(table, selected_RRH, selected_Yr, selected_Qtr)
    for name, table in tables.items()
}

# Access the results
filter_RRH_radgy = filtered_tables["RRH_radgy"]
filter_RRHradgy_Details = filtered_tables["RRHradgy_Details"]
filter_Radgy_gapsRRH = filtered_tables["Radgy_gapsRRH"]
filter_Radgy_actionTracker  = filtered_tables["Radgy_actionTracker"]

# %% Radiology KPIs

st.markdown(
       """
       <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
           Radiology KPI Status, by RRH
       </h2>
       """, 
       unsafe_allow_html=True
   )
# apply the styling

gb = GridOptionsBuilder().from_dataframe(filter_RRH_radgy)

# Enable filtering
gb.configure_default_column(filter = True, sortable=True)

# Freeze RRH column
gb.configure_column("RRH", pinned="left")

# wrap columns
for col in [
    "RRH",
    "Yr",
    "Qtr",
    "% of labs with the required Radiology equipment in place and functional", 
    "% of labs with Radiation protection functional", 
    "% of labs with Eff ective Radiology Quality assurance practices in place"
      
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
target_cols = ["% of labs with the required Radiology equipment in place and functional", 
               "% of labs with Radiation protection functional", 
               "% of labs with Eff ective Radiology Quality assurance practices in place"
               ]


for col in target_cols:
    if col in filter_RRH_radgy.columns:
        gb.configure_column(col, cellStyle=cellstyle_jscode)
        

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
gb.configure_grid_options(
    rowHeight=28,
     headerHeight=40,
     groupHeaderHeight=60
        ) 
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

# Display the grid and capture the response
grid_response = AgGrid(
       filter_RRH_radgy,
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
    file_name="radogy_byrrh.csv",
    mime="text/csv"
)


# %% Detail

st.markdown(
    """
    <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
        Health Facility Line list with Microbiology Detail
    </h2>
    """, 
    unsafe_allow_html=True
)

# apply the styling

gb = GridOptionsBuilder().from_dataframe(filter_RRHradgy_Details)

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
    "Radiology equipment in place, and functional",
    "Radiation protection functional",
    "Effective Radiology Quality assurance practices in place"
  ]:
    gb.configure_column(
    col,
    wrapHeaderText=True,
    autoHeaderHeight=True,
    headerClass="small-header"
)


# Define the JavaScript for color coding (Equivalent to the function)
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
target_cols = ["Radiology equipment in place, and functional",
               "Radiation protection functional",
               "Effective Radiology Quality assurance practices in place"
               ]


for col in target_cols:
    if col in filter_RRHradgy_Details.columns:
        gb.configure_column(col, cellStyle=cellstyle_jscode)
        
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
       filter_RRHradgy_Details,
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
       "radiology_detail.csv",
       "text/csv"
   )


# %% Gaps
st.markdown(
       """
       <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
           Radiology Gaps/challenges identified
       </h2>
       """, 
       unsafe_allow_html=True
   )
# apply the styling

gb = GridOptionsBuilder.from_dataframe(filter_Radgy_gapsRRH)

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
for col in filter_Radgy_gapsRRH.columns:
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
    filter_Radgy_gapsRRH,
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
    file_name="radgy_gaps.csv",
    mime="text/csv"
)

# %% Detailed Gaps
st.markdown(
       """
       <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
           Radiology Action Tracker
       </h2>
       """, 
       unsafe_allow_html=True
   )
# apply the styling

gb = GridOptionsBuilder.from_dataframe(filter_Radgy_actionTracker)

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
for col in filter_Radgy_actionTracker.columns:
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
    filter_Radgy_actionTracker,
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
    file_name="radiolgy_tracker.csv",
    mime="text/csv"
)