/**
 * Hook for fetching and managing trading signals
 */
import { useQuery } from '@tanstack/react-query';
import { api } from '@/api/client';
import { useToast } from '@/hooks/use-toast';

export interface Signal {
  symbol: string;
  tier: string;
  confidence: number;
  entry_price: number;
  current_price: number;
  change: number;
  volume: number;
  obv_slope: number;
  vwap_distance: number;
  timestamp: string;
  status: string;
}

export interface SignalsResponse {
  signals: Signal[];
  metrics: {
    total_signals: number;
    active_modules: number;
    cooldowns_active?: number;
  };
  latency?: number;
  errors?: any[];
}

export function useSignals(refetchInterval = 60000) {
  const { toast } = useToast();
  
  return useQuery({
    queryKey: ['signals'],
    queryFn: async () => {
      try {
        const response = await api.getSignals();
        return response.data.data as SignalsResponse;
      } catch (error: any) {
        toast({
          title: "Error fetching signals",
          description: error.message || "Failed to fetch trading signals",
          variant: "destructive",
        });
        throw error;
      }
    },
    refetchInterval,
    refetchIntervalInBackground: true,
  });
}