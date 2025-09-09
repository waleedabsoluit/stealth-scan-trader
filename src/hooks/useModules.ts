/**
 * Hook for managing bot modules
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/api/client';
import { useToast } from '@/hooks/use-toast';

export interface Module {
  id: string;
  name: string;
  status: string;
  enabled: boolean;
  performance: number;
  errors: number;
}

export function useModules() {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  
  const query = useQuery({
    queryKey: ['modules'],
    queryFn: async () => {
      try {
        const response = await api.getModules();
        return response.data.data as Module[];
      } catch (error: any) {
        toast({
          title: "Error fetching modules",
          description: error.message || "Failed to fetch module status",
          variant: "destructive",
        });
        throw error;
      }
    },
    refetchInterval: 30000,
  });
  
  const toggleModule = useMutation({
    mutationFn: async (moduleName: string) => {
      const response = await api.toggleModule(moduleName);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['modules'] });
      toast({
        title: "Module updated",
        description: "Module status has been changed",
      });
    },
    onError: (error: any) => {
      toast({
        title: "Error toggling module",
        description: error.message || "Failed to update module",
        variant: "destructive",
      });
    },
  });
  
  const configureModule = useMutation({
    mutationFn: async ({ id, config }: { id: string; config: any }) => {
      const response = await api.configureModule(id, config);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['modules'] });
      toast({
        title: "Configuration updated",
        description: "Module configuration has been saved",
      });
    },
    onError: (error: any) => {
      toast({
        title: "Error updating configuration",
        description: error.message || "Failed to update configuration",
        variant: "destructive",
      });
    },
  });
  
  const restartModules = useMutation({
    mutationFn: async () => {
      const response = await api.restartModules();
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['modules'] });
      toast({
        title: "Modules restarted",
        description: "All modules have been restarted successfully",
      });
    },
    onError: (error: any) => {
      toast({
        title: "Error restarting modules",
        description: error.message || "Failed to restart modules",
        variant: "destructive",
      });
    },
  });
  
  return {
    ...query,
    toggleModule,
    configureModule,
    restartModules,
  };
}