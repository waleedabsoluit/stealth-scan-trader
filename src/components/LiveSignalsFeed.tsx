import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown, Activity } from "lucide-react";
import { useWebSocket } from "@/hooks/useWebSocket";
import { useState, useEffect } from "react";
import { useToast } from "@/hooks/use-toast";

interface Signal {
  signal_id: string;
  symbol: string;
  tier: string;
  confidence: number;
  action: string;
  entry_price: number;
  target_price?: number;
  stop_loss?: number;
  created_at: string;
  status: string;
}

export const LiveSignalsFeed = () => {
  const [recentSignals, setRecentSignals] = useState<Signal[]>([]);
  const { toast } = useToast();

  const { isConnected } = useWebSocket({
    onSignal: (signal) => {
      setRecentSignals(prev => [signal, ...prev].slice(0, 10));
      
      // Show toast for high-tier signals
      if (signal.tier === 'PLATINUM' || signal.tier === 'GOLD') {
        toast({
          title: `New ${signal.tier} Signal`,
          description: `${signal.symbol} - ${signal.confidence}% confidence`,
          duration: 5000,
        });
      }
    },
    onAlert: (alert) => {
      toast({
        title: alert.title || "System Alert",
        description: alert.message,
        variant: alert.severity === 'error' ? 'destructive' : 'default',
      });
    }
  });

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'PLATINUM': return 'bg-purple-500';
      case 'GOLD': return 'bg-yellow-500';
      case 'SILVER': return 'bg-gray-400';
      case 'BRONZE': return 'bg-orange-600';
      default: return 'bg-gray-500';
    }
  };

  return (
    <Card className="p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Activity className="h-5 w-5 text-primary" />
          <h3 className="font-semibold">Live Signals Feed</h3>
        </div>
        <div className="flex items-center gap-2">
          <div className={`h-2 w-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className="text-xs text-muted-foreground">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      <div className="space-y-2">
        {recentSignals.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-4">
            No signals yet. Waiting for live updates...
          </p>
        ) : (
          recentSignals.map((signal, index) => (
            <div
              key={signal.signal_id || index}
              className="flex items-center justify-between p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors animate-fade-in"
            >
              <div className="flex items-center gap-3">
                {signal.action === 'BUY' ? (
                  <TrendingUp className="h-4 w-4 text-green-500" />
                ) : (
                  <TrendingDown className="h-4 w-4 text-red-500" />
                )}
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{signal.symbol}</span>
                    <Badge variant="outline" className={`${getTierColor(signal.tier)} text-white text-xs`}>
                      {signal.tier}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    ${signal.entry_price?.toFixed(2)} • {signal.confidence}% confidence
                  </p>
                </div>
              </div>
              <span className="text-xs text-muted-foreground">
                {new Date(signal.created_at).toLocaleTimeString()}
              </span>
            </div>
          ))
        )}
      </div>
    </Card>
  );
};
