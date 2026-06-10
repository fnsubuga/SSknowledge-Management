# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 09:28:13 2026

@author: HP
"""

import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import plotly.express as px
import matplotlib.pyplot as plt
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

# -----------------------------------------------------
# Streamlit Page Config
# -----------------------------------------------------
st.set_page_config(
    page_title="Test_Menu",
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
st.markdown('<div class="sticky-header">Test Menu Implementation<b> </div>', unsafe_allow_html=True)

# Content spacing
st.markdown('<div class="content">', unsafe_allow_html=True)


# %% Load the data frames

# Test menu KPI status by RRH region
file_path2 = "Data/TestMenu/test_menu_implementationRRH.xls"
RRHTestMenu = pd.read_excel(file_path2)

# gaps
file_path212 = "Data/TestMenu/rrhtest_menu_gaps.xls"
TestMenugaps = pd.read_excel(file_path212)

# action points
file_path232 = "Data/TestMenu/rrhtest_menu_gapDetail.xls"
TestMenuactions = pd.read_excel(file_path232)


# %% Common filter
# -----------------------------------------------------
# Sidebar Filter for all tables
# -----------------------------------------------------
# Apply the filter for all table

# Define Hub Name
RRH_list = sorted(RRHTestMenu["RRH"].dropna().unique().tolist())

Yr_list  = sorted(RRHTestMenu["Yr"].dropna().unique().tolist())

Qtr_list  = sorted(RRHTestMenu["Qtr"].dropna().unique().tolist())

with st.sidebar:
    st.header("Filters", divider=True)
    
    selected_RRH = st.selectbox("RRH", ["All"] + RRH_list, key="select_rrh")
    
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
    "statusRRHTestMenu": RRHTestMenu,
    "Gaps_RRHTestmenu":TestMenugaps,
    "ActionTracker_all" : TestMenuactions
    
        }


filtered_tables = {
    name: apply_filters(table, selected_RRH, selected_Yr, selected_Qtr)
    for name, table in tables.items()
}

# -----------------------------------------------------
# Access filtered tables
# -----------------------------------------------------
filter_statusRRHTestMenu = filtered_tables["statusRRHTestMenu"]
filter_Gaps_RRHTestmenu = filtered_tables["Gaps_RRHTestmenu"]
filter_ActionTracker_all = filtered_tables["ActionTracker_all"]


# %% Report - Test menu implementation
st.markdown(
    """
    <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
        HR Status, by RRH
    </h2>
    """, 
    unsafe_allow_html=True
)

gb = GridOptionsBuilder().from_dataframe(filter_statusRRHTestMenu)

# Enable filtering
gb.configure_default_column(filter = True, sortable=True)

# Freeze RRH column
gb.configure_column("RRH", pinned="left")

# Wrap long column headers
# RRH
gb.configure_column(
    "RRH",
    headerName="RRH",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# wrap columns
for col in [
    "%age of labs implementing >85% of test menu for health level"
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
cellstyle_jscode2 = JsCode("""
function(params) {
    if (params.value === null || params.value === undefined) return {};

    let valueStr = params.value.toString().trim();

    if (valueStr === "" || valueStr.toLowerCase() === "nan") return {};

    // Extract number (e.g. 33 from "33% (1/3)")
    let match = valueStr.match(/\\d+/);
    if (!match) return {};

    let val = parseInt(match[0]);

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
target_cols = ["%age of labs implementing >85% of test menu for health level"]

# apply the conditioning to the columns of interest
for col in target_cols:
    if col in filter_statusRRHTestMenu.columns:
        gb.configure_column(col, cellStyle=cellstyle_jscode2)

# Configure default column behavior
gb.configure_default_column(
     autoHeight=True,            # Adjust row height to fit wrapped text
    cellStyle={
        'font-size': '10px',
        'padding-top': '0px',   # Optional: reduces space at the top of the cell
        'padding-bottom': '0px' # Optional: reduces space at the bottom of the cell
          } 
)
# spacing in the table
gb.configure_grid_options(
   rowHeight=28,
    headerHeight=40,
    groupHeaderHeight=60) 

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
    filter_statusRRHTestMenu,
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
df_to_download = grid_response['data']

st.download_button(
    label="📥 Download Table",
    data=df_to_download.to_csv(index=False).encode('utf-8'),
    file_name='hr_byrrh.csv',
    mime='text/csv'
)


# %% Gaps
st.markdown(
       """
       <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
           Test Menu Gaps/challenges identified
       </h2>
       """, 
       unsafe_allow_html=True
   )
# apply the styling

gb = GridOptionsBuilder.from_dataframe(filter_Gaps_RRHTestmenu)

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
for col in filter_Gaps_RRHTestmenu.columns:
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
    filter_Gaps_RRHTestmenu,
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
    file_name="testmenu_gaps.csv",
    mime="text/csv"
)

# %% Detailed Gaps
st.markdown(
       """
       <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
           Detailed Test menu Gaps/challenges identified
       </h2>
       """, 
       unsafe_allow_html=True
   )
# apply the styling

gb = GridOptionsBuilder.from_dataframe(filter_ActionTracker_all)

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
for col in filter_ActionTracker_all.columns:
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
    filter_ActionTracker_all,
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
    file_name="testmenu_tracker.csv",
    mime="text/csv"
)

