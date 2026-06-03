"""
Project: Labor Market Dashboard
Created By: Elinor Hunt
Date Last Edited: 06/03/2026
"""

# Import Packages
import pandas as pd
import streamlit as st
import plotly.express as px
import openpyxl as opx
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

################################################### BUILD DASHBOARD ####################################################

# ----------------------------------------------------
# Set-Up Page
# ----------------------------------------------------
st.set_page_config(
    page_title="Maine Labor Market Dashboard",
    page_icon="📊",
    layout="wide"
)
# ----------------------------------------------------
# Upload Data
# ----------------------------------------------------
@st.cache_data
def load_data():
    file = "Labor Market Dashboard Data.xlsx"

    employment = pd.read_excel(file, sheet_name="Employment")
    postings = pd.read_excel(file, sheet_name="Job Postings")
    skills = pd.read_excel(file, sheet_name="Skills")
    ai_skills = pd.read_excel(file, sheet_name="AI Skills")

    # Fill down NAICS and industry names in skills sheets
    skills[["NAICS", "Industry Name"]] = skills[["NAICS", "Industry Name"]].ffill()
    ai_skills[["NAICS", "Industry Name"]] = ai_skills[["NAICS", "Industry Name"]].ffill()

    # Standardize column names
    employment = employment.rename(columns={"Sector": "Industry"})
    postings = postings.rename(columns={
        "Industry Name": "Industry",
        "2026 Q1 Postings": "Job Postings"
    })
    skills = skills.rename(columns={"Industry Name": "Industry"})
    ai_skills = ai_skills.rename(columns={"Industry Name": "Industry"})

    return employment, postings, skills, ai_skills


employment, postings, skills, ai_skills = load_data()

st.title("Maine Labor Market Dashboard")
st.caption("Industry level insights into employment and in-demand skills")

# ----------------------------------------------------
# Industry filter
# ----------------------------------------------------
industries = sorted(employment["Industry"].dropna().unique())

selected_industry = st.selectbox(
    "Select an industry",
    industries
)

emp_filtered = employment[employment["Industry"] == selected_industry]
post_filtered = postings[postings["Industry"] == selected_industry]
skills_filtered = skills[skills["Industry"] == selected_industry]
ai_filtered = ai_skills[ai_skills["Industry"] == selected_industry]

# ----------------------------------------------------
# KPI cards
# ----------------------------------------------------
years = sorted(emp_filtered["Year"].unique())

latest_year = years[-1]
previous_year = years[-2]

latest_employment = emp_filtered.loc[
    emp_filtered["Year"] == latest_year,
    "Employment"
].sum()

previous_employment = emp_filtered.loc[
    emp_filtered["Year"] == previous_year,
    "Employment"
].sum()

employment_change = latest_employment - previous_employment
employment_pct_change = (
    employment_change / previous_employment * 100
)

job_postings = post_filtered["Job Postings"].sum()

if "AI Job Postings" in post_filtered.columns:
    ai_postings = post_filtered["AI Job Postings"].sum()
else:
    ai_postings = 0

total_skill_postings = skills_filtered["Postings"].sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    f"Employment, {latest_year}",
    f"{latest_employment:,.0f}"
)

col2.metric(
    f"Employment Growth from {previous_year} to {latest_year}",
    f"{employment_pct_change:.1f}%"
)

col3.metric(
    "2026 Q1 Job Postings",
    f"{job_postings:,.0f}"
)

col4.metric(
    "2026 Q1 AI Job Postings",
    f"{ai_postings:,.0f}"
)

st.divider()

# ----------------------------------------------------
# Employment line chart
# ----------------------------------------------------
st.subheader("Employment Trend")

fig_emp = px.line(
    emp_filtered,
    x="Year",
    y="Employment",
    markers=True,
    title=f"Employment Over Time: {selected_industry}"
)

fig_emp.update_layout(
    xaxis_title="Year",
    yaxis_title="Employment"
)

st.plotly_chart(fig_emp, use_container_width=True)

# ----------------------------------------------------
# Skills and AI skills bar charts
# ----------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top Skills")

    top_skills = skills_filtered.sort_values(
        "Postings",
        ascending=False
    ).head(10)

    fig_skills = px.bar(
        top_skills,
        x="Postings",
        y="Skills",
        color="Skill Classification",
        orientation="h",
        title="Most In-Demand Skills in Job Postings"
    )

    fig_skills.update_layout(
        yaxis={"categoryorder": "total ascending"}
    )

    st.plotly_chart(fig_skills, use_container_width=True)

with col2:
    st.subheader("Top AI Skills")

    top_ai = ai_filtered.dropna(subset=["Skills"]).sort_values(
        "Postings",
        ascending=False
    ).head(10)

    fig_ai = px.bar(
        top_ai,
        x="Postings",
        y="Skills",
        orientation="h",
        title="Most In-Demand AI Skills in Job Postings"
    )

    fig_ai.update_layout(
        yaxis={"categoryorder": "total ascending"}
    )

    st.plotly_chart(fig_ai, use_container_width=True)
