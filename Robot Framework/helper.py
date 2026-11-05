from collections import Counter

import pandas as pd
from selenium.webdriver.common.by import By


def read_html_table_to_dataframe(table_element):
    """Convert a Selenium table WebElement into a Pandas DataFrame."""
    rows = table_element.find_elements(By.TAG_NAME, "tr")
    if not rows:
        raise ValueError("No rows (tr) were found in the table.")

    def cells_of(row):
        return [c.text.strip() for c in row.find_elements(By.XPATH, "./th|./td")]

    header = cells_of(rows[0])
    data = [cells_of(r) for r in rows[1:]]
    data = [r for r in data if r]  # skip rows without cells

    return pd.DataFrame(data, columns=header)


def read_plotly_table_to_dataframe(graph_element, filter_date=None, date_column="visit_date"):
    """Read the table trace from a Plotly graph element into a DataFrame."""
    table_data = graph_element.parent.execute_script(
        """
        const graph = arguments[0];
        const trace = (graph.data || []).find(item => item.type === "table");
        if (!trace) {
            return null;
        }
        return {
            headers: trace.header.values,
            columns: trace.cells.values
        };
        """,
        graph_element,
    )
    if not table_data:
        raise ValueError("No Plotly table trace was found in the report.")

    column_names = {
        "Facility Type": "facility_type",
        "Visit Date": "visit_date",
        "Average Time Spent": "avg_time_spent",
    }
    headers = [column_names.get(str(header).strip(), str(header).strip()) for header in table_data["headers"]]
    columns = table_data["columns"]
    if len(headers) != len(columns):
        raise ValueError(
            f"Plotly table has {len(headers)} headers but {len(columns)} data columns."
        )

    df = pd.DataFrame(dict(zip(headers, columns)))
    if filter_date and str(filter_date).strip() not in ("", "None"):
        if date_column not in df.columns:
            raise ValueError(
                f"Column '{date_column}' was not found. Available columns: {list(df.columns)}"
            )
        df = df[df[date_column].astype(str).str[:10] == str(filter_date).strip()]
    return df.reset_index(drop=True)


def read_partitioned_parquet(folder_path, filter_date=None, date_column="date"):
    """Read a partitioned Parquet dataset and optionally filter it by date."""
    df = pd.read_parquet(folder_path)

    if "partition_date" in df.columns and date_column != "partition_date":
        df = df.drop(columns=["partition_date"])

    if filter_date and str(filter_date).strip() not in ("", "None"):
        if date_column not in df.columns:
            raise ValueError(
                f"Column '{date_column}' was not found. Available columns: {list(df.columns)}"
            )
        df = df[df[date_column].astype(str).str[:10] == str(filter_date).strip()]

    return df.reset_index(drop=True)


def _normalize(df, ignore_columns=None):
    """Prepare data for a fair comparison (HTML is all strings, Parquet is typed)."""
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    if ignore_columns:
        df = df.drop(columns=list(ignore_columns), errors="ignore")
    df = df.astype(str).apply(lambda col: col.str.strip())
    return df.replace({"nan": "", "None": "", "NaT": ""})


def compare_dataframes(df_html, df_parquet, ignore_columns=None):
    """Compare two DataFrames for an exact match and return a list of differences.
    An empty list means the DataFrames match exactly."""
    a = _normalize(df_html, ignore_columns)
    b = _normalize(df_parquet, ignore_columns)
    diffs = []

    cols_a, cols_b = set(a.columns), set(b.columns)
    if cols_a != cols_b:
        if cols_a - cols_b:
            diffs.append(f"Columns only in HTML: {sorted(cols_a - cols_b)}")
        if cols_b - cols_a:
            diffs.append(f"Columns only in Parquet: {sorted(cols_b - cols_a)}")
        return diffs

    if len(a) != len(b):
        diffs.append(f"Row count mismatch: HTML={len(a)}, Parquet={len(b)}")

    cols = sorted(a.columns)
    rows_a = Counter(map(tuple, a[cols].values.tolist()))
    rows_b = Counter(map(tuple, b[cols].values.tolist()))

    for row, count in (rows_a - rows_b).items():
        diffs.append(f"Only in HTML (x{count}): {dict(zip(cols, row))}")
    for row, count in (rows_b - rows_a).items():
        diffs.append(f"Only in Parquet (x{count}): {dict(zip(cols, row))}")

    return diffs