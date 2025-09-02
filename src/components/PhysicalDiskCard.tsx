import { PhysicalDisk } from '@/types/hardware';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { HardDrive, Thermometer, Clock, AlertTriangle } from '@phosphor-icons/react';

interface PhysicalDiskCardProps {
  disk: PhysicalDisk;
}

export function PhysicalDiskCard({ disk }: PhysicalDiskCardProps) {
  const getStatusColor = (status: PhysicalDisk['status']) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'failed':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getTemperatureColor = (temp: number) => {
    if (temp < 40) return 'text-green-600';
    if (temp < 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  const formatUptime = (hours: number) => {
    const days = Math.floor(hours / 24);
    return `${days} days`;
  };

  return (
    <Card className="relative">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <HardDrive className="h-5 w-5" />
            {disk.name}
          </CardTitle>
          <Badge className={getStatusColor(disk.status)}>
            {disk.status.toUpperCase()}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-muted-foreground">Model:</span>
            <p className="font-mono">{disk.model}</p>
          </div>
          <div>
            <span className="text-muted-foreground">Capacity:</span>
            <p className="font-mono">{disk.capacity}</p>
          </div>
          <div>
            <span className="text-muted-foreground">Serial:</span>
            <p className="font-mono text-xs">{disk.serialNumber}</p>
          </div>
          <div>
            <span className="text-muted-foreground">SMART:</span>
            <p className={`font-mono ${disk.smartStatus === 'passed' ? 'text-green-600' : 'text-red-600'}`}>
              {disk.smartStatus.toUpperCase()}
            </p>
          </div>
        </div>

        <div className="flex items-center justify-between pt-2 border-t">
          <div className="flex items-center gap-1 text-sm">
            <Thermometer className={`h-4 w-4 ${getTemperatureColor(disk.temperature)}`} />
            <span className={getTemperatureColor(disk.temperature)}>{disk.temperature}°C</span>
          </div>
          <div className="flex items-center gap-1 text-sm text-muted-foreground">
            <Clock className="h-4 w-4" />
            <span>{formatUptime(disk.powerOnHours)}</span>
          </div>
        </div>

        {disk.badSectors > 0 && (
          <div className="flex items-center gap-2 p-2 bg-yellow-50 rounded-md border border-yellow-200">
            <AlertTriangle className="h-4 w-4 text-yellow-600" />
            <span className="text-sm text-yellow-800">{disk.badSectors} bad sectors detected</span>
          </div>
        )}

        {disk.predictiveFailure && (
          <div className="flex items-center gap-2 p-2 bg-red-50 rounded-md border border-red-200">
            <AlertTriangle className="h-4 w-4 text-red-600" />
            <span className="text-sm text-red-800 font-medium">Predictive failure detected</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}