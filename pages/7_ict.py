# -*- coding: utf-8 -*-
"""
Created on Thu Apr  2 19:13:23 2026

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
    page_title="ICT",
    layout="wide"
)

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
st.markdown('<div class="sticky-header">ICT<b> </div>', unsafe_allow_html=True)

# Content spacing
st.markdown('<div class="content">', unsafe_allow_html=True)


# %% Load the data frames

# ICT RRH KPIs
file_path30 = "Data/ict/rrh_all_ict_kpi_status.xls"
ictkpis  =  pd.read_excel(file_path30)

# ICT Health Facility Detail
file_path31 = "Data/ict/ict_detail.xls"
ictDetails  =  pd.read_excel(file_path31)

# ICT gaps
file_path3023 = "Data/ict/rrhict_gaps.xls"
ictgaps  =  pd.read_excel(file_path3023)

# ICT action tracker
file_path3143 = "Data/ict/rrhict_gapsDetail.xls"
ictactiontracker  =  pd.read_excel(file_path3143)


# %% Common filter
# -----------------------------------------------------
# Sidebar Filter for all tables
# -----------------------------------------------------
# Apply the filter for all table

RRH_list = sorted(ictkpis["RRH"].dropna().unique().tolist())
Yr_list  = sorted(ictkpis["Yr"].dropna().unique().tolist())
Qtr_list  = sorted(ictkpis["Qtr"].dropna().unique().tolist())

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
tables = {
    "ict_KPIs": ictkpis,
    "ictdetails": ictDetails,
    "ICT_gaps"   : ictgaps,
    "ict_actionPoints"  : ictactiontracker
    
        }

filtered_tables = {
    name: apply_filters(table, selected_RRH, selected_Yr, selected_Qtr)
    for name, table in tables.items()
}

# -----------------------------------------------------
# Access filtered tables
# -----------------------------------------------------
filter_ict_KPIs = filtered_tables["ict_KPIs"]
filter_ictdetails = filtered_tables["ictdetails"]
filter_ICT_gaps = filtered_tables["ICT_gaps"]
filter_ict_actionPoints = filtered_tables["ict_actionPoints"]

# %% ICT RRH KPIs

# apply the styling
st.markdown(
       """
       <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
           ICT KPI Status, by RRH
       </h2>
       """, 
       unsafe_allow_html=True
   )
# apply the styling

gb = GridOptionsBuilder().from_dataframe(filter_ict_KPIs)

# Enable filtering
gb.configure_default_column(filter = True, sortable=True)

# Freeze RRH column
gb.configure_column("RRH", pinned="left")

# wrap columns
for col in [
    "RRH",
    "Yr",
    "Qtr",
    "%age of labs with functional ICT systems", 
    "%age of labs exclusively using e-LIMS for data mgt.", 
    "%age of labs with EMRs performing HIE with VL,EID LIMS",
    "%age of labs with EMR inteparable with ALIS",
    "% of labs performing e-VL requests",
    "% of labs performing e-EID requests"
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
target_cols = ["%age of labs with functional ICT systems", 
               "%age of labs exclusively using e-LIMS for data mgt.", 
               "%age of labs with EMRs performing HIE with VL,EID LIMS",
               "%age of labs with EMR inteparable with ALIS",
               "% of labs performing e-VL requests",
               "% of labs performing e-EID requests",
               ]


for col in target_cols:
    if col in filter_ict_KPIs.columns:
        gb.configure_column(col, cellStyle=cellstyle_jscode)
        
# Wrap long column headers

# column: %age labs with all the required lab cadres
gb.configure_column(
    "%age of labs with functional ICT systems",
    headerName="%age labs with functional e-LIMS",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# column: %age labs with all the required lab cadres
gb.configure_column(
    "%age of labs exclusively using e-LIMS for data mgt.",
    headerName="%age labs exclusively using e-LIMS for data mgt.",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# column: %age labs with all the required lab cadres
gb.configure_column(
    "%age of labs with EMRs performing HIE with VL,EID LIMS",
    headerName="%age labs with labs with EMRs performing HIE with VL,EID LIMS",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

gb.configure_column(
    "%age of labs with EMR inteparable with ALIS",
    headerName="%age of labs with EMR inteparable with ALIS",
    wrapHeaderText=True,
    autoHeaderHeight=True
)


gb.configure_column(
    "% of labs performing e-VL requests",
    headerName="% of labs performing e-VL requests",
    wrapHeaderText=True,
    autoHeaderHeight=True
)


gb.configure_column(
    "% of labs performing e-EID requests",
    headerName="% of labs performing e-EID requests",
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
       filter_ict_KPIs,
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
    file_name="ict_kpi_byrrh.csv",
    mime="text/csv"
)

# %% The detailed table
st.markdown(
    """
    <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
        Health Facility Line list with ICT Detail
    </h2>
    """, 
    unsafe_allow_html=True
)

# apply the styling

gb = GridOptionsBuilder().from_dataframe(filter_ictdetails)

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
    "Lab has functional ICT systems", 
    "Lab is exclusively using e-LIMS for data mgt.", 
    "Labs' EMR performs HIE with VL,EID LIMS",
    "Lab has effective data connectivity",
    "Which e-LIMS is used in the facility",
    "Labs' EMR is inteparable with ALIS', 'Lab performs e-VL requests",
    "Lab performs e-EID requests",
    "Labs' equipment autosends test data to e-LIMS"
      
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
target_cols = ["Lab has functional ICT systems", 
                   "Lab is exclusively using e-LIMS for data mgt.", 
                   "Labs' EMR performs HIE with VL,EID LIMS",
                   "Lab has effective data connectivity",
                   "Labs' EMR is inteparable with ALIS', 'Lab performs e-VL requests",
                   "Lab performs e-EID requests",
                   "Labs' equipment autosends test data to e-LIMS"
               ]


for col in target_cols:
    if col in filter_ictdetails.columns:
        gb.configure_column(col, cellStyle=cellstyle_jscode)
        


# Wrap long column headers

# column: %age labs with all the required lab cadres
gb.configure_column(
    "Lab has functional ICT systems",
    headerName="Lab has a functional e-LIMS",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# column: %age labs with all the required lab cadres
gb.configure_column(
    "Lab is exclusively using e-LIMS for data mgt.",
    headerName="lab exclusively uses e-LIMS",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# column: %age labs with all the required lab cadres
gb.configure_column(
    "Labs' EMR performs HIE with VL,EID LIMS",
    headerName="labs' EMR performs HIE",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

gb.configure_column(
    "Lab has effective data connectivity",
    headerName="labs has data connectivity",
    wrapHeaderText=True,
    autoHeaderHeight=True
)


gb.configure_column(
    "Which e-LIMS is used in the facility",
    headerName="e-LIMS used in the lab",
    wrapHeaderText=True,
    autoHeaderHeight=True
)


gb.configure_column(
    "Labs' EMR is inteparable with ALIS', 'Lab performs e-VL requests",
    headerName="EMR is inteparable with ALIS",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

gb.configure_column(
    "Lab performs e-VL requests",
    headerName="lab performs e-VL requests",
    wrapHeaderText=True,
    autoHeaderHeight=True
)
gb.configure_column(
    "Lab performs e-EID requests",
    headerName="lab performs e-EID requests",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

gb.configure_column(
    "Labs' equipment autosends test data to e-LIMS",
    headerName="labs' equipment autosends test data to e-LIMS",
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
       filter_ictdetails,
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
       "ict_detail.csv",
       "text/csv"
   )



# %% Gaps
st.markdown(
       """
       <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
           ICT Gaps/challenges identified
       </h2>
       """, 
       unsafe_allow_html=True
   )
# apply the styling

gb = GridOptionsBuilder.from_dataframe(filter_ICT_gaps)

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
for col in filter_ICT_gaps.columns:
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
    filter_ICT_gaps,
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
    file_name="ict_gaps.csv",
    mime="text/csv"
)

# %% Detailed Gaps
st.markdown(
       """
       <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
           ICT Action Tracker
       </h2>
       """, 
       unsafe_allow_html=True
   )
# apply the styling

gb = GridOptionsBuilder.from_dataframe(filter_ict_actionPoints)

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
for col in filter_ict_actionPoints.columns:
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
    filter_ict_actionPoints,
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
    file_name="ict_tracker.csv",
    mime="text/csv"
)


