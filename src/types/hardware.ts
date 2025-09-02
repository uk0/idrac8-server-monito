export interface PhysicalDisk {
  id: string;
  name: string;
  model: string;
  serialNumber: string;
  size: string;
  status: 'healthy' | 'warning' | 'critical' | 'failed' | 'offline' | 'unknown';
  interface: string;
  manufacturer: string;
  mediaType: string;
  location: string;
  temperature: string | number;
  powerOnHours: string | number;
  predictiveFailure: string | number;
  lastUpdated: string;
}

export interface VirtualDisk {
  id: string;
  name: string;
  raidLevel: string;
  status: 'healthy' | 'warning' | 'critical' | 'failed' | 'offline' | 'unknown';
  size: string;
  lastUpdated: string;
}

export interface SystemAlert {
  id: string;
  severity: 'info' | 'warning' | 'critical';
  message: string;
  timestamp: string;
  acknowledged: boolean;
}

export interface ServerInfo {
  name: string;
  model: string;
  manufacturer: string;
  serialNumber: string;
  powerState: string;
  lastUpdated: string;
}

export interface ServerStatus {
  serverInfo: ServerInfo;
  physicalDisks: PhysicalDisk[];
  virtualDisks: VirtualDisk[];
  alerts: SystemAlert[];
  lastRefresh: string;
}