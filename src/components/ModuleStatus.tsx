import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { ScrollArea } from "@/components/ui/scroll-area";
import { CheckCircle, XCircle, AlertCircle, Settings, RefreshCw, Cpu, Loader2 } from "lucide-react";
import { useModules } from "@/hooks/useModules";
import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { api } from "@/api/client";

const ModuleStatus = () => {
  const { data: modules, isLoading, toggleModule, configureModule, restartModules } = useModules();
  const [configDialog, setConfigDialog] = useState<{ open: boolean; module: any | null }>({ open: false, module: null });
  const [configValues, setConfigValues] = useState<any>({});
  
  const handleToggle = (moduleId: string) => {
    toggleModule.mutate(moduleId);
  };
  
  const handleConfigure = async (moduleId: string) => {
    try {
      const response = await api.getModuleDetails(moduleId);
      const moduleData = response.data.data;
      setConfigValues(moduleData.configuration || {});
      setConfigDialog({ open: true, module: moduleData });
    } catch (error) {
      console.error("Error fetching module details:", error);
    }
  };
  
  const handleSaveConfig = () => {
    if (configDialog.module) {
      configureModule.mutate({ id: configDialog.module.id, config: configValues });
      setConfigDialog({ open: false, module: null });
    }
  };
  
  const handleRestartAll = () => {
    restartModules.mutate();
  };
  
  const getStatusIcon = (status: string) => {
    switch (status) {
      case "running":
        return <CheckCircle className="h-4 w-4 text-success" />;
      case "idle":
        return <AlertCircle className="h-4 w-4 text-warning" />;
      default:
        return <XCircle className="h-4 w-4 text-destructive" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "running":
        return "bg-success text-success-foreground";
      case "idle":
        return "bg-warning text-warning-foreground";
      default:
        return "bg-destructive text-destructive-foreground";
    }
  };

  const getPerformanceColor = (performance: number) => {
    if (performance >= 90) return "text-success";
    if (performance >= 70) return "text-warning";
    return "text-destructive";
  };
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }
  
  const moduleList = modules || [];
  const activeModules = moduleList.filter(m => m.enabled).length;
  const avgPerformance = moduleList.length > 0 
    ? Math.round(moduleList.reduce((acc, m) => acc + m.performance, 0) / moduleList.length)
    : 0;
  const totalErrors = moduleList.reduce((acc, m) => acc + m.errors, 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">System Modules</h2>
          <p className="text-muted-foreground">Monitor and control bot processing modules</p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline" size="sm" onClick={handleRestartAll}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Restart All
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted-foreground text-sm">System Health</p>
              <p className="text-2xl font-bold text-success">Operational</p>
            </div>
            <Cpu className="h-8 w-8 text-success opacity-50" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted-foreground text-sm">Active Modules</p>
              <p className="text-2xl font-bold">{activeModules}/{moduleList.length}</p>
            </div>
            <CheckCircle className="h-8 w-8 text-primary opacity-50" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted-foreground text-sm">Avg Performance</p>
              <p className={`text-2xl font-bold ${getPerformanceColor(avgPerformance)}`}>{avgPerformance}%</p>
            </div>
            <Settings className="h-8 w-8 text-primary opacity-50" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted-foreground text-sm">Total Errors</p>
              <p className={`text-2xl font-bold ${totalErrors > 0 ? 'text-destructive' : 'text-success'}`}>{totalErrors}</p>
            </div>
            <AlertCircle className="h-8 w-8 text-warning opacity-50" />
          </div>
        </Card>
      </div>

      {/* Modules List */}
      <Card>
        <ScrollArea className="h-[500px]">
          <div className="p-6 space-y-4">
            {moduleList.map((module) => (
              <div key={module.id} className="border rounded-lg p-4 hover:bg-card-hover transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4 flex-1">
                    {getStatusIcon(module.status)}
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <h3 className="font-semibold">{module.name}</h3>
                        <Badge className={getStatusColor(module.status)} variant="secondary">
                          {module.status}
                        </Badge>
                      </div>
                      <div className="flex items-center space-x-4 mt-2 text-sm text-muted-foreground">
                        <span className={getPerformanceColor(module.performance)}>
                          Performance: {module.performance}%
                        </span>
                        <span className={module.errors > 0 ? 'text-destructive' : ''}>
                          Errors: {module.errors}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleConfigure(module.id)}
                    >
                      <Settings className="h-4 w-4" />
                    </Button>
                    <Switch
                      checked={module.enabled}
                      onCheckedChange={() => handleToggle(module.id)}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>
      </Card>

      {/* Configuration Dialog */}
      <Dialog open={configDialog.open} onOpenChange={(open) => !open && setConfigDialog({ open: false, module: null })}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Configure {configDialog.module?.name}</DialogTitle>
            <DialogDescription>
              Adjust module settings and parameters
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            {Object.entries(configValues).map(([key, value]) => (
              <div key={key} className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor={key} className="text-right">
                  {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </Label>
                <Input
                  id={key}
                  value={String(value)}
                  onChange={(e) => setConfigValues({ ...configValues, [key]: e.target.value })}
                  className="col-span-3"
                />
              </div>
            ))}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setConfigDialog({ open: false, module: null })}>
              Cancel
            </Button>
            <Button onClick={handleSaveConfig}>Save Changes</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ModuleStatus;