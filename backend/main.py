from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import json
import traceback
import concurrent.futures

from config import Config
from idrac_client import IDRACRedfishClient, IDRACHardwareMonitor

# Global variables for caching data
cached_hardware_data: Optional[Dict] = None
last_update_time: Optional[datetime] = None
monitoring_thread: Optional[threading.Thread] = None
is_monitoring = False
update_lock = threading.Lock()
initialization_complete = threading.Event()
initial_data_fetched = threading.Event()

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
idrac_client = None
hardware_monitor = None


def initialize_idrac_client():
    """Initialize iDRAC client with retry logic and immediate data fetch"""
    global idrac_client, hardware_monitor, cached_hardware_data, last_update_time

    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            print(f"🔌 Attempting to connect to iDRAC at {Config.IDRAC_IP} (attempt {attempt + 1}/{max_retries})")

            idrac_client = IDRACRedfishClient(
                idrac_ip=Config.IDRAC_IP,
                username=Config.IDRAC_USERNAME,
                password=Config.IDRAC_PASSWORD
            )
            hardware_monitor = IDRACHardwareMonitor(idrac_client)

            # Test connection by fetching initial data
            print("🔍 Fetching initial data...")
            test_data = hardware_monitor.get_full_hardware_status()

            if test_data and test_data.get("serverInfo"):
                print(f"✅ Successfully connected to iDRAC at {Config.IDRAC_IP}")
                print(f"📦 Server: {test_data['serverInfo'].get('name', 'Unknown')}")
                print(f"📊 Initial data: {len(test_data.get('physicalDisks', []))} physical disks, "
                      f"{len(test_data.get('virtualDisks', []))} virtual disks, "
                      f"{len(test_data.get('alerts', []))} alerts")

                # Cache initial data immediately
                with update_lock:
                    cached_hardware_data = test_data
                    last_update_time = datetime.now()

                initialization_complete.set()
                initial_data_fetched.set()
                print(f"✅ Initial data cached at {last_update_time}")
                return True
            else:
                print("⚠️ Connected but received empty data")

        except Exception as e:
            print(f"❌ Connection attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                print(f"⏳ Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("❌ All connection attempts failed")
                traceback.print_exc()

    initialization_complete.set()  # Set even if failed, to unblock waiting threads
    return False


def update_hardware_data():
    """Update hardware data from iDRAC with thread safety"""
    global cached_hardware_data, last_update_time

    if not hardware_monitor:
        print("❌ Hardware monitor not available")
        return False

    with update_lock:
        try:
            print(f"🔄 Fetching hardware data from iDRAC {Config.IDRAC_IP}...")
            start_time = time.time()

            data = hardware_monitor.get_full_hardware_status()

            if data and data.get("serverInfo"):
                cached_hardware_data = data
                last_update_time = datetime.now()

                fetch_time = round(time.time() - start_time, 2)
                print(f"✅ Hardware data updated at {last_update_time} (took {fetch_time}s)")

                # Log summary
                physical_count = len(data.get("physicalDisks", []))
                virtual_count = len(data.get("virtualDisks", []))
                alert_count = len(data.get("alerts", []))
                print(
                    f"📊 Summary: {physical_count} physical disks, {virtual_count} virtual disks, {alert_count} alerts")

                return True
            else:
                print("⚠️ Received empty or invalid data from iDRAC")
                return False

        except Exception as e:
            print(f"❌ Failed to update hardware data: {str(e)}")
            traceback.print_exc()
            return False


def monitoring_worker():
    """Background worker for periodic hardware monitoring"""
    global is_monitoring, cached_hardware_data

    print(f"🚀 Starting hardware monitoring (interval: {Config.REFRESH_INTERVAL}s)")

    # Wait for initial data to be fetched
    print("⏳ Waiting for initial data fetch...")
    initial_data_fetched.wait(timeout=120)  # Wait max 2 minutes

    if not cached_hardware_data:
        print("⚠️ No initial data available, attempting first fetch...")
        update_hardware_data()

    consecutive_failures = 0
    max_consecutive_failures = 5

    while is_monitoring:
        try:
            time.sleep(Config.REFRESH_INTERVAL)

            if is_monitoring:  # Check again in case we were stopped
                success = update_hardware_data()

                if success:
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                    if consecutive_failures >= max_consecutive_failures:
                        print(f"⚠️ {consecutive_failures} consecutive failures. Attempting to reconnect...")
                        initialize_idrac_client()
                        consecutive_failures = 0

        except Exception as e:
            print(f"❌ Monitoring worker error: {str(e)}")
            time.sleep(30)  # Wait 30 seconds before retrying


@app.on_event("startup")
async def startup_event():
    """Start background monitoring on app startup"""
    global monitoring_thread, is_monitoring

    print("🎯 Starting up iDRAC Hardware Monitor API...")

    # Initialize iDRAC client and fetch initial data in background
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
    executor.submit(initialize_idrac_client)

    # Start monitoring thread
    is_monitoring = True
    monitoring_thread = threading.Thread(target=monitoring_worker, daemon=True)
    monitoring_thread.start()
    print("🎯 Background monitoring thread started")


@app.on_event("shutdown")
async def shutdown_event():
    """Stop background monitoring on app shutdown"""
    global is_monitoring
    is_monitoring = False
    print("🛑 Background monitoring stopped")


@app.get("/")
async def root():
    """Health check endpoint"""
    is_ready = initialization_complete.is_set()
    has_data = cached_hardware_data is not None

    return {
        "message": "iDRAC8 Hardware Monitor API",
        "version": "1.0.0",
        "status": "ready" if (is_ready and has_data) else "initializing",
        "idrac_ip": Config.IDRAC_IP,
        "last_update": last_update_time.isoformat() if last_update_time else None,
        "cache_available": has_data
    }


@app.get("/api/health")
async def health_check():
    """API health check with detailed status"""
    cache_age = None
    if last_update_time:
        cache_age = (datetime.now() - last_update_time).total_seconds()

    is_ready = initialization_complete.is_set()
    has_data = cached_hardware_data is not None

    return {
        "status": "healthy" if (is_ready and has_data) else "degraded",
        "idrac_connected": is_ready,
        "last_update": last_update_time.isoformat() if last_update_time else None,
        "cache_status": "available" if has_data else "empty",
        "cache_age_seconds": cache_age,
        "refresh_interval": Config.REFRESH_INTERVAL,
        "initialization_complete": is_ready
    }


@app.get("/api/server/status")
async def get_server_status():
    """Get complete server hardware status from cache"""
    # Wait for initialization to complete (max 10 seconds)
    if not initialization_complete.wait(timeout=10):
        return JSONResponse(
            status_code=202,
            content={
                "message": "System still initializing, please retry in a few seconds",
                "status": "initializing"
            }
        )

    if not cached_hardware_data:
        # Try one manual update
        print("📡 No cached data available, attempting manual fetch...")
        success = update_hardware_data()

        if not success or not cached_hardware_data:
            # Return empty structure instead of error
            return JSONResponse(content={
                "serverInfo": {},
                "physicalDisks": [],
                "virtualDisks": [],
                "alerts": [],
                "lastRefresh": datetime.now().isoformat(),
                "_metadata": {
                    "error": "Unable to fetch data from iDRAC",
                    "status": "unavailable"
                }
            })

    # Check cache age and warn if stale
    cache_age_warning = None
    if last_update_time:
        cache_age = (datetime.now() - last_update_time).total_seconds()
        if cache_age > Config.REFRESH_INTERVAL * 3:  # If cache is 3x older than refresh interval
            cache_age_warning = f"Cache is {int(cache_age)} seconds old"

    response_data = {
        **cached_hardware_data,
        "_metadata": {
            "cached_at": last_update_time.isoformat() if last_update_time else None,
            "cache_age_warning": cache_age_warning
        }
    }

    return JSONResponse(content=response_data)


@app.get("/api/server/refresh")
async def refresh_server_data():
    """Manually trigger a refresh of server data"""
    # Wait for initialization
    if not initialization_complete.wait(timeout=5):
        raise HTTPException(
            status_code=503,
            detail="System still initializing"
        )

    if not hardware_monitor:
        raise HTTPException(
            status_code=503,
            detail="iDRAC client not available"
        )

    # Perform synchronous update in background
    def do_refresh():
        return update_hardware_data()

    # Run in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    success = await loop.run_in_executor(None, do_refresh)

    if success and cached_hardware_data:
        return {
            "message": "Hardware data refreshed successfully",
            "timestamp": last_update_time.isoformat() if last_update_time else None,
            "data": cached_hardware_data
        }
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to refresh hardware data from iDRAC"
        )


@app.get("/api/disks/physical")
async def get_physical_disks():
    """Get physical disks status from cache"""
    # Wait for initialization
    initialization_complete.wait(timeout=5)

    if not cached_hardware_data:
        return JSONResponse(content={
            "disks": [],
            "count": 0,
            "cached_at": None,
            "status": "no_data"
        })

    disks = cached_hardware_data.get("physicalDisks", [])
    return JSONResponse(content={
        "disks": disks,
        "count": len(disks),
        "cached_at": last_update_time.isoformat() if last_update_time else None
    })


@app.get("/api/disks/virtual")
async def get_virtual_disks():
    """Get virtual disks and RAID status from cache"""
    # Wait for initialization
    initialization_complete.wait(timeout=5)

    if not cached_hardware_data:
        return JSONResponse(content={
            "disks": [],
            "count": 0,
            "cached_at": None,
            "status": "no_data"
        })

    disks = cached_hardware_data.get("virtualDisks", [])
    return JSONResponse(content={
        "disks": disks,
        "count": len(disks),
        "cached_at": last_update_time.isoformat() if last_update_time else None
    })


@app.get("/api/alerts")
async def get_alerts():
    """Get system alerts from cache"""
    # Wait for initialization
    initialization_complete.wait(timeout=5)

    if not cached_hardware_data:
        return JSONResponse(content={
            "alerts": [],
            "count": 0,
            "cached_at": None,
            "status": "no_data"
        })

    alerts = cached_hardware_data.get("alerts", [])
    return JSONResponse(content={
        "alerts": alerts,
        "count": len(alerts),
        "cached_at": last_update_time.isoformat() if last_update_time else None
    })


@app.get("/api/server/info")
async def get_server_info():
    """Get basic server information from cache"""
    # Wait for initialization
    initialization_complete.wait(timeout=5)

    if not cached_hardware_data:
        return JSONResponse(content={
            "serverInfo": {},
            "cached_at": None,
            "status": "no_data"
        })

    info = cached_hardware_data.get("serverInfo", {})
    return JSONResponse(content={
        **info,
        "cached_at": last_update_time.isoformat() if last_update_time else None
    })


@app.get("/api/cache/stats")
async def get_cache_stats():
    """Get cache statistics"""
    cache_size = 0
    if cached_hardware_data:
        cache_size = len(json.dumps(cached_hardware_data))

    cache_age = None
    if last_update_time:
        cache_age = (datetime.now() - last_update_time).total_seconds()

    return {
        "cache_available": cached_hardware_data is not None,
        "cache_size_bytes": cache_size,
        "last_update": last_update_time.isoformat() if last_update_time else None,
        "cache_age_seconds": cache_age,
        "refresh_interval": Config.REFRESH_INTERVAL,
        "is_monitoring": is_monitoring,
        "initialization_complete": initialization_complete.is_set(),
        "physical_disks_count": len(cached_hardware_data.get("physicalDisks", [])) if cached_hardware_data else 0,
        "virtual_disks_count": len(cached_hardware_data.get("virtualDisks", [])) if cached_hardware_data else 0,
        "alerts_count": len(cached_hardware_data.get("alerts", [])) if cached_hardware_data else 0
    }


if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print(f"🚀 Starting iDRAC8 Hardware Monitor API")
    print(f"📡 Target iDRAC: {Config.IDRAC_IP}")
    print(f"🌐 API Server: {Config.API_HOST}:{Config.API_PORT}")
    print(f"⏱️  Refresh interval: {Config.REFRESH_INTERVAL} seconds")
    print("=" * 60)

    uvicorn.run(
        "main:app",
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=False,  # Set to False for production
        log_level="info"
    )