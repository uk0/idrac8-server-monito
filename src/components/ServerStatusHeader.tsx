import { ServerStatus } from '@/types/hardware';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Server, Wifi, RefreshCcw, Circle } from '@phosphor-icons/react';

interface ServerStatusHeaderProps {
  serverStatus: ServerStatus;
  onRefresh: () => void;
  isRefreshing: boolean;
}

export function ServerStatusHeader({ serverStatus, onRefresh, isRefreshing }: ServerStatusHeaderProps) {
  const getConnectionStatusColor = (status: ServerStatus['connectionStatus']) => {
    switch (status) {
      case 'connected':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'disconnected':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      case 'error':
        return 'bg-red-100 text-red-800 border-red-200';
    }
  };

  const getConnectionIcon = (status: ServerStatus['connectionStatus']) => {
    switch (status) {
      case 'connected':
        return <Circle className="h-3 w-3 fill-green-600 text-green-600" />;
      case 'disconnected':
        return <Circle className="h-3 w-3 fill-gray-600 text-gray-600" />;
      case 'error':
        return <Circle className="h-3 w-3 fill-red-600 text-red-600" />;
    }
  };

  const getOverallHealth = () => {
    const criticalDisks = serverStatus.physicalDisks.filter(disk => disk.status === 'critical' || disk.status === 'failed').length;
    const warningDisks = serverStatus.physicalDisks.filter(disk => disk.status === 'warning').length;
    const degradedVDisks = serverStatus.virtualDisks.filter(vd => vd.status === 'degraded' || vd.status === 'failed').length;
    const criticalAlerts = serverStatus.alerts.filter(alert => alert.severity === 'critical' && !alert.acknowledged).length;

    if (criticalDisks > 0 || degradedVDisks > 0 || criticalAlerts > 0) {
      return { status: 'critical', label: 'Critical Issues Detected' };
    }
    if (warningDisks > 0) {
      return { status: 'warning', label: 'Warnings Present' };
    }
    return { status: 'healthy', label: 'All Systems Healthy' };
  };

  const health = getOverallHealth();

  return (
    <Card className="mb-6">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Server className="h-6 w-6" />
            <div>
              <CardTitle className="text-2xl">{serverStatus.serverName}</CardTitle>
              <div className="flex items-center gap-2 mt-1">
                <Wifi className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm text-muted-foreground">{serverStatus.ipAddress}</span>
                <div className="flex items-center gap-1">
                  {getConnectionIcon(serverStatus.connectionStatus)}
                  <Badge className={getConnectionStatusColor(serverStatus.connectionStatus)}>
                    {serverStatus.connectionStatus.toUpperCase()}
                  </Badge>
                </div>
              </div>
            </div>
          </div>
          <Button
            onClick={onRefresh}
            disabled={isRefreshing}
            variant="outline"
            className="flex items-center gap-2"
          >
            <RefreshCcw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="flex items-center gap-2">
            <div className="text-sm text-muted-foreground">Overall Health:</div>
            <Badge 
              className={
                health.status === 'critical' 
                  ? 'bg-red-100 text-red-800 border-red-200' 
                  : health.status === 'warning'
                  ? 'bg-yellow-100 text-yellow-800 border-yellow-200'
                  : 'bg-green-100 text-green-800 border-green-200'
              }
            >
              {health.label}
            </Badge>
          </div>
          <div className="text-sm">
            <span className="text-muted-foreground">Physical Disks:</span>
            <span className="ml-2 font-mono">{serverStatus.physicalDisks.length}</span>
          </div>
          <div className="text-sm">
            <span className="text-muted-foreground">Virtual Disks:</span>
            <span className="ml-2 font-mono">{serverStatus.virtualDisks.length}</span>
          </div>
          <div className="text-sm">
            <span className="text-muted-foreground">Last Update:</span>
            <span className="ml-2 font-mono">{serverStatus.lastUpdate.toLocaleTimeString()}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}