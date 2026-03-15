
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

st.title("Piping BOQ Engineering Intelligence Dashboard")

st.sidebar.header("Upload BOQ Files")

proposal = st.sidebar.file_uploader("Proposal BOQ", type=["xlsx"])
boq30 = st.sidebar.file_uploader("30% BOQ", type=["xlsx"])
boq60 = st.sidebar.file_uploader("60% BOQ", type=["xlsx"])
boq90 = st.sidebar.file_uploader("90% BOQ", type=["xlsx"])


def load_data(file):
    df = pd.read_excel(file)
    df.columns = df.columns.str.strip().str.upper()
    if "QTY" not in df.columns:
        df["QTY"] = 1
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

st.header(stage + " Analysis")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Items", int(df["QTY"].sum()))

if "TOTAL INCH DIA" in df.columns:
    col2.metric("Total Inch Dia", round(df["TOTAL INCH DIA"].sum(), 2))

if "INCH METER" in df.columns:
    col3.metric("Total Inch Meter", round(df["INCH METER"].sum(), 2))

if "PROCESS_LINE_NO" in df.columns:
    col4.metric("Total Lines", df["PROCESS_LINE_NO"].nunique())


st.subheader("MOC Distribution")

if "BASE_MATERIAL" in df.columns:
    moc = df.groupby("BASE_MATERIAL")["QTY"].sum().reset_index()
    fig = px.pie(moc, names="BASE_MATERIAL", values="QTY")
    st.plotly_chart(fig, use_container_width=True)


st.subheader("Component Distribution")

if "BOQ_MATERIAL_GROUP" in df.columns:
    grp = df.groupby("BOQ_MATERIAL_GROUP")["QTY"].sum().reset_index()
    fig = px.bar(grp, x="BOQ_MATERIAL_GROUP", y="QTY", color="BOQ_MATERIAL_GROUP")
    st.plotly_chart(fig, use_container_width=True)


st.subheader("Metallic vs Non Metallic")

if "CS_NON_CS" in df.columns:
    metal = df.groupby("CS_NON_CS")["QTY"].sum().reset_index()
    fig = px.bar(metal, x="CS_NON_CS", y="QTY", color="CS_NON_CS")
    st.plotly_chart(fig, use_container_width=True)


st.subheader("Pipe Size Distribution")

if "SIZE1" in df.columns:
    fig = px.histogram(df, x="SIZE1")
    st.plotly_chart(fig, use_container_width=True)


st.header("Stage Comparison")

summary = []

for s, data in datasets.items():
    summary.append({
        "Stage": s,
        "Items": data["QTY"].sum(),
        "InchDia": data["TOTAL INCH DIA"].sum() if "TOTAL INCH DIA" in data.columns else 0,
        "InchMeter": data["INCH METER"].sum() if "INCH METER" in data.columns else 0
    })

summary_df = pd.DataFrame(summary)

st.dataframe(summary_df)

fig = px.bar(summary_df, x="Stage", y="InchDia", title="Engineering Maturity")
st.plotly_chart(fig, use_container_width=True)
