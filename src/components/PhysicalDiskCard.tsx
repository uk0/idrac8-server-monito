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
      case 'offline':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const formatValue = (value: string | number): string => {
    if (typeof value === 'string') return value;
    if (typeof value === 'number') return value.toString();
    return 'N/A';
  };

  const getTemperatureDisplay = () => {
    const temp = formatValue(disk.temperature);
    if (temp === 'N/A') return temp;
    return temp.includes('°') ? temp : `${temp}°C`;
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
            <span className="text-muted-foreground">Size:</span>
            <p className="font-mono">{disk.size}</p>
          </div>
          <div>
            <span className="text-muted-foreground">Serial:</span>
            <p className="font-mono text-xs">{disk.serialNumber}</p>
          </div>
          <div>
            <span className="text-muted-foreground">Interface:</span>
            <p className="font-mono">{disk.interface}</p>
          </div>
          <div>
            <span className="text-muted-foreground">Manufacturer:</span>
            <p className="font-mono">{disk.manufacturer}</p>
          </div>
          <div>
            <span className="text-muted-foreground">Type:</span>
            <p className="font-mono">{disk.mediaType}</p>
          </div>
        </div>

        <div className="flex items-center justify-between pt-2 border-t">
          <div className="flex items-center gap-1 text-sm">
            <Thermometer className="h-4 w-4" />
            <span>{getTemperatureDisplay()}</span>
          </div>
          <div className="flex items-center gap-1 text-sm text-muted-foreground">
            <Clock className="h-4 w-4" />
            <span>{formatValue(disk.powerOnHours)} hrs</span>
          </div>
        </div>

        {disk.location && disk.location !== 'Unknown' && (
          <div className="text-sm">
            <span className="text-muted-foreground">Location:</span>
            <span className="ml-2 font-mono">{disk.location}</span>
          </div>
        )}

        {typeof disk.predictiveFailure === 'number' && disk.predictiveFailure < 50 && (
          <div className="flex items-center gap-2 p-2 bg-yellow-50 rounded-md border border-yellow-200">
            <AlertTriangle className="h-4 w-4 text-yellow-600" />
            <span className="text-sm text-yellow-800">Media life: {disk.predictiveFailure}% remaining</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}