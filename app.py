
import streamlit as st
import pandas as pd
import plotly.express as px
import time

st.set_page_config(layout="wide")
st.title("Piping BOQ Engineering Analytics")

st.sidebar.header("Upload BOQ Files")

proposal = st.sidebar.file_uploader("Proposal BOQ", type=["xlsx"])
boq30 = st.sidebar.file_uploader("30% BOQ", type=["xlsx"])
boq60 = st.sidebar.file_uploader("60% BOQ", type=["xlsx"])
boq90 = st.sidebar.file_uploader("90% BOQ", type=["xlsx"])

def safe_sum(df, col):
    if col in df.columns:
        return pd.to_numeric(df[col], errors="coerce").fillna(0).sum()
    return 0

def load_data(file):
    progress = st.progress(0)
    progress.progress(10)

    df = pd.read_excel(file)
    progress.progress(40)

    df.columns = df.columns.str.strip().str.upper()
    progress.progress(60)

    for col in ["QTY", "TOTAL INCH DIA", "INCH METER"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    progress.progress(90)
    time.sleep(0.3)
    progress.progress(100)

    return df

datasets = {}

if proposal:
    datasets["Proposal"] = load_data(proposal)

if boq30:
    datasets["30%"] = load_data(boq30)

if boq60:
    datasets["60%"] = load_data(boq60)

if boq90:
    datasets["90%"] = load_data(boq90)

if len(datasets) == 0:
    st.info("Upload at least one BOQ file")
    st.stop()

stage = st.selectbox("Select BOQ Stage", list(datasets.keys()))
df = datasets[stage]

st.header(stage + " Summary")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Items", int(safe_sum(df, "QTY")))
c2.metric("Total Inch Dia", round(safe_sum(df, "TOTAL INCH DIA"), 2))
c3.metric("Total Inch Meter", round(safe_sum(df, "INCH METER"), 2))

if "PROCESS_LINE_NO" in df.columns:
    c4.metric("Total Lines", df["PROCESS_LINE_NO"].nunique())
else:
    c4.metric("Total Lines", "N/A")

st.subheader("MOC Wise Inch-Dia")

if "BASE_MATERIAL" in df.columns and "TOTAL INCH DIA" in df.columns:
    moc = df.groupby("BASE_MATERIAL")["TOTAL INCH DIA"].sum().sort_values(ascending=False).reset_index()
    fig = px.bar(moc, x="BASE_MATERIAL", y="TOTAL INCH DIA")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Component Distribution")

if "BOQ_MATERIAL_GROUP" in df.columns:
    comp = df.groupby("BOQ_MATERIAL_GROUP")["QTY"].sum().sort_values(ascending=False).reset_index()
    fig = px.pie(comp, names="BOQ_MATERIAL_GROUP", values="QTY")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Metallic vs Non Metallic")

if "CS_NON_CS" in df.columns:
    metal = df.groupby("CS_NON_CS")["TOTAL INCH DIA"].sum().reset_index()
    fig = px.bar(metal, x="CS_NON_CS", y="TOTAL INCH DIA")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Pipe Size Distribution")

if "SIZE1" in df.columns:
    fig = px.histogram(df, x="SIZE1")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Top 20 Lines by Inch Dia")

if "PROCESS_LINE_NO" in df.columns and "TOTAL INCH DIA" in df.columns:
    lines = df.groupby("PROCESS_LINE_NO")["TOTAL INCH DIA"].sum().sort_values(ascending=False).head(20)
    st.dataframe(lines)

st.header("BOQ Stage Comparison")

summary = []

for s, data in datasets.items():
    summary.append({
        "Stage": s,
        "Items": safe_sum(data, "QTY"),
        "InchDia": safe_sum(data, "TOTAL INCH DIA"),
        "InchMeter": safe_sum(data, "INCH METER")
    })

summary_df = pd.DataFrame(summary)

st.dataframe(summary_df)

fig = px.bar(summary_df, x="Stage", y="InchDia", title="Engineering BOQ Growth")
st.plotly_chart(fig, use_container_width=True)
