import { VirtualDisk } from '@/types/hardware';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Database, HardDrive } from '@phosphor-icons/react';

interface VirtualDiskCardProps {
  disk: VirtualDisk;
}

export function VirtualDiskCard({ disk }: VirtualDiskCardProps) {
  const getStatusColor = (status: VirtualDisk['status']) => {
    switch (status) {
      case 'optimal':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'degraded':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'failed':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'rebuilding':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const calculateUsagePercentage = () => {
    const used = parseFloat(disk.usedSpace.replace(/[^\d.]/g, ''));
    const total = parseFloat(disk.capacity.replace(/[^\d.]/g, ''));
    return Math.round((used / total) * 100);
  };

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <Database className="h-5 w-5" />
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
            <span className="text-muted-foreground">RAID Level:</span>
            <p className="font-mono font-medium">{disk.raidLevel}</p>
          </div>
          <div>
            <span className="text-muted-foreground">Total Capacity:</span>
            <p className="font-mono">{disk.capacity}</p>
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex justify-between items-center text-sm">
            <span className="text-muted-foreground">Storage Usage</span>
            <span className="font-mono">{disk.usedSpace} / {disk.capacity}</span>
          </div>
          <Progress value={calculateUsagePercentage()} className="h-2" />
          <div className="text-right text-xs text-muted-foreground">
            {calculateUsagePercentage()}% used
          </div>
        </div>

        {disk.status === 'rebuilding' && disk.rebuildProgress !== undefined && (
          <div className="space-y-2 p-3 bg-blue-50 rounded-md border border-blue-200">
            <div className="flex justify-between items-center text-sm">
              <span className="text-blue-800 font-medium">Rebuilding Progress</span>
              <span className="font-mono text-blue-800">{disk.rebuildProgress}%</span>
            </div>
            <Progress value={disk.rebuildProgress} className="h-2" />
          </div>
        )}

        <div className="pt-2 border-t">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <HardDrive className="h-4 w-4" />
            <span>{disk.physicalDisks.length} physical disks</span>
          </div>
          <div className="mt-1 text-xs text-muted-foreground">
            Last checked: {disk.lastChecked.toLocaleTimeString()}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}