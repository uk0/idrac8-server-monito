import { ServerStatus, PhysicalDisk, VirtualDisk, RaidController, SystemAlert } from '@/types/hardware';

// Simulated data that represents realistic IDRAC8 monitoring data
export const generateMockServerData = (): ServerStatus => {
  const now = new Date();
  
  const physicalDisks: PhysicalDisk[] = [
    {
      id: 'disk-0-0',
      name: 'Physical Disk 0:0',
      model: 'DELL ST600MM0006',
      serialNumber: 'S0M3XYZ1',
      capacity: '600 GB',
      status: 'healthy',
      temperature: 32,
      smartStatus: 'passed',
      badSectors: 0,
      powerOnHours: 8760,
      predictiveFailure: false,
      lastChecked: now
    },
    {
      id: 'disk-0-1',
      name: 'Physical Disk 0:1',
      model: 'DELL ST600MM0006',
      serialNumber: 'S0M3XYZ2',
      capacity: '600 GB',
      status: 'warning',
      temperature: 45,
      smartStatus: 'passed',
      badSectors: 3,
      powerOnHours: 12000,
      predictiveFailure: true,
      lastChecked: now
    },
    {
      id: 'disk-0-2',
      name: 'Physical Disk 0:2',
      model: 'DELL ST600MM0006',
      serialNumber: 'S0M3XYZ3',
      capacity: '600 GB',
      status: 'healthy',
      temperature: 35,
      smartStatus: 'passed',
      badSectors: 0,
      powerOnHours: 7200,
      predictiveFailure: false,
      lastChecked: now
    },
    {
      id: 'disk-0-3',
      name: 'Physical Disk 0:3',
      model: 'DELL ST600MM0006',
      serialNumber: 'S0M3XYZ4',
      capacity: '600 GB',
      status: 'critical',
      temperature: 55,
      smartStatus: 'failed',
      badSectors: 25,
      powerOnHours: 15000,
      predictiveFailure: true,
      lastChecked: now
    }
  ];

  const virtualDisks: VirtualDisk[] = [
    {
      id: 'vd-0',
      name: 'Virtual Disk 0',
      raidLevel: 'RAID-5',
      status: 'degraded',
      capacity: '1.8 TB',
      usedSpace: '1.2 TB',
      physicalDisks: ['disk-0-0', 'disk-0-1', 'disk-0-2', 'disk-0-3'],
      lastChecked: now
    },
    {
      id: 'vd-1',
      name: 'Virtual Disk 1',
      raidLevel: 'RAID-1',
      status: 'optimal',
      capacity: '600 GB',
      usedSpace: '300 GB',
      physicalDisks: ['disk-1-0', 'disk-1-1'],
      lastChecked: now
    }
  ];

  const raidControllers: RaidController[] = [
    {
      id: 'ctrl-0',
      name: 'RAID Controller 0',
      model: 'DELL PERC H730',
      status: 'healthy',
      batteryStatus: 'healthy',
      cacheSize: '1 GB',
      temperature: 42,
      lastChecked: now
    }
  ];

  const alerts: SystemAlert[] = [
    {
      id: 'alert-1',
      severity: 'critical',
      title: 'Physical Disk Failure Predicted',
      message: 'Physical Disk 0:3 showing signs of imminent failure. Immediate replacement recommended.',
      component: 'disk-0-3',
      timestamp: new Date(now.getTime() - 1000 * 60 * 30), // 30 minutes ago
      acknowledged: false
    },
    {
      id: 'alert-2',
      severity: 'warning',
      title: 'Disk Temperature High',
      message: 'Physical Disk 0:1 temperature is elevated (45°C). Monitor closely.',
      component: 'disk-0-1',
      timestamp: new Date(now.getTime() - 1000 * 60 * 60), // 1 hour ago
      acknowledged: false
    },
    {
      id: 'alert-3',
      severity: 'warning',
      title: 'Virtual Disk Degraded',
      message: 'Virtual Disk 0 is in degraded state due to physical disk issues.',
      component: 'vd-0',
      timestamp: new Date(now.getTime() - 1000 * 60 * 45), // 45 minutes ago
      acknowledged: false
    }
  ];

  return {
    serverName: 'IDRAC8-SERVER-01',
    ipAddress: '10.88.51.66',
    lastUpdate: now,
    connectionStatus: 'connected',
    physicalDisks,
    virtualDisks,
    raidControllers,
    alerts
  };
};

// Simulate realistic data variations for periodic updates
export const updateServerData = (currentData: ServerStatus): ServerStatus => {
  const updatedData = { ...currentData };
  updatedData.lastUpdate = new Date();
  
  // Simulate minor temperature fluctuations
  updatedData.physicalDisks = updatedData.physicalDisks.map(disk => ({
    ...disk,
    temperature: Math.max(25, Math.min(60, disk.temperature + (Math.random() - 0.5) * 3)),
    lastChecked: new Date()
  }));
  
  // Occasionally add new alerts
  if (Math.random() < 0.1) { // 10% chance of new alert
    const newAlert: SystemAlert = {
      id: `alert-${Date.now()}`,
      severity: Math.random() < 0.3 ? 'critical' : 'warning',
      title: 'System Check Alert',
      message: 'Routine monitoring detected a parameter change.',
      component: 'system',
      timestamp: new Date(),
      acknowledged: false
    };
    updatedData.alerts = [newAlert, ...updatedData.alerts].slice(0, 10); // Keep only latest 10
  }
  
  return updatedData;
};