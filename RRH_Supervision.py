# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 10:36:25 2026

@author: HP
"""

import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode
from pathlib import Path


# -----------------------------------------------------
# Streamlit Page Config
# -----------------------------------------------------
st.set_page_config(
    page_title="Support Supervision Details",
    layout="wide"
)

st.title("Support Supervision Report")



st.markdown("""
            The suppport supervision report 
    
            """
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
st.markdown('<div class="sticky-header">The suppport supervision report<b> </div>', unsafe_allow_html=True)

# Content spacing
st.markdown('<div class="content">', unsafe_allow_html=True)


# %% Load data 

# Total sites visited
file_path = Path("Data") / "visit" / "TotalSites_Visited.xls"

# Fallback to local path when running in Spyder
if not file_path.exists():
    file_path = Path(
        r"D:\Python\dashboard\dashboard\SupportSupervisionRpt\dash_SSupervision\Data\visit\TotalSites_Visited.xls"
    )
TlVisit  =  pd.read_excel(file_path)

# Total sites visited, and by RRH
file_path1 = Path("Data") / "visit" / "RRH_SitesVisited_level.xls"

# Fallback to local path when running in Spyder
if not file_path1.exists():
    file_path1 = Path(
        r"D:\Python\dashboard\dashboard\SupportSupervisionRpt\dash_SSupervision\Data\visit\RRH_SitesVisited_level.xls"
    )
visits  = pd.read_excel(file_path1)

# Line list of visited facilities
file_path3 = Path("Data") / "visit" / "Linelist_sitesVisited.xls"

# Fallback to local path when running in Spyder
if not file_path3.exists():
    file_path3 = Path(
        r"D:\Python\dashboard\dashboard\SupportSupervisionRpt\dash_SSupervision\Data\visit\Linelist_sitesVisited.xls"
    )
Fac_linelist  = pd.read_excel(file_path3)


# All KPIs
file_path32323 = Path("KPI_Summary.xls")
# Fallback to local path when running in Spyder
if not file_path32323.exists():
    file_path32323 = Path(
        r"D:\Python\dashboard\dashboard\SupportSupervisionRpt\dash_SSupervision\KPI_Summary.xls"
    )
allKPIs  = pd.read_excel(file_path32323)

# Gaps
file_path2435 = Path("Data") / "HR" / "aps_HR.xlsx"
# Fallback to local path when running in Spyder
if not file_path2435.exists():
    file_path2435 = Path(
        r"D:\Python\dashboard\dashboard\SupportSupervisionRpt\dash_SSupervision\Data\HR\aps_HR.xlsx"
    )

NatHR_Gaps = pd.read_excel(file_path2435)


# KPI summary table
#file_path4 = "Data/visit/Jan_March/KPI_Summary.xls"
#KPIs  = pd.read_excel(file_path4)
# %% Filters
# Apply the filter for all table

# Define Hub Name
RRH_list = sorted(visits["RRH"].dropna().unique().tolist())

#indicator_list  = sorted(KPIs["Indicator"].dropna().unique().tolist())

Yr_list  = sorted(Fac_linelist["Yr"].dropna().unique().tolist())

Qtr_list  = sorted(Fac_linelist["Qtr"].dropna().unique().tolist())

with st.sidebar:
    st.header("Filters", divider=True)
    
    selected_RRH = st.selectbox("RRH Region:", ["All"] + RRH_list, key="select_rrh")
    
    #selected_Indicator = st.selectbox("Indicator:", ["All"] + indicator_list, key="select_ind")
    
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
        
    # Filter by Indicator if column exists and not "All"
    #if "Indicator" in df_filtered.columns and indicator != "All":
        #df_filtered = df_filtered[df_filtered["Indicator"] == indicator]
        
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
    "Total_Visits": TlVisit,
    "RRH_visits": visits,
    "RRH_linelist":  Fac_linelist,
    "All_kpiSummary"  : allKPIs
    #"kpi_sumry":    KPIs,
    #"RRH_Vslvl":    VLevel 
    
}

# Now apply the filter
filtered_tables = {
    name: apply_filters(table, selected_RRH, selected_Yr, selected_Qtr)
    for name, table in tables.items()
}

# 3. Access the results
filter_Total_Visits = filtered_tables["Total_Visits"]
filter_RRH_visits = filtered_tables["RRH_visits"]
filter_Fac_linelist = filtered_tables["RRH_linelist"]
filter_All_kpiSummary = filtered_tables["All_kpiSummary"]
#filter_kpi_sumry = filtered_tables["kpi_sumry"]
#filter_RRH_Vslvl = filtered_tables["RRH_Vslvl"]


# %% No. sites visited (National)
st.markdown(
    """
    <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
        Number of health labs visited
    </h2>
    """, 
    unsafe_allow_html=True
)
# change Yr type to String
TlVisit["Yr"]  = TlVisit["Yr"].astype(str)

# The table
gb = GridOptionsBuilder().from_dataframe(filter_Total_Visits)

# Enable filtering
gb.configure_default_column(filter = True, sortable=True)

# Freeze RRH column
gb.configure_column("Yr", pinned="left")


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

# Display the grid and capture the response
grid_response = AgGrid(
    filter_Total_Visits,
    gridOptions=grid_options,
    # for downloading
    data_return_mode="FILTERED_AND_SORTED", 
    fit_columns_on_grid_load=True,
    theme='alpine'
)


# %% Total sites visited, and by RRH
st.markdown(
    """
    <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
        Number of health labs visited by RRH Region
    </h2>
    """, 
    unsafe_allow_html=True
)


gb = GridOptionsBuilder().from_dataframe(filter_RRH_visits)

# Enable filtering
gb.configure_default_column(filter = True, sortable=True)

# Freeze RRH column
gb.configure_column("RRH", pinned="left")


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

# Display the grid and capture the response
grid_response = AgGrid(
    filter_RRH_visits,
    gridOptions=grid_options,
    # for downloading
    data_return_mode="FILTERED_AND_SORTED", 
    fit_columns_on_grid_load=True,
    theme='alpine'
)

# Add the Download Button
# Extract the data currently shown in the grid (post-filter/sort)
if grid_response and 'data' in grid_response:
    df_to_download = pd.DataFrame(grid_response['data'])

result = st.download_button(
    label="📥 Download Table",
    data=df_to_download.to_csv(index=False).encode("utf-8"),
    file_name="rrh_sitesVisited.csv",
    mime="text/csv"
)

# %% Line list of health facilities visited

st.markdown(
    """
    <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
        Linelist of health facilities visited by RRH
    </h2>
    """, 
    unsafe_allow_html=True
)


gb = GridOptionsBuilder().from_dataframe(filter_Fac_linelist)

# Enable filtering
gb.configure_default_column(filter = True, sortable=True)

# Freeze RRH column
gb.configure_column("RRH", pinned="left")


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

# Display the grid and capture the response
grid_response = AgGrid(
    filter_Fac_linelist,
    gridOptions=grid_options,
    # for downloading
    data_return_mode="FILTERED_AND_SORTED", 
    fit_columns_on_grid_load=True,
    theme='alpine'
)

# Add the Download Button
# Extract the data currently shown in the grid (post-filter/sort)
if grid_response and 'data' in grid_response:
    df_to_download = pd.DataFrame(grid_response['data'])

result = st.download_button(
    label="📥 Download Table",
    data=df_to_download.to_csv(index=False).encode("utf-8"),
    file_name="list_sitesVisited.csv",
    mime="text/csv"
)



# %% All KPIS
st.markdown(
    """
    <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
        All KPIs - A summary
    </h2>
    """, 
    unsafe_allow_html=True
)

gb = GridOptionsBuilder().from_dataframe(filter_All_kpiSummary)

# Enable filtering
gb.configure_default_column(filter = True, sortable=True)

# Freeze RRH column
gb.configure_column("Lab Section", pinned="left")

gb.configure_column("Yr", width=70)
gb.configure_column("Qtr", width=90)
gb.configure_column("Status", width=140)

gb.configure_column(
    "Indicator",
    width=450,
    wrapText=True,
    autoHeight=True
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
target_cols = ["Status" ]

# apply the conditioning to the columns of interest
for col in target_cols:
    if col in filter_All_kpiSummary.columns:
        gb.configure_column(col, cellStyle=cellstyle_jscode2)
        

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
        "font-size": "12px !important",
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
    filter_All_kpiSummary,
    gridOptions=grid_options,
    custom_css=custom_css,
    # for downloading
    fit_columns_on_grid_load=False,
    theme='alpine',
    allow_unsafe_jscode=True
)

# Add the Download Button
# Extract the data currently shown in the grid (post-filter/sort)
df_to_download = grid_response['data']

st.download_button(
    label="📥 Download Table",
    data=df_to_download.to_csv(index=False).encode('utf-8'),
    file_name='all_kpis.csv',
    mime='text/csv'
)

# %% Overall HR challenges

gap_cols = [
    "Understaffing",
    "Training gaps",
    "Not all Staff required deployed",
    "Inadequate HR funding",
    "Inadequate/No Support Staff",
    "Staff turnover",
    "No promotions",
    "Staff not reporting to upcountry sites"
]

df_plot = NatHR_Gaps.copy()

# create quarterly order
qtr_order = {
    "Jan-Mar": 1,
    "Apri-Jun": 2,
    "Apri-Jun": 2,
    "Jul-Sept": 3,
    "Oct-Dec": 4
}

df_plot["Qtr_Order"] = df_plot["Qtr"].map(qtr_order)

df_plot["Sort_Order"] = (
    df_plot["Yr"] * 10 +
    df_plot["Qtr_Order"]
)

df_plot["Period"] = (
    df_plot["Qtr"] + " " +
    df_plot["Yr"].astype(str)
)

df_plot = df_plot.sort_values("Sort_Order")

# extract percentages
for col in gap_cols:
    df_plot[col] = (
        df_plot[col]
        .astype(str)
        .str.extract(r'([\d\.]+)', expand=False)
        .astype(float)
    )
    
heatmap_df = (
    df_plot
    .set_index("Period")[gap_cols]
    .T
)

# draw the heatmap
fig = px.imshow(
    heatmap_df,
    text_auto=".1f",
    aspect="auto",
    color_continuous_scale="Reds",
    labels=dict(
        x="Quarter",
        y="HR Gap",
        color="% of Sites"
    ),
    title="Common HR Gaps by Quarter"
)

fig.update_layout(
    height=350
)

fig.update_traces(
    textfont_size=9
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# improving scale color
fig = px.imshow(
    heatmap_df,
    text_auto=".1f",
    aspect="auto",
    color_continuous_scale="RdYlGn_r",
    labels=dict(
        x="Quarter",
        y="HR Gap",
        color="% of Sites"
    ),
    title="Common HR Gaps by Quarter"
)





