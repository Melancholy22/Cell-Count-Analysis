from pathlib import Path
import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from analysis import initial_analysis, statistical_analysis, subset_analysis, question_1

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "cell-count.db"
INITIAL_ANALYSIS_PATH = BASE_DIR / "initial_analysis.csv"
STATISTICAL_ANALYSIS_PATH = BASE_DIR / "statistical_analysis.csv"

st.set_page_config(
    page_title="Loblaw Bio Cell Count Dashboard",
    page_icon="",
    layout="wide",
)

# Reads the two CSV files and then generates the pandas dataframes
def load_current_results():
    initial_df = pd.read_csv(INITIAL_ANALYSIS_PATH)
    stats_df = pd.read_csv(STATISTICAL_ANALYSIS_PATH)
    return initial_df, stats_df

def run_analysis_from_db():
    with sqlite3.connect(DB_PATH) as conn:
        initial_df = initial_analysis(conn)
        stats_df = statistical_analysis(initial_df)
        subset_analysis(conn)
        average_b_cells = question_1(conn)
    return initial_df, stats_df, average_b_cells

def response_summary(df):
    summary = (
        df.groupby("response")
        .agg(samples=("sample", "nunique"), mean_percentage=("percentage", "mean"))
        .reset_index()
        .sort_values("response")
    )
    summary["mean_percentage"] = summary["mean_percentage"].round(2)
    return summary

def draw_boxplot(df, cell_name):
    fig, ax = plt.subplots(figsize=(6, 4))
    df[df["cell_name"] == cell_name].boxplot(
        column="percentage",
        by="response",
        ax=ax,
        grid=False,
    )
    fig.suptitle("")
    ax.set_title(f"{cell_name} frequency by response")
    ax.set_xlabel("Response")
    ax.set_ylabel("Frequency (%)")
    return fig


def draw_mean_comparison(stats_df):
    chart_df = stats_df.set_index("cell_name")[
        ["mean_responders", "mean_non_responders"]
    ].rename(
        columns={
            "mean_responders": "Responders",
            "mean_non_responders": "Non-responders",
        }
    )
    st.bar_chart(chart_df)


def main():
    st.title("Loblaw Bio Cell Count Dashboard")
    st.caption("Melanoma, miraclib, PBMC samples split by responder status.")

    if INITIAL_ANALYSIS_PATH.exists() and STATISTICAL_ANALYSIS_PATH.exists():
        initial_df, stats_df = load_current_results()
        average_b_cells = None
    elif DB_PATH.exists():
        initial_df, stats_df, average_b_cells = run_analysis_from_db()
    else:
        st.error("Run analysis.py first, or add cell-count.db to rerun the analysis.")
        st.stop()

    filtered_df = initial_df
    filtered_stats_df = stats_df
    cell_options = sorted(initial_df["cell_name"].dropna().unique())

    sample_count = filtered_df["sample"].nunique()
    cell_count = filtered_df["cell_name"].nunique()
    row_count = len(filtered_df)
    response_counts = filtered_df.groupby("response")["sample"].nunique().to_dict()

    metric_cols = st.columns(4)
    metric_cols[0].metric("Samples", f"{sample_count:,}")
    metric_cols[1].metric("Cell types", f"{cell_count:,}")
    metric_cols[2].metric("Rows", f"{row_count:,}")
    metric_cols[3].metric(
        "Responder samples",
        f"{response_counts.get('yes', 0):,}",
        help="Unique samples with response=yes.",
    )

    tab_overview, tab_cell_detail, tab_tables = st.tabs(
        ["Overview", "Cell Detail", "Tables"]
    )

    with tab_overview:
        left, right = st.columns([2, 1])
        with left:
            st.subheader("Mean Frequency by Cell Type")
            draw_mean_comparison(filtered_stats_df)
        with right:
            st.subheader("Response Summary")
            st.dataframe(
                response_summary(filtered_df),
                use_container_width=True,
                hide_index=True,
            )
            if average_b_cells is not None and not average_b_cells.empty:
                value = average_b_cells.iloc[0, 0]
                st.metric("Average B cells, male responders at time 0", f"{value:,.2f}")

    with tab_cell_detail:
        selected_cell = st.selectbox("Cell type", cell_options)
        left, right = st.columns([3, 2])
        with left:
            st.pyplot(draw_boxplot(filtered_df, selected_cell), clear_figure=True)
        with right:
            selected_stats = filtered_stats_df[
                filtered_stats_df["cell_name"] == selected_cell
            ]
            st.subheader("Statistics")
            st.dataframe(
                selected_stats.round(3),
                use_container_width=True,
                hide_index=True,
            )
            st.subheader("Raw Samples")
            st.dataframe(
                filtered_df[filtered_df["cell_name"] == selected_cell]
                .sort_values(["response", "percentage"])
                .reset_index(drop=True),
                use_container_width=True,
            )

    with tab_tables:
        st.subheader("Statistical Analysis")
        st.dataframe(filtered_stats_df.round(3), use_container_width=True, hide_index=True)
        st.download_button(
            "Download statistical analysis",
            filtered_stats_df.to_csv(index=False).encode("utf-8"),
            "statistical_analysis_filtered.csv",
            "text/csv",
        )

        st.subheader("Initial Analysis")
        st.dataframe(filtered_df.reset_index(drop=True), use_container_width=True)
        st.download_button(
            "Download initial analysis",
            filtered_df.to_csv(index=False).encode("utf-8"),
            "initial_analysis_filtered.csv",
            "text/csv",
        )


if __name__ == "__main__":
    main()
