
try:
    import dotenv
    print("dotenv imported successfully")
except ImportError as e:
    print(f"dotenv failed: {e}")

try:
    import google.genai
    print("google.genai imported successfully")
except ImportError as e:
    print(f"google.genai failed: {e}")
