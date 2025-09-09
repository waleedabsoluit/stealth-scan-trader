/**
 * Hook for managing configuration
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/api/client';
import { useToast } from '@/hooks/use-toast';

export interface Config {
  trading: {
    min_confidence: number;
    max_positions: number;
    default_position_size: number;
    max_position_size: number;
    risk_per_trade: number;
  };
  scanning: {
    universe_size: number;
    scan_interval: number;
    market_sessions: {
      premarket: boolean;
      regular: boolean;
      afterhours: boolean;
    };
  };
  modules: Record<string, any>;
  integrations?: {
    market_data?: {
      provider: string;
      api_key?: string;
      universe?: string[];
      websocket?: boolean;
    };
  };
}

export function useConfig() {
  const { toast } = useToast();
  
  return useQuery({
    queryKey: ['config'],
    queryFn: async () => {
      try {
        const response = await api.getConfig();
        return response.data.data as Config;
      } catch (error: any) {
        toast({
          title: "Error fetching configuration",
          description: error.message || "Failed to fetch config",
          variant: "destructive",
        });
        throw error;
      }
    },
  });
}

export function useUpdateConfig() {
  const queryClient = useQueryClient();
  const { toast } = useToast();
  
  return useMutation({
    mutationFn: async (config: Config) => {
      const response = await api.updateConfig(config);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['config'] });
      toast({
        title: "Configuration updated",
        description: "Settings have been saved successfully",
      });
    },
    onError: (error: any) => {
      toast({
        title: "Failed to update configuration",
        description: error.message || "An error occurred",
        variant: "destructive",
      });
    },
  });
}