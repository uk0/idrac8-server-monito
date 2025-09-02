import { ServerStatus } from '@/types/hardware';

const API_BASE_URL = 'http://localhost:8080/api/v1';

export class ServerAPI {
  private static instance: ServerAPI;
  
  private constructor() {}
  
  static getInstance(): ServerAPI {
    if (!ServerAPI.instance) {
      ServerAPI.instance = new ServerAPI();
    }
    return ServerAPI.instance;
  }
  
  async getServerStatus(): Promise<ServerStatus> {
    try {
      const response = await fetch(`${API_BASE_URL}/server/status`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Convert string dates back to Date objects
      return {
        ...data,
        lastUpdate: new Date(data.lastUpdate),
        physicalDisks: data.physicalDisks.map((disk: any) => ({
          ...disk,
          lastChecked: new Date(disk.lastChecked),
        })),
        virtualDisks: data.virtualDisks.map((disk: any) => ({
          ...disk,
          lastChecked: new Date(disk.lastChecked),
        })),
        raidControllers: data.raidControllers.map((controller: any) => ({
          ...controller,
          lastChecked: new Date(controller.lastChecked),
        })),
        alerts: data.alerts.map((alert: any) => ({
          ...alert,
          timestamp: new Date(alert.timestamp),
        })),
      };
    } catch (error) {
      console.error('Failed to fetch server status:', error);
      throw error;
    }
  }
  
  async checkConnection(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL.replace('/api/v1', '')}/health`, {
        method: 'GET',
      });
      return response.ok;
    } catch (error) {
      console.error('Backend connection failed:', error);
      return false;
    }
  }
}