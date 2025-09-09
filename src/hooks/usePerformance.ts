/**
 * Hook for fetching performance metrics
 */
import { useQuery } from '@tanstack/react-query';
import { api } from '@/api/client';
import { useToast } from '@/hooks/use-toast';

export interface PerformanceData {
  total_pnl: number;
  win_rate: number;
  sharpe_ratio: number;
  max_drawdown: number;
  total_trades: number;
  daily_pnl: Array<{ date: string; pnl: number }>;
  tier_performance: Array<{
    tier: string;
    win_rate: number;
    avg_return: number;
    trades: number;
  }>;
  monthly_returns: Array<{ month: string; return: number }>;
}

export function usePerformance() {
  const { toast } = useToast();
  
  return useQuery({
    queryKey: ['performance'],
    queryFn: async () => {
      try {
        const response = await api.getPerformance();
        return response.data.data as PerformanceData;
      } catch (error: any) {
        toast({
          title: "Error fetching performance",
          description: error.message || "Failed to fetch performance metrics",
          variant: "destructive",
        });
        throw error;
      }
    },
    refetchInterval: 300000, // 5 minutes
  });
}