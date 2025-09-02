# IDRAC8 Server Monitor

A comprehensive monitoring solution for Dell PowerEdge servers with IDRAC8, providing real-time hardware status monitoring including physical disks, virtual disks, RAID controllers, and system alerts.

## Architecture

- **Frontend**: React + TypeScript with Tailwind CSS and shadcn/ui components
- **Backend**: Go REST API that connects to IDRAC8 via Redfish API
- **Data Flow**: Real-time polling every 5 minutes with manual refresh capability

## Features

- Real-time monitoring of physical disk health and SMART status
- Virtual disk and RAID array status monitoring
- System alerts and event tracking
- Temperature monitoring
- Predictive failure detection
- Manual and automatic refresh capabilities

## Prerequisites

- Go 1.21 or higher
- Node.js 18 or higher
- Access to IDRAC8 interface (network connectivity)
- Valid IDRAC8 credentials

## Backend Setup

### 1. Install Dependencies

```bash
cd backend
go mod tidy
```

### 2. Configuration

Set environment variables or use defaults:

```bash
export IDRAC_HOST="10.88.51.66"      # Your IDRAC IP address
export IDRAC_USERNAME="root"          # IDRAC username
export IDRAC_PASSWORD="calvin"        # IDRAC password
export SERVER_PORT="8080"             # API server port
export POLL_INTERVAL="300000"         # Poll interval in milliseconds (5 minutes)
```

### 3. Run the Backend

```bash
go run main.go config.go
```

Or build and run:

```bash
go build -o idrac-monitor main.go config.go
./idrac-monitor
```

## Frontend Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## API Endpoints

### GET /api/v1/server/status
Returns complete server hardware status including:
- Physical disk information
- Virtual disk and RAID status
- RAID controller details
- System alerts

### GET /health
Health check endpoint

## IDRAC8 API Integration

The backend uses the Dell IDRAC8 Redfish API to retrieve hardware information:

- **Authentication**: Basic Auth with session token
- **Endpoints Used**:
  - `/redfish/v1/Systems/System.Embedded.1/Storage` - Physical disks and controllers
  - `/redfish/v1/Systems/System.Embedded.1/Storage/Volumes` - Virtual disks
  - `/redfish/v1/SessionService/Sessions` - Authentication

## Security Considerations

- TLS certificate verification is disabled for IDRAC connections (common for internal server management)
- Store IDRAC credentials securely (environment variables, secrets management)
- Use HTTPS in production
- Implement proper authentication for the web interface in production

## Troubleshooting

### Connection Issues
1. Verify IDRAC IP address and network connectivity
2. Check IDRAC credentials
3. Ensure IDRAC web interface is accessible
4. Check firewall settings

### Backend Errors
- Check logs for authentication failures
- Verify IDRAC Redfish API is enabled
- Ensure IDRAC firmware supports the used API endpoints

### Frontend Issues
- Verify backend is running on port 8080
- Check browser console for CORS or network errors
- Ensure frontend is configured to connect to correct backend URL

## Development

### Adding New Monitoring Features
1. Extend the Go structs for new data types
2. Add new IDRAC API endpoints
3. Update frontend components to display new data
4. Add appropriate error handling

### Customizing Polling Interval
Modify the `POLL_INTERVAL` environment variable or update the default in `config.go`

## Production Deployment

1. Use proper TLS certificates
2. Implement authentication and authorization
3. Set up monitoring and logging
4. Use environment-specific configuration
5. Consider using Docker containers
6. Implement health checks and monitoring