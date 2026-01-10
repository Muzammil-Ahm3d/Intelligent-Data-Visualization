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

```mermaid
graph TD
    User(["User"]) <--> App["Streamlit App (app.py)"]
    
    subgraph "Frontend Layer"
        App
    end
    
    subgraph "Logic Layer"
        Loader[src.loader]
        Analysis[src.analysis]
        Visualizer[src.visualizer]
        Copilot[src.copilot]
    end
    
    subgraph "External Services"
        Gemini["Google Gemini API"]
    end
    
    App -->|Load Data| Loader
    App -->|Profile Data| Analysis
    App -->|Generate Charts| Visualizer
    App -->|Ask Question| Copilot
    Copilot <-->|API Call| Gemini
```

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


