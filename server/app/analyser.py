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

def overall_analysis(args = []):
    print('overall analysis')
    report = {}
    count = 0
    while args:
        count += 1
        df = pd.read_parquet(args[0])
        args.pop(0)
        cols, means, medians, mins, maxs = [], [], [], [], []
        for col in df.columns:
            if np.issubdtype(df[col].dtype, np.number):
                cols.append(col)
                means.append(df[col].mean())
                medians.append(np.median(df[col]))
                mins.append(np.min(df[col]))
                maxs.append(np.max(df[col]))
        report[f'dataframe_{count}'] = pd.DataFrame({'': [i+1 for i in range(len(cols))],'columns': cols, 'mean': means, 'median': medians, 'minimum': mins, 'maximum': maxs})
    return report

