import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# Keep dependencies minimal for students: show both Streamlit and Matplotlib examples

st.set_page_config(page_title="MLB Data Science Project", layout="wide")
st.title("Baseball Performance vs Salary Analysis")
st.write("This app loads a webscraped sample MLB dataset and analyzes player performance metrics in relation to their salaries.")
st.write("This project is coming down the pipline. Return soon for updates!")

if st.button("Test"):
    st.success("Author has not yet finished this project. Please check back later!")

# st.set_page_config(page_title="BYU Football Explorer", layout="wide")

# st.title("BYU Football: Explore Rush vs Pass")

# st.markdown(
#     """
#     This app loads the BYU dataset shipped with the project and shows Rush vs Pass.

#     The CSV is loaded from `byu_football_stats_2025.csv` in the project folder.  
#     Use the sidebar to toggle between total yards and average yards per attempt.
#     """
# )

# DATA_PATH = "byu_football_stats_2025.csv"
# df = pd.read_csv(DATA_PATH)

# st.subheader("Data preview")
# st.dataframe(df.head(50))

# # mode = st.sidebar.radio("Metric", ["Total yards", "Average per attempt"]) 
# mode = st.radio("Metric", ["Total yards", "Average per attempt"])

# plot_df = df.copy()
# plot_df['totalYards'] = plot_df['rushingYards'] + plot_df['netPassingYards']
# for c in ["rushingYards", "yardsPerRushAttempt", "netPassingYards", "yardsPerPass", "totalYards"]:
#     if c in plot_df.columns:
#         plot_df[c] = pd.to_numeric(plot_df[c], errors="coerce")

# plot_df = plot_df.reset_index(drop=True)
# x_vals = plot_df.index + 1
# x_label = "game_number"

# if mode == "Total yards":
#     plot_df["rush_metric"] = plot_df["rushingYards"] if "rushingYards" in plot_df.columns else np.nan
#     plot_df["pass_metric"] = plot_df["netPassingYards"] if "netPassingYards" in plot_df.columns else np.nan
#     plot_df["totalYards"] = plot_df["totalYards"] if "totalYards" in plot_df.columns else np.nan
#     df_plot = pd.DataFrame({"game_number": x_vals, "Rush": plot_df["rush_metric"].values, "Pass": plot_df["pass_metric"].values, "Total": plot_df["totalYards"].values})
# else:
#     plot_df["rush_metric"] = plot_df["yardsPerRushAttempt"]
#     plot_df["pass_metric"] = plot_df["yardsPerPass"]
#     df_plot = pd.DataFrame({"game_number": x_vals, "Rush": plot_df["rush_metric"].values, "Pass": plot_df["pass_metric"].values})

# df_plot = df_plot.set_index("game_number")

# st.header(f"BYU: {mode}")
# st.line_chart(df_plot)

# st.markdown("## Matplotlib version of the chart")
# fig, ax = plt.subplots(figsize=(10, 4))
# # x values are the index (game numbers)
# x = df_plot.index

# # Plot Rush and Pass (and Total if present)
# ax.plot(x, df_plot['Rush'], label='Rush')
# ax.plot(x, df_plot['Pass'], label='Pass')
# if 'Total' in df_plot.columns:
#     ax.plot(x, df_plot['Total'], label='Total')

# ax.set_xlabel('Game number')
# ax.set_ylabel('Yards' if mode == 'Total yards' else 'Yards per attempt')
# ax.set_title(f'BYU: {mode} (Matplotlib)')
# ax.grid(alpha=0.3)
# ax.legend()
# st.pyplot(fig)

# tab1, tab2 = st.tabs(["Rush Statistics", "Pass Statistics"])

# with tab1:
#     st.markdown("### Rush Statistics")
#     st.write(plot_df[["rushingAttempts", "rushingYards", "yardsPerRushAttempt"]].describe())

# with tab2:
#     col1, col2 = st.columns(2)

#     with col1:
#         col_df = df.copy()
#         col_df = col_df[['thirdDownEff', 'fourthDownEff']]
#         st.bar_chart(col_df, stack=False, height=300)

#     with col2:
#         st.markdown("### Pass Statistics")
#         st.write(plot_df[["netPassingYards", "yardsPerPass"]].describe())