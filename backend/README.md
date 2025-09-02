# iDRAC8 Hardware Monitor Backend

## Environment Variables

Create a `.env` file in the backend directory with your iDRAC credentials:

```env
# iDRAC Configuration
IDRAC_IP=10.88.51.66
IDRAC_USERNAME=root
IDRAC_PASSWORD=your_idrac_password

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Monitoring Configuration
REFRESH_INTERVAL=300
```

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your iDRAC credentials in `.env` file

3. Start the API server:
```bash
python main.py
```

## API Endpoints

- `GET /` - API health check
- `GET /api/health` - Detailed health status
- `GET /api/server/status` - Complete server hardware status
- `GET /api/server/refresh` - Manually refresh hardware data
- `GET /api/disks/physical` - Physical disks status
- `GET /api/disks/virtual` - Virtual disks and RAID status
- `GET /api/alerts` - System alerts
- `GET /api/server/info` - Basic server information

## Features

- **Automatic Monitoring**: Fetches hardware data every 5 minutes
- **Redfish API Integration**: Uses Dell's official Redfish API
- **CORS Support**: Configured for frontend integration
- **Error Handling**: Comprehensive error handling and logging
- **Caching**: Caches data to reduce iDRAC load
- **Manual Refresh**: On-demand data refresh capability

## Data Model

The API returns hardware status in a structured format compatible with the frontend:

```json
{
  "serverInfo": {
    "name": "Server Name",
    "model": "PowerEdge R720",
    "manufacturer": "Dell Inc.",
    "serialNumber": "XXXXXXX",
    "powerState": "On",
    "lastUpdated": "2024-01-01T12:00:00"
  },
  "physicalDisks": [...],
  "virtualDisks": [...],
  "alerts": [...],
  "lastRefresh": "2024-01-01T12:00:00"
}
```

## Security Notes

- Uses HTTPS for iDRAC communication
- SSL certificate verification is disabled for self-signed certificates
- Credentials are stored in environment variables
- CORS is configured for development (adjust for production)