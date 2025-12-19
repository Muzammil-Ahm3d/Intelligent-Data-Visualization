import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

def get_column_types(df):
    """
    Detects numerical, categorical, and date columns.
    """
    numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    date_cols = []
    
    # Heuristic for dates
    for col in categorical_cols:
        try:
            pd.to_datetime(df[col], errors='raise')
            date_cols.append(col)
        except:
            pass
            
    # Remove date columns from categorical
    categorical_cols = [c for c in categorical_cols if c not in date_cols]
    
    return {
        "numerical": numerical_cols,
        "categorical": categorical_cols,
        "date": date_cols
    }

def identify_key_metrics(df, col_types):
    """
    Identifies 3 important columns to show as KPIs.
    Prioritizes columns with names like 'Sales', 'Profit', 'Revenue'.
    """
    candidates = col_types['numerical']
    priority_keywords = ['sales', 'revenue', 'profit', 'amount', 'cost', 'price', 'total']
    
    # Score candidates
    scored = []
    for col in candidates:
        score = 0
        if any(k in col.lower() for k in priority_keywords):
            score += 2
        if df[col].nunique() > 10: # Likely continuous, not ID
            score += 1
        scored.append((col, score))
        
    scored.sort(key=lambda x: x[1], reverse=True)
    return [x[0] for x in scored[:3]]

def calculate_correlations(df):
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.empty:
        return None
    return numeric_df.corr()

def analyze_dependencies(df, target_col):
    try:
        df_clean = df.copy().dropna()
        X = df_clean.drop(columns=[target_col])
        y = df_clean[target_col]
        
        for col in X.select_dtypes(include=['object']).columns:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            
        if pd.api.types.is_numeric_dtype(y) and len(y.unique()) > 10:
            model = RandomForestRegressor(n_estimators=50, random_state=42)
        else:
            if not pd.api.types.is_numeric_dtype(y):
                le = LabelEncoder()
                y = le.fit_transform(y.astype(str))
            model = RandomForestClassifier(n_estimators=50, random_state=42)
            
        model.fit(X, y)
        importances = model.feature_importances_
        feature_imp = pd.DataFrame({'Feature': X.columns, 'Importance': importances})
        return feature_imp.sort_values(by='Importance', ascending=False)
    except:
        return None

def generate_summary_text(df, col_types):
    num_cols = len(col_types['numerical'])
    cat_cols = len(col_types['categorical'])
    nrows, ncols = df.shape
    return f"Dataset: **{nrows} rows**, **{ncols} columns** ({num_cols} Num, {cat_cols} Cat)."
