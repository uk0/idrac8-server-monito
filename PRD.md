# IDRAC8 Server Hardware Monitor

Monitor physical disk health, RAID configuration, and virtual disk status for Dell IDRAC8 servers with real-time alerts and automated health checks.

**Experience Qualities**:
1. **Reliable** - Critical system monitoring requires unwavering accuracy and immediate alert visibility
2. **Professional** - Enterprise-grade interface that instills confidence in system administrators
3. **Efficient** - Streamlined workflows that enable quick assessment and decision-making during critical situations

**Complexity Level**: Light Application (multiple features with basic state)
- Displays real-time hardware status with automated refresh cycles, basic alerting system, and data persistence for historical tracking

## Essential Features

### Real-time Hardware Status Display
- **Functionality**: Shows current status of all physical disks, RAID arrays, and virtual disks
- **Purpose**: Provides immediate visibility into hardware health to prevent data loss
- **Trigger**: Automatic page load and 5-minute refresh intervals
- **Progression**: Dashboard loads → Hardware data fetches → Status cards populate → Health indicators display → Alerts highlight issues
- **Success criteria**: All hardware components show current status with clear health indicators

### Automated Health Monitoring
- **Functionality**: Continuously monitors disk health parameters and RAID status
- **Purpose**: Proactive identification of failing hardware before critical failure
- **Trigger**: Automated 5-minute polling cycle
- **Progression**: Timer triggers → API call executes → Data comparison occurs → Status updates → Alerts generate if needed
- **Success criteria**: System accurately detects and reports hardware issues within monitoring window

### Alert Management System
- **Functionality**: Displays critical, warning, and informational alerts with timestamp tracking
- **Purpose**: Ensures immediate awareness of hardware issues requiring attention
- **Trigger**: Hardware status change detection or manual alert review
- **Progression**: Issue detected → Alert generated → Dashboard notification → Admin review → Action taken or acknowledged
- **Success criteria**: All critical issues generate immediate visible alerts with clear action guidance

### Hardware Replacement Recommendations
- **Functionality**: Analyzes disk health metrics to recommend proactive replacements
- **Purpose**: Prevent unexpected hardware failures through predictive maintenance
- **Trigger**: Health parameter threshold breach or manual health assessment
- **Progression**: Health metrics analyzed → Risk assessment calculated → Recommendation generated → Timeline provided → Action plan suggested
- **Success criteria**: System accurately identifies disks requiring replacement before failure occurs

## Edge Case Handling

- **Connection Failures**: Display cached data with clear offline indicators and retry mechanisms
- **Partial Data**: Show available information while clearly marking missing components
- **API Timeouts**: Graceful degradation with manual refresh options and status explanations
- **Invalid Responses**: Error boundaries with detailed logging and fallback display modes
- **Rapid Status Changes**: Debounced updates to prevent UI flickering during hardware events

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