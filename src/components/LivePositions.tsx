import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { TrendingUp, TrendingDown, X } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import api from "@/api/client";
import { useWebSocket } from "@/hooks/useWebSocket";
import { useState, useEffect } from "react";

interface Position {
  trade_id: string;
  symbol: string;
  quantity: number;
  entry_price: number;
  current_price: number;
  unrealized_pnl: number;
  unrealized_pnl_percent: number;
  stop_loss?: number;
  take_profit?: number;
}

export const LivePositions = () => {
  const [positions, setPositions] = useState<Position[]>([]);

  const { data, refetch } = useQuery({
    queryKey: ['live-positions'],
    queryFn: async () => {
      const response = await api.get('/trades/open');
      return response.data.data;
    },
    refetchInterval: 5000, // Refetch every 5 seconds
  });

  useWebSocket({
    onTrade: (trade) => {
      refetch();
    },
    onMarketUpdate: (marketData) => {
      // Update position prices in real-time
      setPositions(prev => prev.map(pos => {
        if (marketData[pos.symbol]) {
          const currentPrice = marketData[pos.symbol].price;
          const unrealized_pnl = (currentPrice - pos.entry_price) * pos.quantity;
          const unrealized_pnl_percent = (unrealized_pnl / (pos.entry_price * pos.quantity)) * 100;
          
          return {
            ...pos,
            current_price: currentPrice,
            unrealized_pnl,
            unrealized_pnl_percent
          };
        }
        return pos;
      }));
    }
  });

  useEffect(() => {
    if (data?.positions) {
      setPositions(data.positions);
    }
  }, [data]);

  const closePosition = async (tradeId: string) => {
    try {
      await api.post(`/trades/${tradeId}/close`);
      refetch();
    } catch (error) {
      console.error('Error closing position:', error);
    }
  };

  const totalUnrealizedPnL = positions.reduce((sum, pos) => sum + pos.unrealized_pnl, 0);

  return (
    <Card className="p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">Open Positions</h3>
        <div className="text-sm">
          <span className="text-muted-foreground">Total P&L: </span>
          <span className={totalUnrealizedPnL >= 0 ? 'text-green-500' : 'text-red-500'}>
            ${totalUnrealizedPnL.toFixed(2)}
          </span>
        </div>
      </div>

      <div className="space-y-2">
        {positions.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-4">
            No open positions
          </p>
        ) : (
          positions.map((pos) => (
            <div
              key={pos.trade_id}
              className="p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="font-medium">{pos.symbol}</span>
                  <Badge variant="outline" className="text-xs">
                    {pos.quantity} shares
                  </Badge>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => closePosition(pos.trade_id)}
                  className="h-6 w-6 p-0"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="text-muted-foreground">Entry: </span>
                  <span>${pos.entry_price.toFixed(2)}</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Current: </span>
                  <span>${pos.current_price.toFixed(2)}</span>
                </div>
                {pos.stop_loss && (
                  <div>
                    <span className="text-muted-foreground">Stop: </span>
                    <span className="text-red-500">${pos.stop_loss.toFixed(2)}</span>
                  </div>
                )}
                {pos.take_profit && (
                  <div>
                    <span className="text-muted-foreground">Target: </span>
                    <span className="text-green-500">${pos.take_profit.toFixed(2)}</span>
                  </div>
                )}
              </div>

              <div className="flex items-center gap-2 mt-2 pt-2 border-t border-border">
                {pos.unrealized_pnl >= 0 ? (
                  <TrendingUp className="h-4 w-4 text-green-500" />
                ) : (
                  <TrendingDown className="h-4 w-4 text-red-500" />
                )}
                <span className={`font-medium ${pos.unrealized_pnl >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                  ${pos.unrealized_pnl.toFixed(2)} ({pos.unrealized_pnl_percent.toFixed(2)}%)
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </Card>
  );
};
