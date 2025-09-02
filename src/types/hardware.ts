export interface PhysicalDisk {
  id: string;
  name: string;
  model: string;
  serialNumber: string;
  capacity: string;
  status: 'healthy' | 'warning' | 'critical' | 'failed';
  temperature: number;
  smartStatus: 'passed' | 'failed';
  badSectors: number;
  powerOnHours: number;
  predictiveFailure: boolean;
  lastChecked: Date;
}

export interface VirtualDisk {
  id: string;
  name: string;
  raidLevel: string;
  status: 'optimal' | 'degraded' | 'failed' | 'rebuilding';
  capacity: string;
  usedSpace: string;
  physicalDisks: string[];
  rebuildProgress?: number;
  lastChecked: Date;
}

export interface RaidController {
  id: string;
  name: string;
  model: string;
  status: 'healthy' | 'warning' | 'critical';
  batteryStatus: 'healthy' | 'warning' | 'failed';
  cacheSize: string;
  temperature: number;
  lastChecked: Date;
}

export interface SystemAlert {
  id: string;
  severity: 'info' | 'warning' | 'critical';
  title: string;
  message: string;
  component: string;
  timestamp: Date;
  acknowledged: boolean;
}

export interface ServerStatus {
  serverName: string;
  ipAddress: string;
  lastUpdate: Date;
  connectionStatus: 'connected' | 'disconnected' | 'error';
  physicalDisks: PhysicalDisk[];
  virtualDisks: VirtualDisk[];
  raidControllers: RaidController[];
  alerts: SystemAlert[];
}