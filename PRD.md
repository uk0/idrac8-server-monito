# IDRAC8 Server Hardware Monitor

Real-time monitoring solution for Dell PowerEdge servers with IDRAC8, providing comprehensive hardware status monitoring through direct IDRAC API integration with automatic polling and predictive failure detection.

**Experience Qualities**:
1. **Reliable** - Direct API integration with IDRAC8 ensures accurate real-time hardware status
2. **Professional** - Enterprise-grade interface designed for system administrators and datacenter operations
3. **Efficient** - Automated monitoring with intelligent alerting reduces manual checks and prevents downtime

**Complexity Level**: Complex Application (advanced functionality, real-time API integration)
- Features comprehensive IDRAC8 API integration, real-time hardware monitoring, automated polling, alert management, and historical data tracking with backend service architecture

## Technical Architecture

### Backend Service (Go)
- **Functionality**: RESTful API service that communicates directly with IDRAC8 via Redfish API
- **Purpose**: Provides secure, reliable interface between frontend and IDRAC8 hardware
- **Integration**: Direct IDRAC8 Redfish API calls for real-time hardware data
- **Features**: Session management, error handling, data transformation, health checks

### Frontend Application (React)
- **Functionality**: Real-time dashboard displaying hardware status and alerts
- **Purpose**: Provides intuitive interface for monitoring and managing server hardware
- **Integration**: Consumes backend API for live hardware data
- **Features**: Auto-refresh, manual refresh, alert management, responsive design

## Essential Features

### Direct IDRAC8 API Integration
- **Functionality**: Connects to IDRAC8 at 10.88.51.66 using Redfish API for real-time hardware data
- **Purpose**: Provides authentic, live hardware status without simulation or mock data
- **Trigger**: Automatic connection on service startup with authenticated sessions
- **Progression**: Service starts → IDRAC authentication → API endpoint discovery → Data polling begins → Frontend receives real data
- **Success criteria**: Successfully authenticate and retrieve live hardware data from IDRAC8

### Real-time Hardware Status Display
- **Functionality**: Shows current status of all physical disks, RAID arrays, and virtual disks from actual IDRAC data
- **Purpose**: Provides immediate visibility into actual hardware health to prevent data loss
- **Trigger**: Automatic page load and 5-minute refresh intervals
- **Progression**: Dashboard loads → Backend API called → IDRAC queried → Hardware data returned → Status cards populate → Health indicators display
- **Success criteria**: All hardware components show live status with accurate health indicators from IDRAC8

### Automated Health Monitoring with IDRAC Polling
- **Functionality**: Continuously polls IDRAC8 every 5 minutes for hardware health parameters
- **Purpose**: Proactive identification of failing hardware through direct IDRAC SMART data and sensor readings
- **Trigger**: Automated 5-minute polling cycle managed by Go backend service
- **Progression**: Timer triggers → IDRAC API called → Hardware data retrieved → Status comparison → Database updated → Frontend notified
- **Success criteria**: System accurately detects and reports actual hardware issues from IDRAC within monitoring window

### Enterprise Alert Management System
- **Functionality**: Generates alerts based on actual IDRAC hardware status and event logs
- **Purpose**: Ensures immediate awareness of real hardware issues requiring attention
- **Trigger**: IDRAC hardware status change detection or manual alert review
- **Progression**: IDRAC issue detected → Backend processes change → Alert generated → Database stored → Frontend displays notification
- **Success criteria**: All critical hardware issues from IDRAC generate immediate visible alerts with actionable information

### Predictive Failure Analysis from SMART Data
- **Functionality**: Analyzes actual SMART data and IDRAC sensor readings to recommend proactive replacements
- **Purpose**: Prevent unexpected hardware failures through real predictive maintenance data
- **Trigger**: SMART parameter threshold breach or temperature anomaly detection from IDRAC
- **Progression**: IDRAC SMART data analyzed → Risk assessment calculated → Recommendation generated → Timeline provided → Maintenance scheduled
- **Success criteria**: System accurately identifies disks requiring replacement before failure using real IDRAC data

## Edge Case Handling

- **IDRAC Connection Failures**: Display cached data with clear offline indicators, automatic retry logic, and manual reconnection options
- **IDRAC Authentication Issues**: Graceful handling of credential failures with secure retry mechanisms and admin notifications
- **Partial IDRAC Data**: Show available hardware information while clearly marking inaccessible components or sensors
- **IDRAC API Timeouts**: Implement timeout handling with exponential backoff and fallback to last known status
- **Network Connectivity Issues**: Detect network problems and provide clear status indicators with automatic recovery
- **IDRAC Firmware Compatibility**: Handle different IDRAC API versions and provide compatibility warnings
- **Concurrent Access**: Manage multiple user sessions without overwhelming IDRAC with requests
- **Hardware Events During Polling**: Handle rapid hardware state changes without UI flickering or data inconsistency

## Implementation Considerations

### Security & Authentication
- **IDRAC Credentials**: Secure storage and transmission of IDRAC login credentials
- **Session Management**: Proper IDRAC session handling with automatic renewal
- **Network Security**: TLS configuration for IDRAC communication
- **Access Control**: Authentication for web interface access in production

### Performance & Scalability
- **API Efficiency**: Optimized IDRAC API calls to minimize server load
- **Caching Strategy**: Intelligent caching of IDRAC data with appropriate TTL
- **Error Recovery**: Robust error handling and automatic recovery mechanisms
- **Resource Management**: Efficient memory and connection management for long-running service

### Deployment & Configuration
- **Environment Variables**: Configurable IDRAC connection parameters
- **Docker Support**: Containerized deployment with docker-compose
- **Health Monitoring**: Service health checks and monitoring endpoints
- **Logging**: Comprehensive logging for troubleshooting and audit

## Design Direction

The design should feel authoritative and mission-critical, similar to professional server management interfaces, with a clean, data-dense layout that prioritizes information hierarchy and immediate problem identification over visual flourishes.

## Color Selection

Triadic (three equally spaced colors) - Using enterprise monitoring standards with red for critical alerts, amber for warnings, and green for healthy status, creating immediate visual comprehension of system state.

- **Primary Color**: Deep Navy Blue (oklch(0.25 0.08 250)) - Communicates stability and professional authority
- **Secondary Colors**: Slate Gray (oklch(0.45 0.02 250)) for supporting elements, Light Gray (oklch(0.95 0.01 250)) for backgrounds
- **Accent Color**: Critical Red (oklch(0.55 0.22 25)) for immediate attention on hardware failures and urgent alerts
- **Foreground/Background Pairings**: 
  - Background (Light Gray oklch(0.98 0.01 250)): Dark Navy text (oklch(0.15 0.08 250)) - Ratio 12.8:1 ✓
  - Card (White oklch(1 0 0)): Dark Navy text (oklch(0.15 0.08 250)) - Ratio 14.2:1 ✓
  - Primary (Deep Navy oklch(0.25 0.08 250)): White text (oklch(1 0 0)) - Ratio 8.9:1 ✓
  - Accent (Critical Red oklch(0.55 0.22 25)): White text (oklch(1 0 0)) - Ratio 4.7:1 ✓

## Font Selection

Typefaces should convey technical precision and readability under stress, using monospace for data values and clean sans-serif for interface elements.

- **Typographic Hierarchy**:
  - H1 (Dashboard Title): Inter Bold/32px/tight letter spacing
  - H2 (Section Headers): Inter Semibold/24px/normal spacing  
  - H3 (Component Labels): Inter Medium/18px/normal spacing
  - Body (Status Text): Inter Regular/16px/relaxed spacing
  - Data (Metrics): JetBrains Mono Regular/14px/tabular spacing
  - Alert Text: Inter Medium/16px/normal spacing

## Animations

Animations should be minimal and functional, primarily serving to draw attention to critical status changes and smooth data transitions during refresh cycles without causing distraction during emergency situations.

- **Purposeful Meaning**: Subtle pulsing for critical alerts, smooth fade transitions for data updates, and gentle loading states that maintain professional atmosphere
- **Hierarchy of Movement**: Critical alerts receive priority animation focus, followed by status changes, with background refresh animations being nearly imperceptible

## Component Selection

- **Components**: Card for hardware component grouping, Badge for status indicators, Alert for system notifications, Table for detailed metrics, Progress for health percentages, Button for manual actions, Tabs for different hardware views
- **Customizations**: Custom status indicator components with color-coded health states, specialized metric display cards with trend indicators
- **States**: Status badges with distinct visual states (healthy/warning/critical), buttons with clear enabled/disabled states for maintenance actions, interactive cards with hover details
- **Icon Selection**: Server, HardDrive, AlertTriangle, CheckCircle, XCircle, RefreshCcw, Settings icons for clear hardware representation
- **Spacing**: Consistent 4-unit (16px) padding for cards, 2-unit (8px) margins between related elements, 6-unit (24px) section separation
- **Mobile**: Responsive card layout with collapsible details, simplified metric display, touch-friendly action buttons, maintains critical alert visibility