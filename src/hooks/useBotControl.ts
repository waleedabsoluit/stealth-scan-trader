/**
 * Hook for bot control operations
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/api/client';
import { useToast } from '@/hooks/use-toast';

export interface BotStatus {
  auto_trading: boolean;
  scanning: boolean;
  last_action_at: string;
  scan_count: number;
  trade_count: number;
}

export function useBotStatus() {
  return useQuery({
    queryKey: ['bot-status'],
    queryFn: async () => {
      const response = await api.bot.getStatus();
      return response.data.data as BotStatus;
    },
    refetchInterval: 3000, // Refresh every 3 seconds
  });
}

export function useToggleAutoTrade() {
  const queryClient = useQueryClient();
  const { toast } = useToast();
  
  return useMutation({
    mutationFn: async () => {
      const response = await api.bot.toggleAutoTrade();
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['bot-status'] });
      toast({
        title: "Auto Trading Updated",
        description: data.data.message,
      });
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to toggle auto trading",
        variant: "destructive",
      });
    },
  });
}

export function useToggleScanning() {
  const queryClient = useQueryClient();
  const { toast } = useToast();
  
  return useMutation({
    mutationFn: async () => {
      const response = await api.bot.toggleScanning();
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['bot-status'] });
      toast({
        title: "Market Scanning Updated",
        description: data.data.message,
      });
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to toggle scanning",
        variant: "destructive",
      });
    },
  });
}

export function useScanOnce() {
  const { toast } = useToast();
  
  return useMutation({
    mutationFn: async () => {
      const response = await api.bot.scanOnce();
      return response.data;
    },
    onSuccess: (data) => {
      const results = data.data;
      toast({
        title: "Scan Complete",
        description: `Found ${results.results_count} opportunities. Top pick: ${results.top_opportunities[0]?.symbol || 'None'}`,
      });
    },
    onError: (error: any) => {
      toast({
        title: "Scan Failed",
        description: error.message || "Failed to run scan",
        variant: "destructive",
      });
    },
  });
}

export function useResetBot() {
  const queryClient = useQueryClient();
  const { toast } = useToast();
  
  return useMutation({
    mutationFn: async () => {
      const response = await api.bot.reset();
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['bot-status'] });
      toast({
        title: "Bot Reset",
        description: data.data.message,
      });
    },
    onError: (error: any) => {
      toast({
        title: "Reset Failed",
        description: error.message || "Failed to reset bot",
        variant: "destructive",
      });
    },
  });
}