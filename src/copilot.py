
import os
import io
import pandas as pd
import time
import random
from dotenv import load_dotenv
from google import genai

# Load environment variables (API Key)
load_dotenv()

def get_api_client():
    """Initializes the Gemini API client."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    try:
        # Initialize the client with the API key
        client = genai.Client(api_key=api_key)
        return client
    except Exception as e:
        print(f"Error initializing Gemini client: {e}")
        return None

def prepare_context(df: pd.DataFrame) -> str:
    """
    Prepares a context string summarizing the dataframe.
    Includes columns, simple stats, and a sample.
    """
    if df is None or df.empty:
        return "No data available."
    
    buffer = io.StringIO()
    
    buffer.write(f"Dataset Shape: {df.shape}\n\n")
    
    buffer.write("Columns and Data Types:\n")
    for col, dtype in df.dtypes.items():
        buffer.write(f"- {col}: {dtype}\n")
    buffer.write("\n")
    
    buffer.write("Missing Values:\n")
    missing = df.isnull().sum()
    if missing.sum() == 0:
        buffer.write("None\n")
    else:
        for col, count in missing[missing > 0].items():
            buffer.write(f"- {col}: {count} missing\n")
    buffer.write("\n")
    
    buffer.write("Summary Statistics (Numerical):\n")
    try:
        desc = df.describe().to_markdown()
        buffer.write(desc)
    except Exception as e:
        buffer.write(f"Could not generate stats: {e}")
        try:
             buffer.write(df.describe().to_string())
        except:
             pass
    buffer.write("\n\n")
    
    buffer.write("First 3 Rows (Sample):\n")
    try:
        sample = df.head(3).to_markdown(index=False)
        buffer.write(sample)
    except:
        buffer.write("Could not generate sample.")
        
    return buffer.getvalue()

def execute_generated_code(code: str, df: pd.DataFrame) -> str:
    """
    Executes the generated pandas code safely.
    """
    try:
        # Create a local safe scope
        local_scope = {"df": df, "pd": pd, "result": None}
        
        # Execute the code
        exec(code, {}, local_scope)
        
        # Get the result
        result = local_scope.get("result")
        if result is None:
            return "The code ran but did not yield a 'result' variable."
            
        return str(result)
    except Exception as e:
        return f"Error executing code: {e}"

def clean_code_block(text: str) -> str:
    """Extracts code from markdown code blocks."""
    if "```python" in text:
        return text.split("```python")[1].split("```")[0].strip()
    elif "```" in text:
        return text.split("```")[1].split("```")[0].strip()
    return text.strip()

def ask_copilot(df: pd.DataFrame, user_query: str) -> dict:
    """
    Analyzes the user query and dataset to generate an answer.
    Returns specific structure:
    {
        "type": "code" | "text",
        "content": str, # The final answer text
        "code": str     # The generated code (optional)
    }
    """
    client = get_api_client()
    if not client:
        return {"type": "text", "content": "⚠️ Gemini API Key not found. Please set GEMINI_API_KEY in .env file."}
    
    # Context now focuses on structure rather than content
    dtypes_summary = str(df.dtypes)
    columns = list(df.columns)
    
    prompt = f"""
    You are an expert Python Data Analyst.
    
    Dataset Columns: {columns}
    Data Types:
    {dtypes_summary}
    
    User Query: "{user_query}"
    
    INSTRUCTIONS:
    1. If the user asks a general question (e.g., "Hello", "How are you?"), answer normally.
    2. If the user asks ANY question about the data, even if you can't see the rows, YOU MUST GENERATE PYTHON CODE to answer it.
       - Do NOT complain that you can't see the data.
       - Do NOT output "I cannot answer".
       - Write a Pandas script that assumes 'df' is loaded.
       - Store the result in a variable named 'result'.
       - Wrap the code in a ```python block.
    
    Example for "Highest temperature in Asia":
    ```python
    result = df[df['Region'] == 'Asia']['Temperature'].max()
    ```
    """
    
    max_retries = 3
    base_delay = 1
    
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            raw_text = response.text
            print(f"DEBUG: Copilot Response: {raw_text}")
            
            # Check if code was generated
            if "```python" in raw_text or "```" in raw_text:
                code = clean_code_block(raw_text)
                execution_result = execute_generated_code(code, df)
                return {
                    "type": "code",
                    "content": execution_result,
                    "code": code
                }
            else:
                return {
                    "type": "text",
                    "content": raw_text
                }
                
        except Exception as e:
            if "503" in str(e) or "429" in str(e): # Service Unavailable or Rate Limit
                if attempt < max_retries - 1:
                    sleep_time = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(sleep_time)
                    continue
            return {"type": "text", "content": f"Error connecting to Gemini API (Attempt {attempt+1}/{max_retries}): {str(e)}"}
    
    return {"type": "text", "content": "Error: Failed to connect to Gemini API after multiple attempts."}
