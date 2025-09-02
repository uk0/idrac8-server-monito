import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # iDRAC configuration
    IDRAC_IP = os.getenv("IDRAC_IP", "10.88.51.66")
    IDRAC_USERNAME = os.getenv("IDRAC_USERNAME", "root")
    IDRAC_PASSWORD = os.getenv("IDRAC_PASSWORD", "uh-WYoKv_p8zeM!t")
    
    # API configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    
    # Monitoring configuration
    REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", "300"))  # 5 minutes in seconds
    
    # CORS configuration
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*"  # Allow all origins for development
    ]