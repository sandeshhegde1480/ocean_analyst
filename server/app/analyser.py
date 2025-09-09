import pandas as pd
import numpy as np

operations = ['overall analysis', 'compare', 'min', 'max', 'dot-plot', 'bar-plot',  'box plot', 'pie chart', 'mean', 'median', 'mode', 'heatmap']

def compare(path1, path2):
    df1 = pd.read_parquet(path1)
    df2 = pd.read_parquet(path2)

    if not (common_columns := set(df1.columns).intersection(df2.columns)):
        return {"common_columns": [], "comparison": {}}

    comparison = {
        "columns": [],
        "df1_mean": [], "df1_median": [], "df1_min": [], "df1_max": [],
        "df2_mean": [], "df2_median": [], "df2_min": [], "df2_max": []
    }

    for col in common_columns:
        if np.issubdtype(df1[col].dtype, np.number):
            comparison["columns"].append(col)
            comparison["df1_mean"].append(df1[col].mean())
            comparison["df1_median"].append(np.median(df1[col]))
            comparison["df1_min"].append(df1[col].min())
            comparison["df1_max"].append(df1[col].max())

            comparison["df2_mean"].append(df2[col].mean())
            comparison["df2_median"].append(np.median(df2[col]))
            comparison["df2_min"].append(df2[col].min())
            comparison["df2_max"].append(df2[col].max())

    return  {"common_columns": list(common_columns), "comparison": comparison}

def overall_analysis(dataframes):
    report = []
    for x in dataframes:
        cols, means, medians, mins, maxs = [], [],[], [], []
        df = pd.read_parquet(f"{x['path']}")
        columns = df.columns if 'all' in x['columns'] else x['columns']
        for col in columns:
            if np.issubdtype(df[col].dtype, np.number):
                cols.append(col)
                means.append(np.round(df[col].mean(), 2))
                medians.append(np.round(np.median(df[col]), 2))
                mins.append(np.round(np.min(df[col]), 2))
                maxs.append(np.round(np.max(df[col]), 2))
        data = {f"Overall analysis \non\n {x['dataframe_name']}": [i+1 for i in range(len(cols))],'columns': cols, 'Mean': means, 'Medians': medians, 'Minimum Value': mins, 'Maximum Value': maxs}
        data = pd.DataFrame(data)

        report.append(data)

    return report

