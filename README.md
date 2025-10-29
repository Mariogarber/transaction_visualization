

# Transaction Visualization

To build the docker image execute:
`docker build -t dashboard .`

To execute the docker image use:
`docker run -d -p 8080:8080 --name dashboard dashboard`

## Overview

**Transaction Visualization** is a Python project designed to process, analyze, and visualize transactional data (e.g., financial transactions, purchases, or payments) through an interactive dashboard.  
It enables exploration of temporal and categorical patterns, filtering, and generating insightful visualizations for better understanding of transaction dynamics.

The project includes:

- A **main dashboard script** (`dashboard.py`)
- **Utility functions** organized under the `functions/` directory
- **Example data** stored in `data/`
- A **Dockerfile** for easy containerized deployment
- A `requirements.txt` for dependency management

---

## Data Description

The `data/` directory contains one or more datasets representing transaction records.  
Each dataset is expected to include information such as transaction time, amount, and category.

| Column | Type | Description |
|---------|------|-------------|
| `transaction_id` | string / int | Unique identifier of the transaction |
| `timestamp` | datetime | Date and time of the transaction |
| `amount` | float | Transaction amount |
| `category` | string | Category or type (e.g., “food”, “transport”, “utilities”) |
| `user_id` | string / int | Unique user identifier (optional) |
| `description` | string | Short description of the transaction (optional) |
| `merchant` | string | Vendor or counterpart (optional) |

> These fields can be customized depending on your dataset.  
> Make sure column names match the expectations of the functions in `functions/`.

---

## Functions and Modules

The `functions/` directory contains helper modules for data loading, processing, visualization, and dashboard configuration.

### `functions/load_data.py`
Handles reading and validating the transaction data.

- **`load_transactions(filepath: str) → pd.DataFrame`**  
  Loads transaction data from CSV or Parquet into a standardized pandas DataFrame.

- **`validate_schema(df: pd.DataFrame)`**  
  Ensures required columns and data types are present.

---

### `functions/transform.py`
Includes preprocessing and transformation logic.

- **`filter_date_range(df, start, end)`**  
  Filters transactions within a specified date range.

- **`aggregate_by_category(df, freq='M')`**  
  Aggregates transaction amounts by category and time frequency (e.g., monthly, weekly).

- **`compute_cumulative(df, group_by=None)`**  
  Computes cumulative transaction amounts globally or per group.

---

### `functions/visualization_utils.py`
Provides reusable plotting utilities for data visualization.

- **`plot_time_series(df, x_col, y_col, **kwargs)`**  
  Plots time series of transaction amounts.

- **`plot_bar_by_category(df, category_col, value_col, **kwargs)`**  
  Creates bar plots comparing amounts per category.

- **`make_dashboard_components(df)`**  
  Builds dashboard components such as filters, dropdowns, and charts.

---

### `functions/dashboard_helpers.py`
Contains functions to initialize and run the interactive dashboard.

- **`create_app(df)`**  
  Builds the dashboard layout and structure (e.g., with Dash).

- **`update_callbacks(app, df)`**  
  Defines the interactive logic between components (callbacks).

- **`serve_dashboard(port=8080)`**  
  Runs the dashboard server locally.

---

## `dashboard.py`

The main entry point for launching the interactive dashboard.
