import streamlit as st
import pandas as pd
import numpy as np
# Keep dependencies minimal for students: use Streamlit's built-in charting

st.set_page_config(page_title="BYU Football Explorer", layout="wide")

st.title("BYU Football: Explore Rush vs Pass")

st.markdown(
    """
    This app loads the BYU dataset shipped with the project and shows Rush vs Pass.

    The CSV is loaded from `byu_football_stats_2025.csv` in the project folder.  
    Use the sidebar to toggle between total yards and average yards per attempt.
    """
)

DATA_PATH = "byu_football_stats_2025.csv"
df = pd.read_csv(DATA_PATH)

st.subheader("Data preview")
st.dataframe(df.head(50))

mode = st.sidebar.radio("Metric", ["Total yards", "Average per attempt"]) 

plot_df = df.copy()
plot_df['totalYards'] = plot_df['rushingYards'] + plot_df['netPassingYards']
for c in ["rushingYards", "yardsPerRushAttempt", "netPassingYards", "yardsPerPass", "totalYards"]:
    if c in plot_df.columns:
        plot_df[c] = pd.to_numeric(plot_df[c], errors="coerce")

plot_df = plot_df.reset_index(drop=True)
x_vals = plot_df.index + 1
x_label = "game_number"

if mode == "Total yards":
    plot_df["rush_metric"] = plot_df["rushingYards"] if "rushingYards" in plot_df.columns else np.nan
    plot_df["pass_metric"] = plot_df["netPassingYards"] if "netPassingYards" in plot_df.columns else np.nan
    plot_df["totalYards"] = plot_df["totalYards"] if "totalYards" in plot_df.columns else np.nan
    df_plot = pd.DataFrame({"game_number": x_vals, "Rush": plot_df["rush_metric"].values, "Pass": plot_df["pass_metric"].values, "Total": plot_df["totalYards"].values})
else:
    plot_df["rush_metric"] = plot_df["yardsPerRushAttempt"]
    plot_df["pass_metric"] = plot_df["yardsPerPass"]
    df_plot = pd.DataFrame({"game_number": x_vals, "Rush": plot_df["rush_metric"].values, "Pass": plot_df["pass_metric"].values})

df_plot = df_plot.set_index("game_number")

st.header(f"BYU: {mode}")
st.line_chart(df_plot)
