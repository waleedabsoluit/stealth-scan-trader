/**
 * Hook for fetching risk metrics
 */
import { useQuery } from '@tanstack/react-query';
import { api } from '@/api/client';
import { useToast } from '@/hooks/use-toast';

export interface RiskData {
  portfolio_risk: number;
  market_volatility: number;
  max_drawdown: number;
  risk_alerts: number;
  risk_history: Array<{
    time: string;
    portfolio: number;
    market: number;
    position: number;
  }>;
  exposure_breakdown: Array<{
    sector: string;
    exposure: number;
    risk: string;
  }>;
  alerts: Array<{
    severity: string;
    message: string;
    timestamp: string;
  }>;
}

export function useRisk() {
  const { toast } = useToast();
  
  return useQuery({
    queryKey: ['risk'],
    queryFn: async () => {
      try {
        const response = await api.getRisk();
        return response.data.data as RiskData;
      } catch (error: any) {
        toast({
          title: "Error fetching risk data",
          description: error.message || "Failed to fetch risk metrics",
          variant: "destructive",
        });
        throw error;
      }
    },
    refetchInterval: 60000, // 1 minute
  });
}