# Intelligent Data Visualization Platform

Welcome to the **Intelligent Data Visualization Platform**, a comprehensive tool designed to simplify data analysis. With features like **Auto Exploration**, **Data Copilot** (powered by Google Gemini), and dynamic **Dashboards**, turning raw data into actionable insights has never been easier.

## 🚀 Features

- **📂 Multi-Format Support**: Upload CSV or Excel files seamlessly.
- **📊 Auto Exploration**: Automatically generate key insights, trends, and distributions with a single click.
- **🤖 Data Copilot**: Interact with your data using natural language. Ask questions like "What is the total revenue?" or "Show me the top 5 products" and get code-backed answers.
- **🔍 Manual Exploration**: Dive deep into your data by creating custom scatter plots and analyses.
- **📉 Interactive Dashboard**: A unified view of your most important metrics and KPIs, complete with global filters.

## 🏗️ System Architecture

The platform is built using a modular architecture to ensure scalability and maintainability.

<img width="1325" height="728" alt="Image" src="https://github.com/user-attachments/assets/d72fe272-4e61-4274-9c54-07830ff38ef8" />

### Components
- **`app.py`**: The main entry point. It handles the UI layout, navigation state, and user interactions.
- **`src.loader`**: Responsible for reading and preprocessing CSV and Excel files.
- **`src.analysis`**: Performs data profiling, type detection (numerical vs. categorical), and identifies Key Performance Indicators (KPIs).
- **`src.visualizer`**: Generates Plotly charts for the dashboard and exploration views.
- **`src.copilot`**: Connects to the Google Gemini API to interpret user queries and generate pandas code for answers.

## 🛠️ Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone <repository-url>
    cd data-viz-platform
    ```

2.  **Create a Virtual Environment**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**
    Create a `.env` file in the root directory and add your Google Gemini API key:
    ```env
    GEMINI_API_KEY=your_api_key_here
    ```

## ▶️ Usage

Run the application using Streamlit:
```bash
streamlit run app.py
```



For a detailed walkthrough of features, please refer to the [User Guide](USER_GUIDE.md).

> ✨ **Developer Note**: If you are a developer, you will love reading the [Technical Reference](TECHNICAL_REFERENCE.md) for a deep dive into the architecture and algorithms.

## Author
Built and maintained by **Muzammil**.

## Attribution
If you use or adapt this project, please give credit by linking back to this repository.

## Demo Pictures 

<img width="1920" height="1140" alt="Image" src="https://github.com/user-attachments/assets/e1d04670-a96f-4501-820f-a6a95f965f64" />

<img width="1920" height="1140" alt="Image" src="https://github.com/user-attachments/assets/f2782b3b-6e90-4aaf-9a0f-259e09c78ffc" />

<img width="1920" height="1140" alt="Image" src="https://github.com/user-attachments/assets/2abc8a7a-6699-4d49-ac4a-e9ea9b0667b6" />

<img width="1920" height="1140" alt="Image" src="https://github.com/user-attachments/assets/5bcb3bcc-dc42-4855-b9d1-f861b2c6ba23" />

<img width="1920" height="1140" alt="Image" src="https://github.com/user-attachments/assets/3d190dd9-f504-487a-944d-2f803c38b99c" />

<img width="1920" height="1140" alt="Image" src="https://github.com/user-attachments/assets/a6fc3afb-01fd-47e0-9bb0-6734142f4fa0" />



# Project Diagrams (Intelligent Data Visualization)

Below are five diagrams that explain the system architecture and flows of the Intelligent Data Visualization platform.
Paste these Mermaid blocks directly into your README.md (or another markdown file) — GitHub supports rendering Mermaid diagrams inline.

## Figure 1 — System Architecture
```mermaid
flowchart LR
  subgraph UI["Streamlit UI (app.py)"]
    A[Home / Nav / Sidebar] --> B[Data Source Page]
    A --> C[Auto Exploration Page]
    A --> D[Data Copilot Page]
    A --> E[Manual Exploration Page]
    A --> F[Dashboard Page]
  end

  subgraph Backend["Application Modules (src/)"]
    L["Loader (src.loader)"] --> P["Preprocessed Data"]
    P --> AN["Analyzer (src.analysis)"]
    AN --> KPIs["KPI Extraction"]
    AN --> Features["Feature Detection"]
    AN --> ChartPlan["Chart Selection Heuristics"]
    V["Visualizer (src.visualizer)"] --> Plotly["Plotly Charts"]
    CP["Copilot (src.copilot)"] -->|Gemini API| Gemini["Google Gemini / LLM"]
    Demo["Demo Data (src.demo_data)"]
  end

  B -->|upload CSV/Excel| L
  Demo --> P
  P --> AN
  ChartPlan --> V
  KPIs --> V
  C -->|Run Advanced Scan| AN
  D -->|Ask natural language| CP
  CP --> AN
  CP --> V
  V --> F
  Plotly --> F
  Gemini --> CP
```

## Figure 2 — Use Case Diagram
```mermaid
flowchart LR
  DA[Data Analyst]
  BU[Business User]
  AD[Admin]

  DA --- UC1["Upload Data"]
  DA --- UC2["Run Auto Exploration"]
  DA --- UC3["Manual Exploration / Custom Plots"]
  DA --- UC4["Ask Data Copilot (NL)"]

  BU --- UC5["View Dashboard & KPIs"]
  BU --- UC4

  AD --- UC6["Manage Demo / Env"]

  UC1 --> System["IDV Platform"]
  UC2 --> System
  UC3 --> System
  UC4 --> System
  UC5 --> System
  UC6 --> System
```

## Figure 3 — Class Diagram
```mermaid
classDiagram
  class App {
    +run()
    +render_pages()
    +handle_navigation()
    -session_state
  }
  class Loader {
    +load_data(file)
    +preview()
    -_read_csv()
    -_read_excel()
  }
  class Analysis {
    +get_column_types(df)
    +identify_key_metrics(df)
    +run_advanced_scan(df)
  }
  class Visualizer {
    +generate_dashboard_charts(df, col_types, kpis)
    +format_number(x)
    +create_plotly_chart(spec)
  }
  class Copilot {
    +ask_copilot(prompt, context)
    +execute_generated_code(code)
  }
  class DemoData {
    +load_demo_data(name)
  }

  App --> Loader : uses
  App --> Analysis : uses
  App --> Visualizer : uses
  App --> Copilot : uses
  App --> DemoData : loads
  Analysis --> Visualizer : provides chart_plan
  Copilot --> Analysis : requests metadata
```

## Figure 4 — Sequence Diagram
```mermaid
sequenceDiagram
  participant User
  participant StreamlitApp as App (app.py)
  participant Loader as src.loader
  participant Analysis as src.analysis
  participant Visualizer as src.visualizer
  participant Copilot as src.copilot
  participant Gemini as Google Gemini

  User->>App: Click "Upload file" / drag CSV
  App->>Loader: load_data(file)
  Loader-->>App: DataFrame (preview)
  App->>Analysis: run_advanced_scan(df)
  Analysis-->>App: col_types, kpis, chart_plan
  App->>Visualizer: generate_dashboard_charts(df, col_types, kpis)
  Visualizer-->>App: Plotly charts
  App-->>User: Render Dashboard (charts + KPIs)

  Note right of User: Data Copilot flow
  User->>App: Ask natural-language question
  App->>Copilot: ask_copilot(prompt, df_schema)
  Copilot->>Gemini: send prompt + context
  Gemini-->>Copilot: generated python/pandas code + explanation
  Copilot->>App: code + result (or code to exec)
  App->>Visualizer: render result (table/plot)
  App-->>User: Show answer & visualization
```

## Figure 5 — Activity Diagram (Auto Exploration)
```mermaid
flowchart TD
  Start([Start])
  Upload[Upload CSV / Excel]
  Preview[Preview first rows]
  CheckHeaders{Has header row?}
  Preprocess[Preprocess & Clean Data]
  DetectTypes[Detect column types]
  HasNumeric{Enough numeric columns?}
  KPISelect[Score & Select top KPIs]
  ChartGen["Generate chart plan (trend, composition, distribution)"]
  Render[Render charts + Quick Summary]
  End([End])

  Start --> Upload --> Preview --> CheckHeaders
  CheckHeaders -- Yes --> Preprocess --> DetectTypes --> HasNumeric
  CheckHeaders -- No --> Upload
  HasNumeric -- Yes --> KPISelect --> ChartGen --> Render --> End
  HasNumeric -- No --> Render --> End
```

  
  class Backend,L,AN,V,CP,Demo backend;
