import { useState, useEffect } from 'react';
import { useKV } from '@github/spark/hooks';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Toaster } from '@/components/ui/sonner';
import { toast } from 'sonner';
import { ServerStatus } from '@/types/hardware';
import { generateMockServerData, updateServerData } from '@/lib/mockData';
import { ServerStatusHeader } from '@/components/ServerStatusHeader';
import { PhysicalDiskCard } from '@/components/PhysicalDiskCard';
import { VirtualDiskCard } from '@/components/VirtualDiskCard';
import { AlertsPanel } from '@/components/AlertsPanel';

function App() {
  const [serverData, setServerData] = useKV<ServerStatus>('server-data', generateMockServerData());
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastRefresh, setLastRefresh] = useState(Date.now());

  // Auto-refresh every 5 minutes (300,000 ms)
  useEffect(() => {
    const interval = setInterval(() => {
      setServerData(currentData => updateServerData(currentData));
      setLastRefresh(Date.now());
      toast.info('Hardware status updated automatically');
    }, 300000); // 5 minutes

    return () => clearInterval(interval);
  }, [setServerData]);

  const handleManualRefresh = () => {
    setIsRefreshing(true);
    // Simulate API call delay
    setTimeout(() => {
      setServerData(currentData => updateServerData(currentData));
      setLastRefresh(Date.now());
      setIsRefreshing(false);
      toast.success('Hardware status refreshed');
    }, 1500);
  };

  const handleAcknowledgeAlert = (alertId: string) => {
    setServerData(currentData => ({
      ...currentData,
      alerts: currentData.alerts.map(alert =>
        alert.id === alertId ? { ...alert, acknowledged: true } : alert
      )
    }));
    toast.success('Alert acknowledged');
  };

  const criticalDisks = serverData.physicalDisks.filter(disk => 
    disk.status === 'critical' || disk.status === 'failed'
  );
  const warningDisks = serverData.physicalDisks.filter(disk => 
    disk.status === 'warning'
  );
  const healthyDisks = serverData.physicalDisks.filter(disk => 
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
                alerts={serverData.alerts}
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
                {serverData.physicalDisks.length} disks total
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {serverData.physicalDisks.map(disk => (
                <PhysicalDiskCard key={disk.id} disk={disk} />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="virtual-disks" className="space-y-6">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold">Virtual Disks & RAID Arrays</h3>
              <div className="text-sm text-muted-foreground">
                {serverData.virtualDisks.length} virtual disks configured
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {serverData.virtualDisks.map(disk => (
                <VirtualDiskCard key={disk.id} disk={disk} />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="alerts" className="space-y-6">
            <AlertsPanel 
              alerts={serverData.alerts}
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