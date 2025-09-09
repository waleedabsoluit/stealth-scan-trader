/**
 * Hook for fetching live market data
 */
import { useQuery } from '@tanstack/react-query';
import { api } from '@/api/client';
import { useToast } from '@/hooks/use-toast';

export interface MarketQuote {
  symbol: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number;
  high: number;
  low: number;
  open: number;
  previous_close: number;
  timestamp: string;
  market_cap?: number;
  name?: string;
}

export interface MarketStatus {
  status: string;
  session: string;
  timestamp: string;
}

export function useMarketQuotes(symbols: string[]) {
  const { toast } = useToast();
  
  return useQuery({
    queryKey: ['market-quotes', symbols],
    queryFn: async () => {
      if (!symbols || symbols.length === 0) return {};
      
      try {
        const response = await api.post('/api/market/quotes', symbols);
        return response.data.data as Record<string, MarketQuote>;
      } catch (error: any) {
        console.error('Error fetching market quotes:', error);
        // Don't show toast for every poll failure
        return {};
      }
    },
    refetchInterval: 2000, // Poll every 2 seconds
    enabled: symbols.length > 0,
  });
}

export function useMarketStatus() {
  return useQuery({
    queryKey: ['market-status'],
    queryFn: async () => {
      try {
        const response = await api.get('/api/market/status');
        return response.data.data as MarketStatus;
      } catch (error) {
        console.error('Error fetching market status:', error);
        return {
          status: 'CLOSED',
          session: 'Unknown',
          timestamp: new Date().toISOString()
        };
      }
    },
    refetchInterval: 60000, // Check every minute
  });
}

export function useMarketQuote(symbol: string) {
  const { toast } = useToast();
  
  return useQuery({
    queryKey: ['market-quote', symbol],
    queryFn: async () => {
      if (!symbol) return null;
      
      try {
        const response = await api.get(`/api/market/quotes/${symbol}`);
        return response.data.data as MarketQuote;
      } catch (error: any) {
        console.error(`Error fetching quote for ${symbol}:`, error);
        return null;
      }
    },
    refetchInterval: 5000, // Poll every 5 seconds for single quotes
    enabled: !!symbol,
  });
}