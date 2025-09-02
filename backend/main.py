from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import threading
import time
from datetime import datetime
from typing import Dict, Optional

from config import Config
from idrac_client import IDRACRedfishClient, IDRACHardwareMonitor

# Global variables for caching data
cached_hardware_data: Optional[Dict] = None
last_update_time: Optional[datetime] = None
monitoring_thread: Optional[threading.Thread] = None
is_monitoring = False

# Initialize FastAPI app
app = FastAPI(
    title="iDRAC8 Hardware Monitor API",
    description="RESTful API for monitoring Dell server hardware via iDRAC8 Redfish interface",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize iDRAC client and monitor
try:
    idrac_client = IDRACRedfishClient(
        idrac_ip=Config.IDRAC_IP,
        username=Config.IDRAC_USERNAME,
        password=Config.IDRAC_PASSWORD
    )
    hardware_monitor = IDRACHardwareMonitor(idrac_client)
    print(f"✅ iDRAC client initialized for {Config.IDRAC_IP}")
except Exception as e:
    print(f"❌ Failed to initialize iDRAC client: {str(e)}")
    idrac_client = None
    hardware_monitor = None

def update_hardware_data():
    """Update hardware data from iDRAC"""
    global cached_hardware_data, last_update_time
    
    if not hardware_monitor:
        print("❌ Hardware monitor not available")
        return
    
    try:
        print(f"🔄 Fetching hardware data from iDRAC {Config.IDRAC_IP}...")
        data = hardware_monitor.get_full_hardware_status()
        cached_hardware_data = data
        last_update_time = datetime.now()
        print(f"✅ Hardware data updated at {last_update_time}")
        
        # Log summary
        if data:
            physical_count = len(data.get("physicalDisks", []))
            virtual_count = len(data.get("virtualDisks", []))
            alert_count = len(data.get("alerts", []))
            print(f"📊 Data summary: {physical_count} physical disks, {virtual_count} virtual disks, {alert_count} alerts")
            
    except Exception as e:
        print(f"❌ Failed to update hardware data: {str(e)}")

def monitoring_worker():
    """Background worker for periodic hardware monitoring"""
    global is_monitoring
    
    print(f"🚀 Starting hardware monitoring (interval: {Config.REFRESH_INTERVAL}s)")
    
    # Initial data fetch
    update_hardware_data()
    
    while is_monitoring:
        try:
            time.sleep(Config.REFRESH_INTERVAL)
            if is_monitoring:  # Check again in case we were stopped
                update_hardware_data()
        except Exception as e:
            print(f"❌ Monitoring worker error: {str(e)}")
            time.sleep(30)  # Wait 30 seconds before retrying

@app.on_event("startup")
async def startup_event():
    """Start background monitoring on app startup"""
    global monitoring_thread, is_monitoring
    
    if hardware_monitor:
        is_monitoring = True
        monitoring_thread = threading.Thread(target=monitoring_worker, daemon=True)
        monitoring_thread.start()
        print("🎯 Background monitoring started")
    else:
        print("⚠️ Background monitoring disabled - iDRAC client not available")

@app.on_event("shutdown")
async def shutdown_event():
    """Stop background monitoring on app shutdown"""
    global is_monitoring
    is_monitoring = False
    print("🛑 Background monitoring stopped")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "iDRAC8 Hardware Monitor API",
        "version": "1.0.0",
        "status": "running",
        "idrac_ip": Config.IDRAC_IP,
        "last_update": last_update_time.isoformat() if last_update_time else None
    }

@app.get("/api/health")
async def health_check():
    """API health check"""
    if not hardware_monitor:
        raise HTTPException(status_code=503, detail="iDRAC client not available")
    
    return {
        "status": "healthy",
        "idrac_connected": True,
        "last_update": last_update_time.isoformat() if last_update_time else None,
        "cache_status": "available" if cached_hardware_data else "empty"
    }

@app.get("/api/server/status")
async def get_server_status():
    """Get complete server hardware status"""
    if not hardware_monitor:
        raise HTTPException(status_code=503, detail="iDRAC client not available")
    
    if not cached_hardware_data:
        # If no cached data, fetch immediately
        update_hardware_data()
        
        if not cached_hardware_data:
            raise HTTPException(status_code=503, detail="Failed to fetch hardware data from iDRAC")
    
    return JSONResponse(content=cached_hardware_data)

@app.get("/api/server/refresh")
async def refresh_server_data():
    """Manually refresh server data"""
    if not hardware_monitor:
        raise HTTPException(status_code=503, detail="iDRAC client not available")
    
    try:
        update_hardware_data()
        if not cached_hardware_data:
            raise HTTPException(status_code=503, detail="Failed to refresh hardware data")
        
        return {
            "message": "Hardware data refreshed successfully",
            "timestamp": last_update_time.isoformat(),
            "data": cached_hardware_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refresh failed: {str(e)}")

@app.get("/api/disks/physical")
async def get_physical_disks():
    """Get physical disks status"""
    if not cached_hardware_data:
        raise HTTPException(status_code=503, detail="No hardware data available")
    
    return JSONResponse(content=cached_hardware_data.get("physicalDisks", []))

@app.get("/api/disks/virtual")
async def get_virtual_disks():
    """Get virtual disks and RAID status"""
    if not cached_hardware_data:
        raise HTTPException(status_code=503, detail="No hardware data available")
    
    return JSONResponse(content=cached_hardware_data.get("virtualDisks", []))

@app.get("/api/alerts")
async def get_alerts():
    """Get system alerts"""
    if not cached_hardware_data:
        raise HTTPException(status_code=503, detail="No hardware data available")
    
    return JSONResponse(content=cached_hardware_data.get("alerts", []))

@app.get("/api/server/info")
async def get_server_info():
    """Get basic server information"""
    if not cached_hardware_data:
        raise HTTPException(status_code=503, detail="No hardware data available")
    
    return JSONResponse(content=cached_hardware_data.get("serverInfo", {}))

if __name__ == "__main__":
    import uvicorn
    print(f"🚀 Starting iDRAC8 Hardware Monitor API on {Config.API_HOST}:{Config.API_PORT}")
    print(f"📡 Monitoring iDRAC at {Config.IDRAC_IP}")
    print(f"⏱️ Refresh interval: {Config.REFRESH_INTERVAL} seconds")
    
    uvicorn.run(
        "main:app",
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=True,
        log_level="info"
    )