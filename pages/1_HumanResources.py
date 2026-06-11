# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 17:22:28 2026

@author: HP
"""

import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import plotly.express as px
import matplotlib.pyplot as plt
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode
from pathlib import Path
# -----------------------------------------------------
# Streamlit Page Config
# -----------------------------------------------------
st.set_page_config(
    page_title="HR",
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
st.markdown('<div class="sticky-header">Human Resources<b> </div>', unsafe_allow_html=True)

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

file_path2 = Path("Data") / "HR" / "rrhHR_KPIs.xlsx"

# Fallback to local path when running in Spyder
if not file_path2.exists():
    file_path2 = Path(
        r"D:\Python\dashboard\dashboard\SupportSupervisionRpt\dash_SSupervision\Data\HR\rrhHR_KPIs.xlsx"
    )

HRLevel = pd.read_excel(file_path2)


# HR not available by RRH by level
file_path3 = Path("Data") / "HR" / "rrhHR_KPIs.xlsx"

# Fallback to local path when running in Spyder
if not file_path3.exists():
    file_path3 = Path(
        r"D:\Python\dashboard\dashboard\SupportSupervisionRpt\dash_SSupervision\Data\HR\Prop_cadres_unavailable_RRH_lvl.xlsx"
    )
HRRgns  =  pd.read_excel(file_path3)

# Cadres unavailable by health level
file_path4 = Path("Data") / "HR" / "Prop_cadres_unavailable_lvl.xlsx"
# Fallback to local path when running in Spyder
if not file_path4.exists():
    file_path4 = Path(
        r"D:\Python\dashboard\dashboard\SupportSupervisionRpt\dash_SSupervision\Data\HR\Prop_cadres_unavailable_lvl.xlsx"
    )

CadreAvail  =  pd.read_excel(file_path4)

# HR detailed table
file_path6 = Path("Data") / "HR" / "Detailed_HR.xlsx"
# Fallback to local path when running in Spyder
if not file_path6.exists():
    file_path6 = Path(
        r"D:\Python\dashboard\dashboard\SupportSupervisionRpt\dash_SSupervision\Data\HR\Detailed_HR.xlsx"
    )
HRDetail  =  pd.read_excel(file_path6)

# Gaps
file_path411 = Path("Data") / "HR" / "rrh_Gaps_HR.xlsx"
# Fallback to local path when running in Spyder
if not file_path411.exists():
    file_path411 = Path(
        r"D:\Python\dashboard\dashboard\SupportSupervisionRpt\dash_SSupervision\Data\HR\rrh_Gaps_HR.xlsx"
    )
hrgaps  =  pd.read_excel(file_path411)

# action tracker
file_path611 = Path("Data") / "HR" / "actionTracker_HR.xlsx"
# Fallback to local path when running in Spyder
if not file_path611.exists():
    file_path611 = Path(
        r"D:\Python\dashboard\dashboard\SupportSupervisionRpt\dash_SSupervision\Data\HR\actionTracker_HR.xlsx"
    )
HRactionTracker  =  pd.read_excel(file_path611)

# %% Rename the columns - RRH to not crash with the RRH level naming

HRLevel   =  HRLevel.rename(columns = {
    "RRH"  :  "RRH_Region"
        })

# HR not available by RRH by level data frame


# HR detail Dataframe
HRDetail   =  HRDetail.rename(columns = {
    "RRH"  :  "RRH_Region"
        })

# re-arrange the columns
first_cols = ['RRH_Region','District','HFacility', 'LEVEL','VDate', 'Yr','Qtr']
remaining_cols = [col for col in HRDetail.columns if col not in first_cols]
HRDetail  =  HRDetail[first_cols + remaining_cols]



# %% Common filter
# -----------------------------------------------------
# Sidebar Filter for all tables
# -----------------------------------------------------
# Apply the filter for all table

# Define Hub Name
RRH_list = sorted(HRLevel["RRH_Region"].dropna().unique().tolist())

Yr_list  = sorted(HRLevel["Yr"].dropna().unique().tolist())

Qtr_list  = sorted(HRLevel["Qtr"].dropna().unique().tolist())

with st.sidebar:
    st.header("Filters", divider=True)
    
    selected_RRH = st.selectbox("RRH_Region", ["All"] + RRH_list, key="select_rrh")
    
    selected_Yr = st.selectbox("Yr:", ["All"] + Yr_list, key="select_yr")
    
    selected_Qtr = st.selectbox("Qtr:", ["All"] + Qtr_list, key="select_qtr")

# -----------------------------------------------------
# Reusable filter function
# -----------------------------------------------------
def apply_filters(df, rrh, yr, qtr):
    df_filtered = df.copy()
    
    # Filter by RRH if column exists and not "All"
    if "RRH_Region" in df_filtered.columns and rrh != "All":
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
    "statusHRLevel": HRLevel,
    "Prop_HRRgns": HRRgns,
    "HRdetail" : HRDetail,
    "CadreAvaill": CadreAvail,
    "hrgapsRpt"   : hrgaps,
    "hr_tracker" :  HRactionTracker
    
    }


filtered_tables = {
    name: apply_filters(table, selected_RRH, selected_Yr, selected_Qtr)
    for name, table in tables.items()
}

# -----------------------------------------------------
# Access filtered tables
# -----------------------------------------------------
filter_HR_Status = filtered_tables["statusHRLevel"]
filter_Prop_HRRgns = filtered_tables["Prop_HRRgns"]
filter_HRdetail = filtered_tables["HRdetail"]
filter_CadreAvaill = filtered_tables["CadreAvaill"]
filter_hrgapsRpt = filtered_tables["hrgapsRpt"]
filter_hr_tracker = filtered_tables["hr_tracker"]

# %% rename columns
filter_hrgapsRpt  =  filter_hrgapsRpt.rename(columns  = {
    "RRH"  :  "RRH_Region"
        })


filter_hr_tracker   =  filter_hr_tracker.rename(columns = {
    "RRH"  :  "RRH_Region"
    })


# %% HR KPIs 
st.markdown(
    """
    <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
        HR Status, by RRH
    </h2>
    """, 
    unsafe_allow_html=True
)

gb = GridOptionsBuilder().from_dataframe(filter_HR_Status)

# Enable filtering
gb.configure_default_column(filter = True, sortable=True)

# Freeze RRH column
gb.configure_column("RRH_Region", pinned="left")

# Wrap long column headers
# RRH
gb.configure_column(
    "RRH_Region",
    headerName="RRH_Region",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# wrap columns
for col in [
    "Pct_hrinPlace",
    "Pct_InadequatehrinPlace",
    "Pct_hrCap_buildg",
    "Pct_TB_Cap_Buildg"
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
target_cols = ["Pct_hrinPlace",
               "Pct_InadequatehrinPlace",
               "Pct_hrCap_buildg",
               "Pct_TB_Cap_Buildg"]

# apply the conditioning to the columns of interest
for col in target_cols:
    if col in filter_HR_Status.columns:
        gb.configure_column(col, cellStyle=cellstyle_jscode2)
        
# wrap and rename
gb.configure_column(
    "Pct_hrinPlace",
    headerName="%age of labs that possess all the required cadre categories",
    wrapHeaderText=True,
    autoHeaderHeight=True,
    headerClass="small-header"
)

gb.configure_column(
    "Pct_InadequatehrinPlace",
    headerName="% of labs with required cadres, but, in inadequate numbers in the health facility",
    wrapHeaderText=True,
    autoHeaderHeight=True,
    headerClass="small-header"
)

gb.configure_column(
    "Pct_hrCap_buildg",
    headerName="%age of labs whose staff receive targeted capacity-building",
    wrapHeaderText=True,
    autoHeaderHeight=True,
    headerClass="small-header"
)

gb.configure_column(
    "Pct_TB_Cap_Buildg",
    headerName="%age of labs whose staff received TB molecular training in last 2 Yrs",
    wrapHeaderText=True,
    autoHeaderHeight=True,
    headerClass="small-header"
)


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
    filter_HR_Status,
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


# %% Proportion of cadres available by RRH and health level

st.markdown(
    """
    <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
        HR Status:cadre categories available by health level
    </h2>
    """, 
    unsafe_allow_html=True
)


gb = GridOptionsBuilder().from_dataframe(filter_Prop_HRRgns)

# Enable filtering
gb.configure_default_column(filter = True, sortable=True)

# Freeze RRH column
gb.configure_column("List of cadre categories unavailable in the facility", pinned="left")

# Wrap long column headers properly
gb.configure_column(
    "List of cadre categories unavailable in the facility",
    headerName="Cadre",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# -----------------------------
# Conditional Coloring 
# -----------------------------
cellstyle_jscode = JsCode("""
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
target_cols = ["RRH", "HOSPITAL", "HC IV", "HC III"]

for col in target_cols:
    if col in filter_Prop_HRRgns.columns:
        gb.configure_column(col, cellStyle=cellstyle_jscode)
        
              
# Configure default column behavior
gb.configure_default_column(
    wrapText=True,              # Enable text wrapping
    autoHeight=False,            # Adjust row height to fit wrapped text
    cellStyle={
        'font-size': '12px',
        'display': 'flex',
        'align-items': 'center',
        'padding-top': '0px',   # Optional: reduces space at the top of the cell
        'padding-bottom': '0px', # Optional: reduces space at the bottom of the cell
        'margin-bottom': '0px'
          } 
)
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
    filter_Prop_HRRgns,
    gridOptions=grid_options,
    custom_css=custom_css,
    # for downloading
    data_return_mode="FILTERED_AND_SORTED", 
    update_mode=GridUpdateMode.MODEL_CHANGED,
    fit_columns_on_grid_load=True,
    theme='alpine',
    rowHeight=10,
    height=400,
    allow_unsafe_jscode=True 
)

# Add the Download Button
# Extract the data currently shown in the grid (post-filter/sort)
df_to_download = grid_response['data']

st.download_button(
    label="📥 Download Table",
    data=df_to_download.to_csv(index=False).encode('utf-8'),
    file_name='hr_byLvl.csv',
    mime='text/csv'
)



# %% Detailed HR

st.markdown(
    """
    <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
        Health Facility Human Resources Detail
    </h2>
    """, 
    unsafe_allow_html=True
)


gb = GridOptionsBuilder().from_dataframe(filter_HRdetail)

# Enable filtering
gb.configure_default_column(filter = True, sortable=True)

# Freeze RRH column
gb.configure_column("RRH_Region", pinned="left")

# wrap columns
for col in [
    "RRH_Region",
    "District",
    "HFacility",
    "LEVEL",
    "VDate",
     "Yr",
    "Qtr",
    "The facility possesses all the required cadre categories (See attachment)",
    "List of cadre categories unavailable in the facility",
    "The facility has required cadres, but, in inadequate numbers in the health facility",
    "List of HR cadres with inadequate numbers",
    "The staff receive targeted capacity-building",
    "Laboratory workforce received any training (facility or offsite) in TB molecular tools in the last 2 years"    
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
target_cols = ["The facility possesses all the required cadre categories (See attachment)",
               "The staff receive targeted capacity-building",
               "Laboratory workforce received any training (facility or offsite) in TB molecular tools in the last 2 years"]

for col in target_cols:
    if col in filter_HRdetail.columns:
        gb.configure_column(col, cellStyle=cellstyle_jscode3)

# Wrap long column headers properly
# wrap and rename
gb.configure_column(
    "Pct_hrinPlace",
    headerName="%age of labs that possess all the required cadre categories",
    wrapHeaderText=True,
    autoHeaderHeight=True,
    headerClass="small-header"
)

gb.configure_column(
    "Pct_InadequatehrinPlace",
    headerName="% of labs with required cadres, but, in inadequate numbers in the health facility",
    wrapHeaderText=True,
    autoHeaderHeight=True,
    headerClass="small-header"
)

gb.configure_column(
    "Pct_hrCap_buildg",
    headerName="%age of labs whose staff receive targeted capacity-building",
    wrapHeaderText=True,
    autoHeaderHeight=True,
    headerClass="small-header"
)

gb.configure_column(
    "Pct_TB_Cap_Buildg",
    headerName="%age of labs whose staff received TB molecular training in last 2 Yrs",
    wrapHeaderText=True,
    autoHeaderHeight=True,
    headerClass="small-header"
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
    filter_HRdetail,
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
    file_name='hr_detail_report.csv',
    mime='text/csv'
)






# %% Gaps
st.markdown(
       """
       <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
           HR Gaps/challenges identified
       </h2>
       """, 
       unsafe_allow_html=True
   )
# apply the styling

gb = GridOptionsBuilder.from_dataframe(filter_hrgapsRpt)

# Enable filtering
gb.configure_default_column(filter = True, sortable=True, resizable=True, suppressSizeToFit=True)

# Freeze key columns
gb.configure_column(
    "RRH_Region",
    pinned="left",
    width=120
)

gb.configure_column("Yr", width=80)
gb.configure_column("Qtr", width=100)


# Configure all non-pinned columns
for col in filter_hrgapsRpt.columns:
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
    filter_hrgapsRpt,
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
    file_name="hr_gaps.csv",
    mime="text/csv"
)

# %% Detailed Gaps
st.markdown(
       """
       <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
           Detailed HR Gaps/challenges identified
       </h2>
       """, 
       unsafe_allow_html=True
   )
# apply the styling

gb = GridOptionsBuilder.from_dataframe(filter_hr_tracker)

# Enable filtering
gb.configure_default_column(filter = True, sortable=True, resizable=True, suppressSizeToFit=True)

# Freeze key columns
gb.configure_column(
    "RRH_Region",
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
for col in filter_hr_tracker.columns:
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
    filter_hr_tracker,
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
    file_name="HRdetailed_gaps.csv",
    mime="text/csv"
)

