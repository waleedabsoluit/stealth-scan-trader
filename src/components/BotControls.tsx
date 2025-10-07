import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Play, Pause, RotateCw } from "lucide-react";
import { useBotStatus, useToggleAutoTrade, useToggleScanning } from "@/hooks/useBotControl";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/api/client";
import { useToast } from "@/hooks/use-toast";
import { useState } from "react";

export const BotControls = () => {
  const { data: status } = useBotStatus();
  const toggleAutoTrade = useToggleAutoTrade();
  const toggleScanning = useToggleScanning();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [isScanning, setIsScanning] = useState(false);

  const runScan = useMutation({
    mutationFn: async () => {
      setIsScanning(true);
      const response = await api.post('/orchestrate/scan');
      return response.data.data;
    },
    onSuccess: (data) => {
      toast({
        title: "Scan Complete",
        description: `Found ${data.signals_stored} high-quality signals from ${data.total_scanned} scanned`,
      });
      queryClient.invalidateQueries({ queryKey: ['signals'] });
      setIsScanning(false);
    },
    onError: (error: any) => {
      toast({
        title: "Scan Failed",
        description: error.response?.data?.detail || "Error running scan",
        variant: "destructive",
      });
      setIsScanning(false);
    }
  });

  return (
    <Card className="p-4">
      <h3 className="font-semibold mb-4">Bot Controls</h3>
      
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <p className="font-medium">Auto Trading</p>
            <p className="text-xs text-muted-foreground">
              {status?.auto_trading ? 'Trading enabled' : 'Trading paused'}
            </p>
          </div>
          <Button
            variant={status?.auto_trading ? "default" : "outline"}
            size="sm"
            onClick={() => toggleAutoTrade.mutate()}
            disabled={toggleAutoTrade.isPending}
          >
            {status?.auto_trading ? (
              <>
                <Pause className="h-4 w-4 mr-2" />
                Pause
              </>
            ) : (
              <>
                <Play className="h-4 w-4 mr-2" />
                Start
              </>
            )}
          </Button>
        </div>

        <div className="flex items-center justify-between">
          <div>
            <p className="font-medium">Market Scanning</p>
            <p className="text-xs text-muted-foreground">
              {status?.scanning ? 'Actively scanning' : 'Scanning stopped'}
            </p>
          </div>
          <Button
            variant={status?.scanning ? "default" : "outline"}
            size="sm"
            onClick={() => toggleScanning.mutate()}
            disabled={toggleScanning.isPending}
          >
            {status?.scanning ? (
              <>
                <Pause className="h-4 w-4 mr-2" />
                Stop
              </>
            ) : (
              <>
                <Play className="h-4 w-4 mr-2" />
                Scan
              </>
            )}
          </Button>
        </div>

        <div className="pt-3 border-t border-border">
          <Button
            variant="outline"
            className="w-full"
            onClick={() => runScan.mutate()}
            disabled={isScanning}
          >
            <RotateCw className={`h-4 w-4 mr-2 ${isScanning ? 'animate-spin' : ''}`} />
            {isScanning ? 'Scanning...' : 'Run Full Scan Now'}
          </Button>
        </div>

        {status && (
          <div className="pt-3 border-t border-border space-y-1 text-xs text-muted-foreground">
            <div className="flex justify-between">
              <span>Scans:</span>
              <span className="font-medium">{status.scan_count}</span>
            </div>
            <div className="flex justify-between">
              <span>Trades:</span>
              <span className="font-medium">{status.trade_count}</span>
            </div>
            {status.last_action_at && (
              <div className="flex justify-between">
                <span>Last Action:</span>
                <span className="font-medium">
                  {new Date(status.last_action_at).toLocaleTimeString()}
                </span>
              </div>
            )}
          </div>
        )}
      </div>
    </Card>
  );
};
