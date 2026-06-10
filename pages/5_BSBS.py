# -*- coding: utf-8 -*-
"""
Created on Thu Apr  2 13:07:28 2026

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
    page_title="BSBS",
    page_icon="D:/CPHL-MOH/pics/MoH_logo.png",
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
st.markdown('<div class="sticky-header">Bio Safety Bio Security<b> </div>', unsafe_allow_html=True)

# Content spacing
st.markdown('<div class="content">', unsafe_allow_html=True)


# %% Load the data frames

# BSBS RRH KPIs
file_path16 = "D:/CPHL-MOH/Support Supervision/2026/May 2025/BSBS/rrh_bsbs_KPI_Summary.xls"
bsbsKPI  =  pd.read_excel(file_path16)

# BSBS best practices not implemented
file_path16 = "D:/CPHL-MOH/Support Supervision/2026/May 2025/BSBS/rrh_bstpractices_not_Implemented.xls"
bsbs_prac  =  pd.read_excel(file_path16)


# BSBS Health Facility Detail
file_path17 = "D:/CPHL-MOH/Support Supervision/2026/May 2025/BSBS/hFac_bsbs_details.xls"
bsbsHfac  =  pd.read_excel(file_path17)

# BSBS gaps
file_path1622 = "D:/CPHL-MOH/Support Supervision/2026/May 2025/BSBS/rrh_bsbs_gaps.xls"
bsbs_gaps  =  pd.read_excel(file_path1622)


# BSBS action tracker
file_path1721 = "D:/CPHL-MOH/Support Supervision/2026/May 2025/BSBS/rrh_bsbs_gapsDetail.xls"
bsbs_actintracker  =  pd.read_excel(file_path1721)



# %% Common filter
# -----------------------------------------------------
# Sidebar Filter for all tables
# -----------------------------------------------------
# Apply the filter for all table

# Define Hub Name
RRH_list = sorted(bsbsHfac["RRH"].dropna().unique().tolist())
Yr_list  = sorted(bsbsHfac["Yr"].dropna().unique().tolist())
Qtr_list  = sorted(bsbsHfac["Qtr"].dropna().unique().tolist())


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
    "BSBS_kpi": bsbsKPI,
    "BSBS_pract" : bsbs_prac,
    "BSBS_Detail"  :  bsbsHfac,
    "bsbsgaps"   : bsbs_gaps,
    "bsbsactiontracker" :bsbs_actintracker
    
        }

filtered_tables = {
    name: apply_filters(table, selected_RRH, selected_Yr, selected_Qtr)
    for name, table in tables.items()
}

# -----------------------------------------------------
# Access filtered tables
# -----------------------------------------------------
filter_BSBS_kpi = filtered_tables["BSBS_kpi"]
filter_BSBS_Detail = filtered_tables["BSBS_Detail"]
filter_BSBS_pract = filtered_tables["BSBS_pract"]
filter_bsbsgaps = filtered_tables["bsbsgaps"]
filter_bsbsactiontracker = filtered_tables["bsbsactiontracker"]

# %% Renameing column names
filter_BSBS_pract  =  filter_BSBS_pract.rename(columns = {
    "N"    :  "No. of sites"
        })

# %% BSBS RRH KPIs
# apply the styling
st.markdown(
       """
       <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
           BSBS KPI Status, by RRH
       </h2>
       """, 
       unsafe_allow_html=True
   )
# apply the styling

gb = GridOptionsBuilder().from_dataframe(filter_BSBS_kpi)

# Enable filtering
gb.configure_default_column(filter = True, sortable=True)

# Freeze RRH column
gb.configure_column("RRH", pinned="left")


# wrap columns
for col in [
    "%age of labs with functional incinerators",
    "%age of labs performing BSBS audits",
    "%age of BSBS audit gaps addressed",
    "%age of labs implementing waste management plans"
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
target_cols = [
               "%age of labs with functional incinerators", 
               "%age of labs performing BSBS audits", 
               "%age of BSBS audit gaps addressed", 
               "%age of labs implementing waste management plans"]


for col in target_cols:
    if col in filter_BSBS_kpi.columns:
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

grid_options = gb.build()

# spacing in the table
gb.configure_grid_options(
   rowHeight=28,
    headerHeight=40,
    groupHeaderHeight=60) 



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
       filter_BSBS_kpi,
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
    file_name="BSBS_kpi_byrrh.csv",
    mime="text/csv"
)

# %% Missing BRM practices

# apply the styling
st.markdown(
       """
       <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
           Missing BRM Practices, by RRH
       </h2>
       """, 
       unsafe_allow_html=True
   )
# apply the styling

gb = GridOptionsBuilder().from_dataframe(filter_BSBS_pract)

# Enable filtering
gb.configure_default_column(filter = True, sortable=True)

# Freeze RRH column
gb.configure_column("RRH", pinned="left")


# wrap columns
for col in [
    "BSBS Practices not done",
    "No. of sites"
]:
    gb.configure_column(
    col,
    wrapHeaderText=True,
    autoHeaderHeight=True,
    headerClass="small-header"
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

grid_options = gb.build()

# spacing in the table
gb.configure_grid_options(
   rowHeight=28,
    headerHeight=40,
    groupHeaderHeight=60) 



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
       filter_BSBS_pract,
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
    file_name="BSBS_missingPractices_byrrh.csv",
    mime="text/csv"
)




# %% The detailed table
st.markdown(
    """
    <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
        Health Facility Line list with BSBS Detail
    </h2>
    """, 
    unsafe_allow_html=True
)


gb = GridOptionsBuilder().from_dataframe(filter_BSBS_Detail)

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
    "BRM_assessments_audits_held", 
    "Audit_Gaps_Addressed", 
    "missingBRMPractices",
    "Correct_wasteMgr",
    "missing_wastePractices",
    "Functional_incinarator_contractor"
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
cellstyle_jscode3 = JsCode("""
function(params) {
    if (params.value === null || params.value === undefined) return {};

    let val = params.value.toString().trim();

    if (val === "Y") {
        return {backgroundColor: '#28a745', color: 'white'};
    } else if (val === "Partial") {
        return {backgroundColor: '#ffc107', color: 'black'};
    } else if (val === "N") {
        return {backgroundColor: '#dc3545', color: 'white'};
    }

    return {};
}
""")


# Columns to color
target_cols = ["BRM_assessments_audits_held", 
               "Audit_Gaps_Addressed", 
               "missingBRMPractices",
               "Correct_wasteMgr",
               "missing_wastePractices",
               "Functional_incinarator_contractor"
                              ]

for col in target_cols:
    if col in filter_BSBS_Detail.columns:
        gb.configure_column(col, cellStyle=cellstyle_jscode3)


# Wrap long column headers properly
gb.configure_column(
    "BRM_assessments_audits_held",
    headerName="Lab performs BRM assessments",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

gb.configure_column(
    "Audit_Gaps_Addressed",
    headerName="lab addressed BRM Audit Gaps",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

gb.configure_column(
    "missingBRMPractices",
    headerName="Identified BRM Gaps",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

gb.configure_column(
    "Correct_wasteMgr",
    headerName="Lab performs correct waste management",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

gb.configure_column(
    "missing_wastePractices",
    headerName="Gap in waste management identified",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

gb.configure_column(
    "Functional_incinarator_contractor",
    headerName="Lab has a functional incinerator",
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
        "font-size": "8px !important",
        "line-height": "12px !important",
        "font-weight": "bold"
    }
}

# Display the grid and capture the response
grid_response = AgGrid(
    filter_BSBS_Detail,
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
    file_name="bsbs_detial_byrrh.csv",
    mime="text/csv"
)

# %% Gaps
st.markdown(
       """
       <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
           BSBS Gaps/challenges identified
       </h2>
       """, 
       unsafe_allow_html=True
   )
# apply the styling

gb = GridOptionsBuilder.from_dataframe(filter_bsbsgaps)

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
for col in filter_bsbsgaps.columns:
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
    filter_bsbsgaps,
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
    file_name="bsbs_gaps.csv",
    mime="text/csv"
)

# %% Detailed Gaps
st.markdown(
       """
       <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
           Detailed BSBS Action Tracker
       </h2>
       """, 
       unsafe_allow_html=True
   )
# apply the styling

gb = GridOptionsBuilder.from_dataframe(filter_bsbsactiontracker)

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
for col in filter_bsbsactiontracker.columns:
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
    filter_bsbsactiontracker,
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
    file_name="bsbs_tracker.csv",
    mime="text/csv"
)



