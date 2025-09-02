import { useState, useEffect } from 'react';
import { useKV } from '@github/spark/hooks';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Toaster } from '@/components/ui/sonner';
import { toast } from 'sonner';
import { ServerStatus } from '@/types/hardware';
import { ServerAPI } from '@/lib/api';
import { ServerStatusHeader } from '@/components/ServerStatusHeader';
import { PhysicalDiskCard } from '@/components/PhysicalDiskCard';
import { VirtualDiskCard } from '@/components/VirtualDiskCard';
import { AlertsPanel } from '@/components/AlertsPanel';

function App() {
  const [serverData, setServerData] = useKV<ServerStatus | null>('server-data', null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastRefresh, setLastRefresh] = useState(Date.now());
  const [connectionError, setConnectionError] = useState(false);
  
  const api = ServerAPI.getInstance();

  // Function to fetch server data
  const fetchServerData = async (showToast = true) => {
    try {
      setConnectionError(false);
      const data = await api.getServerStatus();
      setServerData(data);
      setLastRefresh(Date.now());
      
      if (showToast) {
        toast.success('Hardware status updated from IDRAC8');
      }
    } catch (error) {
      console.error('Failed to fetch server data:', error);
      setConnectionError(true);
      
      // Set a default structure to prevent undefined errors only if no data exists
      if (!serverData) {
        setServerData({
          serverInfo: {
            name: 'IDRAC8 Server',
            model: 'Connection Failed',
            manufacturer: 'Dell',
            serialNumber: 'N/A',
            powerState: 'Unknown',
            lastUpdated: new Date().toISOString()
          },
          physicalDisks: [],
          virtualDisks: [],
          alerts: [{
            id: 'connection-error',
            severity: 'critical' as const,
            message: 'Unable to connect to IDRAC8 server. Please check network connectivity and backend service.',
            timestamp: new Date().toISOString(),
            acknowledged: false
          }],
          lastRefresh: new Date().toISOString()
        });
      }
      
      if (showToast) {
        toast.error('Failed to connect to IDRAC8 server. Please check the backend service.');
      }
    }
  };

  // Initial data fetch
  useEffect(() => {
    fetchServerData(false);
  }, []);

  // Auto-refresh every 5 minutes (300,000 ms)
  useEffect(() => {
    const interval = setInterval(() => {
      fetchServerData(true);
    }, 300000); // 5 minutes

    return () => clearInterval(interval);
  }, []);

  const handleManualRefresh = async () => {
    setIsRefreshing(true);
    await fetchServerData(true);
    setIsRefreshing(false);
  };

  const handleAcknowledgeAlert = (alertId: string) => {
    if (!serverData || !serverData.alerts) return;
    
    setServerData({
      ...serverData,
      alerts: serverData.alerts.map(alert =>
        alert.id === alertId ? { ...alert, acknowledged: true } : alert
      )
    });
    toast.success('Alert acknowledged');
  };

  // Show loading state if no data yet
  if (!serverData) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">
            {connectionError ? 'Failed to connect to IDRAC8 server' : 'Connecting to IDRAC8...'}
          </p>
          {connectionError && (
            <button 
              onClick={() => fetchServerData(true)}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
            >
              Retry Connection
            </button>
          )}
        </div>
      </div>
    );
  }

  const criticalDisks = (serverData.physicalDisks || []).filter(disk => 
    disk.status === 'critical' || disk.status === 'failed'
  );
  const warningDisks = (serverData.physicalDisks || []).filter(disk => 
    disk.status === 'warning'
  );
  const healthyDisks = (serverData.physicalDisks || []).filter(disk => 
    disk.status === 'healthy'
  );

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        <ServerStatusHeader 
          serverStatus={serverData}
          onRefresh={handleManualRefresh}
          isRefreshing={isRefreshing}
        />

        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="physical-disks">Physical Disks</TabsTrigger>
            <TabsTrigger value="virtual-disks">Virtual Disks</TabsTrigger>
            <TabsTrigger value="alerts">Alerts</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <AlertsPanel 
                alerts={serverData.alerts || []}
                onAcknowledge={handleAcknowledgeAlert}
              />
              
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Hardware Summary</h3>
                
                {criticalDisks.length > 0 && (
                  <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                    <h4 className="font-medium text-red-800 mb-2">Critical Issues Require Immediate Attention</h4>
                    <ul className="text-sm text-red-700 space-y-1">
                      {criticalDisks.map(disk => (
                        <li key={disk.id}>• {disk.name} - {disk.status === 'failed' ? 'Failed' : 'Critical condition'}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {warningDisks.length > 0 && (
                  <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <h4 className="font-medium text-yellow-800 mb-2">Warning: Monitor These Disks</h4>
                    <ul className="text-sm text-yellow-700 space-y-1">
                      {warningDisks.map(disk => (
                        <li key={disk.id}>• {disk.name} - Elevated temperature or wear detected</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="grid grid-cols-3 gap-4 text-center">
                  <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                    <div className="text-2xl font-bold text-green-800">{healthyDisks.length}</div>
                    <div className="text-sm text-green-600">Healthy Disks</div>
                  </div>
                  <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <div className="text-2xl font-bold text-yellow-800">{warningDisks.length}</div>
                    <div className="text-sm text-yellow-600">Warning Disks</div>
                  </div>
                  <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                    <div className="text-2xl font-bold text-red-800">{criticalDisks.length}</div>
                    <div className="text-sm text-red-600">Critical Disks</div>
                  </div>
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="physical-disks" className="space-y-6">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold">Physical Disks</h3>
              <div className="text-sm text-muted-foreground">
                {(serverData.physicalDisks || []).length} disks total
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {(serverData.physicalDisks || []).map(disk => (
                <PhysicalDiskCard key={disk.id} disk={disk} />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="virtual-disks" className="space-y-6">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold">Virtual Disks & RAID Arrays</h3>
              <div className="text-sm text-muted-foreground">
                {(serverData.virtualDisks || []).length} virtual disks configured
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {(serverData.virtualDisks || []).map(disk => (
                <VirtualDiskCard key={disk.id} disk={disk} />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="alerts" className="space-y-6">
            <AlertsPanel 
              alerts={serverData.alerts || []}
              onAcknowledge={handleAcknowledgeAlert}
            />
          </TabsContent>
        </Tabs>
      </div>
      <Toaster />
    </div>
  );
}

export default App;