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
            <span className="text-muted-foreground">Total Size:</span>
            <p className="font-mono">{disk.size}</p>
          </div>
        </div>

        <div className="pt-2 border-t">
          <div className="text-xs text-muted-foreground">
            Last updated: {new Date(disk.lastUpdated).toLocaleTimeString()}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}