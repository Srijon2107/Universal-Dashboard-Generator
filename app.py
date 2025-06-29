import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import plotly.io as pio

# Page config and styling
st.set_page_config(page_title="📊 Universal Dashboard Generator", layout="wide")

st.markdown("""
    <style>
        .main { background-color: #FAFAFA; }
        .kpi-card {
            background-color: #E2E8F0;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            font-weight: bold;
            color: #1A202C;
            box-shadow: 1px 1px 8px rgba(0,0,0,0.05);
        }
        h1, h2, h3 {
            font-family: 'Segoe UI', sans-serif;
            color: #2D3748;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Universal Dashboard Generator")
st.markdown("Upload any CSV file to instantly generate interactive charts and insights. 🚀")

# File Upload
uploaded_file = st.file_uploader("📁 Upload CSV", type=["csv"])

def generate_chart(df, chart_type, x, y=None, top_n=10):
    if chart_type == "Bar":
        top_data = df.groupby(x)[y].sum().sort_values(ascending=False).reset_index().head(top_n)
        fig = px.bar(top_data, x=x, y=y, color=x, title=f"Top {top_n} {x} by {y}")
    elif chart_type == "Histogram":
        fig = px.histogram(df, x=x, title=f"Histogram of {x}")
    elif chart_type == "Line":
        fig = px.line(df, x=x, y=y, title=f"{y} over {x}")
    elif chart_type == "Scatter":
        fig = px.scatter(df, x=x, y=y, title=f"{y} vs {x}")
    elif chart_type == "Box":
        fig = px.box(df, x=x, y=y, title=f"{y} Distribution across {x}")
    else:
        return None
    fig.update_layout(template="plotly_white")
    return fig

# When file uploaded
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding="ISO-8859-1")
    st.success(f"✅ Data Loaded: {df.shape[0]} rows × {df.shape[1]} columns")

    if st.checkbox("🔍 Show Raw Data"):
        st.dataframe(df, use_container_width=True)

    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    cat_cols = df.select_dtypes(exclude='number').columns.tolist()

    # KPIs
    st.subheader("📌 Key Metrics")
    col1, col2, col3 = st.columns(3)
    col1.markdown(f"<div class='kpi-card'>Total Rows<br><span style='font-size:24px'>{len(df):,}</span></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='kpi-card'>Numeric Columns<br><span style='font-size:24px'>{len(numeric_cols)}</span></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='kpi-card'>Categorical Columns<br><span style='font-size:24px'>{len(cat_cols)}</span></div>", unsafe_allow_html=True)

    # Toggle Chart Mode
    mode = st.radio("Select Mode", ["📈 Single Chart", "📊 Compare Charts"], horizontal=True)

    if mode == "📈 Single Chart":
        st.subheader("📈 Single Chart Generator ")
        chart_type = st.selectbox("Choose Chart Type", ["Bar", "Histogram", "Line", "Scatter", "Box"])
        x_axis = st.selectbox("Select X-axis", options=df.columns)
        y_axis = st.selectbox("Select Y-axis", options=numeric_cols) if chart_type != "Histogram" else None
        top_n = st.slider("Top N (for Bar Chart)", 5, 30, 10) if chart_type == "Bar" else 10

        # Filters
        with st.expander("🧰 Filter Data"):
            filtered_df = df.copy()
            for col in cat_cols:
                opts = st.multiselect(f"Filter {col}", df[col].dropna().unique())
                if opts:
                    filtered_df = filtered_df[filtered_df[col].isin(opts)]

        if st.button("📊 Generate Chart"):
            fig = generate_chart(filtered_df, chart_type, x_axis, y_axis, top_n)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

                # Save chart as interactive HTML
                html_bytes = fig.to_html(full_html=False).encode("utf-8")
                st.download_button(
                label="📥 Download Chart (HTML)",
                data=html_bytes,
                file_name="chart.html",
                mime="text/html")
                    


                # Simplified Dashboard Summary
                st.subheader("🧠 Dashboard Summary")
                summary = []
                if chart_type == "Bar" and y_axis:
                    summary.append(f"📊 This bar chart shows how **{y_axis}** varies across different **{x_axis}** values.")
                    summary.append("🔼 Taller bars represent higher values, indicating better performance.")
                elif chart_type == "Histogram":
                    summary.append(f"📊 This histogram displays the distribution of **{x_axis}** values.")
                    summary.append("🔍 It highlights how frequently each value appears.")
                elif chart_type == "Line":
                    summary.append(f"📈 This line chart tracks **{y_axis}** over **{x_axis}**, showing overall trends.")
                    summary.append("🔄 It's useful to observe upward or downward movement over time.")
                elif chart_type == "Scatter":
                    summary.append(f"📉 This scatter plot compares **{x_axis}** and **{y_axis}** to show possible relationships.")
                    summary.append("🔗 Patterns or clustering might suggest correlation.")
                elif chart_type == "Box":
                    summary.append(f"📦 This box plot displays spread and outliers of **{y_axis}** across **{x_axis}** groups.")
                    summary.append("📐 Helps understand central tendency and variability.")

                summary.append("💡 This visual helps make better data-driven decisions with clarity.")
                for s in summary:
                    st.markdown(f"- {s}")
            else:
                st.error("❌ Could not generate chart.")

    else:
        st.subheader("📊 Multiple Chart Comparison ")
        colA, colB = st.columns(2)
        with colA:
            type1 = st.selectbox("Chart 1 Type", ["Bar", "Histogram", "Line", "Scatter", "Box"])
            x1 = st.selectbox("X-Axis (Chart 1)", options=df.columns)
            y1 = st.selectbox("Y-Axis (Chart 1)", options=numeric_cols) if type1 != "Histogram" else None
        with colB:
            type2 = st.selectbox("Chart 2 Type", ["Bar", "Histogram", "Line", "Scatter", "Box"])
            x2 = st.selectbox("X-Axis (Chart 2)", options=df.columns)
            y2 = st.selectbox("Y-Axis (Chart 2)", options=numeric_cols) if type2 != "Histogram" else None

        if st.button("🔁 Generate Comparison Charts"):
            fig1 = generate_chart(df, type1, x1, y1)
            fig2 = generate_chart(df, type2, x2, y2)
            st.plotly_chart(fig1, use_container_width=True)
            st.plotly_chart(fig2, use_container_width=True)

            # Comparative Summary
            st.subheader("🧠 Comparative Dashboard Summary")
            insights = []
            insights.append(f"📊 Chart 1 uses a **{type1}** plot comparing **{x1}** and **{y1 or x1}**.")
            insights.append(f"📊 Chart 2 uses a **{type2}** plot comparing **{x2}** and **{y2 or x2}**.")
            insights.append("🔍 These charts help compare different aspects or perspectives of the data.")
            insights.append("📌 Use this view to spot differences, patterns, or anomalies across datasets.")
            insights.append("💼 Ideal for identifying key drivers and outliers in business metrics.")

            for i in insights:
                st.markdown(f"- {i}")

else:
    st.info("📂 Upload a CSV file to get started.")
