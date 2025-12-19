import plotly.express as px
import pandas as pd

def format_number(num):
    if num > 1000000:
        return f"{num/1000000:.2f}M"
    if num > 1000:
        return f"{num/1000:.2f}K"
    return f"{num:.2f}"

def generate_dashboard_charts(df, col_types, kpi_cols):
    """
    Generates a list of charts for a 3-column grid.
    All charts are returned with standard compact sizing.
    """
    charts = []
    
    primary_metric = kpi_cols[0] if kpi_cols else None
    
    # helper to set common layout
    def update_layout(fig):
        fig.update_layout(
            margin=dict(t=40, l=10, r=10, b=10),
            height=250, # Compact height
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            title_font_size=14
        )
        return fig

    # 1. TREND (Line)
    if primary_metric and col_types['date']:
        date_col = col_types['date'][0]
        df_trend = df.groupby(date_col)[primary_metric].sum().reset_index()
        fig = px.line(df_trend, x=date_col, y=primary_metric, title=f"Trend: {primary_metric}")
        charts.append({"fig": update_layout(fig)})
        
    # 2. COMPOSITION (Pie)
    suitable_cat = None
    for col in col_types['categorical']:
        if 2 <= df[col].nunique() <= 8:
            suitable_cat = col
            break
    if suitable_cat and primary_metric:
        df_cat = df.groupby(suitable_cat)[primary_metric].sum().reset_index()
        fig = px.pie(df_cat, values=primary_metric, names=suitable_cat, title=f"By: {suitable_cat}", hole=0.5)
        charts.append({"fig": update_layout(fig)})
    
    # 3. RANKING (Bar)
    high_card_cat = None
    for col in col_types['categorical']:
        if df[col].nunique() > 8:
            high_card_cat = col
            break
    if not high_card_cat and not suitable_cat and col_types['categorical']:
        high_card_cat = col_types['categorical'][0]
        
    if high_card_cat and primary_metric:
        top_n = df.groupby(high_card_cat)[primary_metric].sum().nlargest(8).reset_index()
        fig = px.bar(top_n, x=primary_metric, y=high_card_cat, orientation='h', title=f"Top {high_card_cat}")
        fig.update_layout(yaxis=dict(autorange="reversed"))
        charts.append({"fig": update_layout(fig)})
        
    # 4. RELATIONSHIP (Scatter)
    if len(kpi_cols) >= 2:
        m1, m2 = kpi_cols[0], kpi_cols[1]
        fig = px.scatter(df, x=m1, y=m2, title=f"{m1} vs {m2}")
        charts.append({"fig": update_layout(fig)})
        
    # 5. DISTRIBUTION (Histogram) - Primary
    if primary_metric:
        fig = px.histogram(df, x=primary_metric, title=f"Dist: {primary_metric}")
        charts.append({"fig": update_layout(fig)})
        
    # 6. SECONDARY CATEGORY (Bar) if available
    if len(col_types['categorical']) > 1:
        sec_cat = col_types['categorical'][1]
        if sec_cat != suitable_cat and sec_cat != high_card_cat:
            top_n = df[sec_cat].value_counts().nlargest(8).reset_index()
            top_n.columns = [sec_cat, 'Count']
            fig = px.bar(top_n, x='Count', y=sec_cat, orientation='h', title=f"Count by {sec_cat}")
            fig.update_layout(yaxis=dict(autorange="reversed"))
            charts.append({"fig": update_layout(fig)})

    return charts
