import { ServerStatus } from '@/types/hardware';

const API_BASE_URL = '/api';

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
      
      // Return data as-is since Python backend provides the correct format
      return data;
    } catch (error) {
      console.error('Failed to fetch server status:', error);
      throw error;
    }
  }
  
  async checkConnection(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/health`, {
        method: 'GET',
      });
      return response.ok;
    } catch (error) {
      console.error('Backend connection failed:', error);
      return false;
    }
  }
}