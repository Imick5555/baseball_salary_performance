import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import plotly.express as px


def load_titanic():
    """Load the titanic dataset via seaborn and do light cleanup."""
    df = sns.load_dataset("titanic")
    # convert some booleans to strings for nice plotting
    df = df.copy()
    bool_cols = df.select_dtypes(include=["bool"]).columns.tolist()
    for c in bool_cols:
        df[c] = df[c].astype("str")
    return df


def run_pca(df, feature_cols, n_components=2):
    X = df[feature_cols].values
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)
    pca = PCA(n_components=n_components)
    comps = pca.fit_transform(Xs)
    return comps, pca.explained_variance_ratio_


def main():
    st.title("Titanic PCA explorer")

    st.markdown(
        """
        Use the ~~controls~~ to choose which **numeric** variables to include in the PCA.  
        Choose a column to color points by and a column to determine marker shapes.
        """
    )

    df = load_titanic()

    st.sidebar.header("PCA inputs")

    # determine candidate columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    non_numeric_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()

    if not numeric_cols:
        st.error("No numeric columns available for PCA.")
        return

    selected_features = st.sidebar.multiselect(
        "Numeric variables to include in PCA",
        options=numeric_cols,
        default=numeric_cols if len(numeric_cols) <= 6 else numeric_cols[:6],
    )

    color_by = st.sidebar.selectbox(
        "Color points by (any column)", options=[None] + list(df.columns), index=0
    )

    marker_by = st.sidebar.selectbox(
        "Marker shapes by (categorical ideally)", options=[None] + non_numeric_cols, index=0
    )

    point_size = st.sidebar.slider("Point size", min_value=4, max_value=24, value=8)

    if len(selected_features) < 2:
        st.warning("Select at least two numeric variables for PCA.")
        st.stop()

    # drop rows with NA in features or selected color/marker columns
    needed_cols = list(selected_features)
    if color_by:
        needed_cols.append(color_by)
    if marker_by:
        needed_cols.append(marker_by)

    # remove duplicates while preserving order so DataFrame indexing doesn't pass duplicate names
    needed_cols = list(dict.fromkeys(needed_cols))

    df_clean = df.dropna(subset=needed_cols)

    comps, evr = run_pca(df_clean, selected_features, n_components=2)
    result = pd.DataFrame(comps, columns=["PC1", "PC2"], index=df_clean.index)
    # attach color/marker columns for plotting
    if color_by:
        result["color"] = df_clean[color_by].values
    else:
        result["color"] = "All"
    if marker_by:
        result["marker"] = df_clean[marker_by].astype(str).values
    else:
        result["marker"] = None

    # prepare hover columns (keep a few informative columns)
    hover_cols = [c for c in ["survived", "sex", "age", "class"] if c in df_clean.columns]

    # attach hover columns into result so Plotly can reference them
    for c in hover_cols:
        result[c] = df_clean[c].values

    title = f"PCA (PC1 {evr[0]:.2f}, PC2 {evr[1]:.2f} explained var)"

    # build plotly scatter
    if marker_by:
        fig = px.scatter(
            result,
            x="PC1",
            y="PC2",
            color="color",
            symbol="marker",
            labels={"color": color_by or "All", "marker": marker_by or ""},
            title=title,
            hover_data=hover_cols,
            width=900,
            height=600,
        )
    else:
        fig = px.scatter(
            result,
            x="PC1",
            y="PC2",
            color="color",
            labels={"color": color_by or "All"},
            title=title,
            hover_data=hover_cols,
            width=900,
            height=600,
        )

    fig.update_traces(marker=dict(size=point_size))

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Show PCA inputs and result sample"):
        st.write("Input data (cleaned)")
        st.dataframe(df_clean[needed_cols].head(50))
        st.write("PCA components (first 50)")
        st.dataframe(result[["PC1", "PC2", "color", "marker"]].head(50))


if __name__ == "__main__":
    main()
