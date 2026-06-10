# -*- coding: utf-8 -*-
"""
Created on Thu Apr  2 10:12:30 2026

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
    page_title="QMS",
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
st.markdown('<div class="sticky-header">Quality Management Systems (QMS)<b> </div>', unsafe_allow_html=True)

# Content spacing
st.markdown('<div class="content">', unsafe_allow_html=True)

# %% Load the data frames
# -----------------------------------------------------
# Load the RRH-Hub Spokes Data
# -----------------------------------------------------

# RRH Summary of KPI indicators
file_path13 = "Data/QMS/rrh_QMS_status.xls"
qms = pd.read_excel(file_path13)

# Tests without EQA Schemes by RRH
file_path15 = "Data/QMS/testNotonEQA_RRH.xls"
NotestEQArrh  =  pd.read_excel(file_path15)

# QMS Detailed Table
file_path14 = "Data/QMS/QMS_details_RRH.xls"
QMSDetail = pd.read_excel(file_path14)

# Gaps
file_path1523 = "Data/QMS/rrhQMS_gaps_RRH.xls"
QMSgaps  =  pd.read_excel(file_path1523)

# QMS Detailed Table
file_path1432 = "Data/QMS/QMS_actiontracker_RRH.xls"
QMSactiontracker = pd.read_excel(file_path1432)


# %% Common filter

# Sidebar Filter for all tables

# Apply the filter for all table

# Define Hub Name
RRH_list = sorted(QMSDetail["RRH"].dropna().unique().tolist())
Yr_list  = sorted(QMSDetail["Yr"].dropna().unique().tolist())
Qtr_list  = sorted(QMSDetail["Qtr"].dropna().unique().tolist())


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
     "QMSKPIs" :   qms,
    "QMS_DetailedTbl": QMSDetail,
    "RRH_EQAScheme":  NotestEQArrh,
    "QMSGaps_rrh"   : QMSgaps,
    "QMS_actionTracker" : QMSactiontracker
          }

filtered_tables = {
    name: apply_filters(table, selected_RRH, selected_Yr, selected_Qtr)
    for name, table in tables.items()
}

# -----------------------------------------------------
# Access filtered tables
# -----------------------------------------------------
filter_QMSKPIs = filtered_tables["QMSKPIs"]
filter_QMS_DetailedTbl = filtered_tables["QMS_DetailedTbl"]
filter_RRH_EQAScheme = filtered_tables["RRH_EQAScheme"]
filter_QMSGaps_rrh = filtered_tables["QMSGaps_rrh"]
filter_QMS_actionTracker = filtered_tables["QMS_actionTracker"]


# %% QMS status by RRH
st.markdown(
       """
       <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
           QMS Status, by RRH
       </h2>
       """, 
       unsafe_allow_html=True
   )
# apply the styling

gb = GridOptionsBuilder().from_dataframe(filter_QMSKPIs)

# Enable filtering
gb.configure_default_column(filter = True, sortable=True)

# Freeze RRH column
gb.configure_column("RRH", pinned="left")



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
target_cols = ["%age of labs not enrolled on a QMS support program, LQMS, SLMTA enrolled onto QMS support program", 
               "%age of labs facility's whose QMS was audited at least once in the 12 months", 
               "%age of audited labs with improving QMS audit scores",
               "%age of labs with all major tests enrolled onto an EQA Scheme",
               "%age of Passing the EQA Scheme"
               ]


for col in target_cols:
    if col in filter_QMSKPIs.columns:
        gb.configure_column(col, cellStyle=cellstyle_jscode)
        
# Wrap long column headers

# column: %age labs with all the required lab cadres
gb.configure_column(
    "%age of labs not enrolled on a QMS support program, LQMS, SLMTA enrolled onto QMS support program",
    headerName="%age non-accredited labs enrolled onto QMS support program",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# column: %age labs with all the required lab cadres
gb.configure_column(
    "%age of labs facility's whose QMS was audited at least once in the 12 months",
    headerName="%age labs enrolled onto QMS, Audited in last 12 months",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# column: %age labs with all the required lab cadres
gb.configure_column(
    "%age of audited labs with improving QMS audit scores",
    headerName="%age audited labs with improving QMS Scores",
    wrapHeaderText=True,
    autoHeaderHeight=True
)


# column: %age labs with all the required lab cadres
gb.configure_column(
    "%age of labs with all major tests enrolled onto an EQA Scheme",
    headerName="%age labs with major lab tests enrolled onto an EQA Scheme",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# column: %age labs with all the required lab cadres
gb.configure_column(
    "%age of Passing the EQA Scheme",
    headerName="%age labs passing the EQA",
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
       filter_QMSKPIs,
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
    file_name="QMS_byrrh.csv",
    mime="text/csv"
)

# %% The detailed table
st.markdown(
    """
    <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
        Health Facility Line list with QMS Detail
    </h2>
    """, 
    unsafe_allow_html=True
)


gb = GridOptionsBuilder().from_dataframe(filter_QMS_DetailedTbl)

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
    "Facility is Accredited or Certified and has maintained accreditation, certification",
    "If not, Health facility is enrolled on a QMS support program, LQMS, SLMTA",
    "The facility's QMS was audited at least once in the 12 months preceding this visit",
    "Facility’s' QMS improving (Improving QMS audit scores, Internal Audit findings)",
    "The facility's key lab tests enrolled onto EQA schemes",
    "If not, indicate the number and list the tests not enrolled EQA",
    "Facility passed all the EQA Schemes for the previous 2 cycles",
    "If not, indicate the number and the tests not passing EQA"
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

    let val = params.value.toString().trim().toUpperCase();

    if (val === "Y") {
        return {backgroundColor: '#28a745', color: 'white'};   // 🔴
    } else if (val === "Partial") {
        return {backgroundColor: '#ffc107', color: 'black'};   // 🟡
    } else if (val === "N") {
        return {backgroundColor: '#dc3545', color: 'white'};   // 🟢
    }

    return {};
}
""")

# Columns to color
target_cols = ["If not, Health facility is enrolled on a QMS support program, LQMS, SLMTA",
               "The facility's QMS was audited at least once in the 12 months preceding this visit",
               "Facility’s' QMS improving (Improving QMS audit scores, Internal Audit findings)",
               "The facility's key lab tests enrolled onto EQA schemes",
               "Facility passed all the EQA Schemes for the previous 2 cycles"
               ]

for col in target_cols:
    if col in filter_QMS_DetailedTbl.columns:
        gb.configure_column(col, cellStyle=cellstyle_jscode)
        
      
# Wrap long column headers

# column: %age labs with all the required lab cadres
gb.configure_column(
    "Facility is Accredited or Certified and has maintained accreditation, certification",
    headerName="Maintained Accreditation",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# column: %age labs with all the required lab cadres
gb.configure_column(
    "If not, Health facility is enrolled on a QMS support program, LQMS, SLMTA",
    headerName="Enrolled onto QMS Support",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# column: %age labs with all the required lab cadres
gb.configure_column(
    "The facility's QMS was audited at least once in the 12 months preceding this visit",
    headerName="QMS audited atleast once in last 12 month",
    wrapHeaderText=True,
    autoHeaderHeight=True
)


# column: %age labs with all the required lab cadres
gb.configure_column(
    "Facility’s' QMS improving (Improving QMS audit scores, Internal Audit findings)",
    headerName="Has improving QMS scores between succesive audits",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# column: %age labs with all the required lab cadres
gb.configure_column(
    "The facility's key lab tests enrolled onto EQA schemes",
    headerName="Major tests enrolled onto EQA schemes",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# column: %age labs with all the required lab cadres
gb.configure_column(
    "If not, indicate the number and list the tests not enrolled EQA",
    headerName="Tests not enrolled onto EQA Scheme",
    wrapHeaderText=True,
    autoHeaderHeight=True,
    cellStyle={
        'fontSize': '8px',     
        'lineHeight': '13px'
        }
)   

# column: %age labs with all the required lab cadres
gb.configure_column(
    "Facility passed all the EQA Schemes for the previous 2 cycles",
    headerName="EQA Passed in last 2 EQA Cycles",
    wrapHeaderText=True,
    autoHeaderHeight=True
)     

# column: %age labs with all the required lab cadres
gb.configure_column(
    "If not, indicate the number and the tests not passing EQA",
    headerName="Tests not passing EQA",
    wrapHeaderText=True,
    autoHeaderHeight=True
)     
      
# Configure default column behavior
gb.configure_default_column(
    wrapText=True,              # Enable text wrapping
    autoHeight=True,            # Adjust row height to fit wrapped text
    cellStyle={
        'font-size': '12px',
        'line-height': '14px',  # Forces lines closer together (try 1.0 or 1.2 as well)
        'padding-top': '2px',   # Optional: reduces space at the top of the cell
        'padding-bottom': '2px' # Optional: reduces space at the bottom of the cell
          } 
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
    filter_QMS_DetailedTbl,
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
    file_name="QMS_detial_byrrh.csv",
    mime="text/csv"
)


# %% %age of sites with major tests enrolled onto EQA scheme
st.markdown(
       """
       <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
           Major tests not enrolled onto an EQA Scheme, by RRH
       </h2>
       """, 
       unsafe_allow_html=True
   )

st.header("", divider="rainbow")
          
# apply the styling

gb = GridOptionsBuilder().from_dataframe(filter_RRH_EQAScheme)

# Enable filtering
gb.configure_default_column(filter = True, sortable=True)

# Freeze RRH column
gb.configure_column("RRH", pinned="left")

        
# Wrap long column headers
# column: %age labs with all the required lab cadres
gb.configure_column(
    "Tests Not enrolled onto an EQA Scheme",
    headerName="Tests Not enrolled onto an EQA Scheme",
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

# display
  
# Display the grid and capture the response
grid_response = AgGrid(
       filter_RRH_EQAScheme,
       gridOptions=grid_options,
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
       "eqa.csv",
       "text/csv"
   )

# %% Gaps
st.markdown(
       """
       <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
           QMS Gaps, challenges identified
       </h2>
       """, 
       unsafe_allow_html=True
   )
# apply the styling

gb = GridOptionsBuilder.from_dataframe(filter_QMSGaps_rrh)

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
for col in filter_QMSGaps_rrh.columns:
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
    filter_QMSGaps_rrh,
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
    file_name="qms_gaps.csv",
    mime="text/csv"
)

# %% Detailed Gaps
st.markdown(
       """
       <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
           QMS Action Tracker
       </h2>
       """, 
       unsafe_allow_html=True
   )
# apply the styling

gb = GridOptionsBuilder.from_dataframe(filter_QMS_actionTracker)

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
for col in filter_QMS_actionTracker.columns:
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
    filter_QMS_actionTracker,
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
    file_name="QMS_tracker.csv",
    mime="text/csv"
)
