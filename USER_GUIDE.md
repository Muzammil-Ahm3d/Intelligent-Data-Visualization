# User Guide: Intelligent Data Visualization Platform

This guide will walk you through the comprehensive features of the Intelligent Data Visualization Platform.

## Table of Contents
1. [Getting Started](#getting-started)
2. [Data Source](#data-source)
3. [Auto Exploration](#auto-exploration)
4. [Data Copilot](#data-copilot)
5. [Manual Exploration](#manual-exploration)
6. [Dashboard](#dashboard)

---

## 1. Getting Started
When you launch the app, you will land on the **Home** page. This provides a quick overview of the application's capabilities. Use the sidebar on the left to navigate between different sections.

## 2. Data Source
**Purpose**: The foundation of your analysis.
- Navigate to the **Data Source** page.
- Drag and drop your **CSV** or **Excel** file into the upload area.
- The app will preview your data (first 5 rows).
- **Note**: Ensure your data has a header row. If the file is successfully loaded, you will see a success message and can proceed to other tabs.

## 3. Auto Exploration
**Purpose**: Get instant insights without manual effort.
- Click on **Auto Exploration** in the sidebar.
- Click the green **"Run Advanced Scan"** button.
- The system will analyze your dataset to:
    - Identify column types (Numerical, Categorical, Dates).
    - Select relevant Key Performance Indicators (KPIs).
    - Generate a "Quick Summary" describing the dataset structure.
    - Create a suite of charts including Trends, Compositions, and Distributions.

## 4. Data Copilot 🤖
**Purpose**: Ask questions in plain English.
- Navigate to **Data Copilot**.
- Type your question in the chat input at the bottom.
- **Examples**:
    - *"What is the total sales amount?"*
    - *"Show me the top 5 cities by revenue."*
    - *"Is there a correlation between price and quantity?"*
- The Copilot will generate Python code to answer your question and display the result (text or code output).

## 5. Manual Exploration
**Purpose**: Create custom 2D visualizations.
- Go to **Manual Exploration**.
- Use the dropdowns to select:
    - **X-Axis**: A column for the horizontal axis.
    - **Y-Axis**: A column for the vertical axis.
- The chart will update automatically. This is perfect for spotting outliers or verifying specific hypotheses.

## 6. Dashboard
**Purpose**: A unified view with global filters.
- The **Dashboard** page aggregates the most important charts generated during exploration.
- **Sidebar Filters**:
    - If your data has suitable categorical columns (e.g., Region, Category), filters will appear in the sidebar.
    - Adjusting these filters updates **all** charts on the dashboard instantaneously.

---

### Tips for Best Results
- **Clean Data**: Ensure there are no merged cells in your Excel files and that the first row contains clear column headers.
- **Date Columns**: Use standard date formats (YYYY-MM-DD) for best trend analysis detection.
