# Technical Reference: Intelligent Data Visualization Platform

This document provides a detailed technical deep-dive into the core logic, algorithms, and architectural decisions behind the Intelligent Data Visualization Platform. It is intended for developers and technical stakeholders.

## 1. Data Loading & Preprocessing
**Module**: `src.loader`

The platform uses `pandas` to handle data ingestion.
- **File Support**: `CSV` and `Excel` (.xlsx).
- **Logic**:
    1. Detects file extension.
    2. Loads data using `pd.read_csv()` or `pd.read_excel()`.
    3. **Preprocessing**: Automatically drops rows that are *entirely* empty (`df.dropna(how='all')`) to prevent ghost rows from Excel files affecting statistics.
    4. **Caching**: Uses `@st.cache_data` to ensure large files are not reloaded on every interaction, improving performance.

## 2. Advanced Scan Engine (Auto Exploration)
**Page**: `Auto Exploration` | **Trigger**: "Run Advanced Scan" button

This feature executes a deterministic statistical analysis pipeline to surface insights without user intervention.

### Algorithms & Methods

#### A. Type Inference
- **Numerical Detection**: Uses `df.select_dtypes(include=[np.number])`.
- **Date Detection**: Heuristic approach in `app.py`. Iterates through object/string columns and attempts `pd.to_datetime()`. If successful, the column is cast to datetime; otherwise, it remains as is.

#### B. Outlier Detection
- **Method**: Interquartile Range (IQR) method.
- **Logic**:
    1. Calculate $Q1$ (25th percentile) and $Q3$ (75th percentile).
    2. Calculate $IQR = Q3 - Q1$.
    3. Define bounds:
       - Lower: $Q1 - 1.5 \times IQR$
       - Upper: $Q3 + 1.5 \times IQR$
    4. Any data point outside these bounds is flagged as an outlier.
- **Application**: The system checks the top 3 numeric columns and reports the count of outliers found.

#### C. Correlation Analysis
- **Method**: Pearson Correlation Coefficient.
- **Logic**:
    1. Computes correlation matrix using `df.corr()`.
    2. Filters for absolute values $> 0.7$ (Strong Correlation).
    3. Identifies pairs of variables that meet this threshold to highlight potential causal relationships or redundancies.

#### D. Distribution Analysis
- **Selection Logic**: The system automatically selects the column with the **highest standard deviation** (`std().idxmax()`) to show the most "interesting" distribution.
- **Visualization**: Generates a Box Plot with points enabled to visualize the spread and specific outliers detected in step B.

## 3. Data Copilot (AI Engine)
**Module**: `src.copilot` | **Model**: Google Gemini 2.5 Flash

The Copilot acts as a natural language interface to the dataset. It does *not* send the entire dataset to the LLM (to preserve privacy and token limits).

### Architecture
1.  **Context Injection (`prepare_context`)**:
    Instead of raw rows, the system extracts metadata:
    - Column Names
    - Data Types (`dtypes`)
    - Missing Value Counts
    - Statistical Summary (`df.describe()`)
    - First 3 rows (Sample)
    *This metadata is injected into the system prompt.*

2.  **Prompt Engineering**:
    The system prompt enforces a strict "Code-First" approach.
    - **Instruction**: "If the user asks ANY question about the data... YOU MUST GENERATE PYTHON CODE."
    - **Constraint**: The LLM must output a python block that assumes a variable `df` exists.
    - **Output**: The code must assign the final answer to a variable named `result`.

3.  **Sandboxed Execution**:
    - The generated code is extracted using regex.
    - It is executed via Python's `exec()` function in a local scope where `df` (the actual dataframe) is available.
    - The value of `result` is captured and returned to the UI.

## 4. Smart Dashboard Generation
**Module**: `src.analysis`, `src.visualizer`

The "Smart Builder" automatically constructs a dashboard composition based on data characteristics.

### KPI Extraction Logic (`identify_key_metrics`)
- **Scoring Algorithm**:
    - Iterate through all numerical columns.
    - **Base Score**: +1 if cardinality > 10 (likely continuous, not an ID).
    - **Keyword Boost**: +2 if column name contains: `sales`, `revenue`, `profit`, `amount`, `cost`, `price`, `total`.
- **Selection**: Sorts by score and picks the top 3 columns as primary KPIs.

### Chart Selection Heuristics (`generate_dashboard_charts`)
The system generates a 6-chart grid layout dynamically:
1.  **Trend (Line)**: If a `date` column exists + Primary KPI.
2.  **Composition (Pie)**: If a categorical column exists with low cardinality (2-8 unique values).
3.  **Ranking (Bar)**: If a categorical column exists with high cardinality (>8 values), shows Top 8.
4.  **Relationship (Scatter)**: If at least 2 KPIs exist, plots KPI 1 vs KPI 2.
5.  **Distribution (Histogram)**: Plots distribution of the Primary KPI.
6.  **Secondary Count (Bar)**: Frequency count of the second most relevant categorical column.

## 5. Manual Exploration
**Page**: `Manual Exploration`

Provides a "No-Code" interface for Plotly Express (`px`).
- **State Management**: Uses Streamlit Session State (`st.session_state`) to persist dropdown selections (X-Axis, Y-Axis, Chart Type) even when navigating between pages.
- **Rendering**: Dynamically calls `px.scatter`, `px.line`, `px.bar`, or `px.area` based on the user's dropdown selection.

## 6. Algorithmic Choices: Why Random Forest?
**Module**: `src.analysis` (Function: `analyze_dependencies`)

Although primarily used for dependency analysis (determining which variables drive a target metric), the **Random Forest** algorithm was selected over others (like Linear Regression, SVM, or Neural Networks) for specific reasons suited to this platform:

1.  **Interpretability (Feature Importance)**:
    - The primary goal in data exploration is often *explanation*, not just prediction. Random Forest provides a built-in `feature_importances_` metric, allowing us to mathematically rank which columns affect a target variable the most.
2.  **Robustness to outliers**:
    - User data is often messy. Tree-based models are generally less sensitive to outliers than linear models, meaning we don't need aggressive data cleaning pipelines.
3.  **Handling Non-Linearity**:
    - Relationships in business data are rarely purely linear. Random Forest captures complex, non-linear interactions between variables automatically.
4.  **No Scaling Required**:
    - Unlike distance-based algorithms (K-Means, SVM), Random Forest does not require features to be scaled (normalized) to the same range. This is critical for an "Auto-Exploration" tool where we process diverse datasets without manual tuning.

## 7. Framework Choice: Why Streamlit?
The platform is built on **Streamlit** as the core frontend framework.

- **Data-First Rapid Prototyping**: Streamlit allows for the rapid translation of Python data scripts into interactive web applications without the overhead of a separate frontend stack (React/Vue + REST API).
- **Native Ecosystem Integration**: It has first-class support for `pandas` dataframes and `plotly` charts, which are the backbone of this application.
- **Session State Management**: Streamlit's execution model (rerun on interaction) combined with `st.session_state` simplifies complex state management (like persisting chat history or navigation selection) compared to traditional stateless web frameworks.

## 8. Technology Stack
- **Frontend/App Framework**: Streamlit
- **Data Manipulation**: Pandas, NumPy
- **Machine Learning**: Scikit-Learn (Random Forest Engine)
- **Visualization**: Plotly Express (Interactive JSON-based charts)
- **LLM Integration**: Google GenAI SDK (`google-genai`)
