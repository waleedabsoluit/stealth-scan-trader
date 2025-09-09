import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { ScrollArea } from "@/components/ui/scroll-area";
import { CheckCircle, XCircle, AlertCircle, Settings, RefreshCw, Cpu } from "lucide-react";

interface Module {
  name: string;
  description: string;
  status: "active" | "inactive" | "error";
  enabled: boolean;
  lastRun: string;
  performance: number;
  errors: number;
}

const ModuleStatus = () => {
  const modules: Module[] = [
    {
      name: "OBV VWAP Engine",
      description: "Computes OBV slope and VWAP distance for momentum analysis",
      status: "active",
      enabled: true,
      lastRun: "2 min ago",
      performance: 98,
      errors: 0
    },
    {
      name: "Float Churn Analyzer",
      description: "Estimates float turnover rate and liquidity metrics",
      status: "active",
      enabled: true,
      lastRun: "1 min ago",
      performance: 95,
      errors: 0
    },
    {
      name: "Dilution Detector",
      description: "Flags dilution risk from shelf/ATM activity",
      status: "active",
      enabled: true,
      lastRun: "3 min ago",
      performance: 92,
      errors: 2
    },
    {
      name: "Orderbook Imbalance",
      description: "Tracks dark pool and iceberg order pressure",
      status: "active",
      enabled: true,
      lastRun: "30 sec ago",
      performance: 100,
      errors: 0
    },
    {
      name: "Squeeze Scanner",
      description: "Identifies short squeeze potential setups",
      status: "active",
      enabled: true,
      lastRun: "1 min ago",
      performance: 88,
      errors: 0
    },
    {
      name: "Pattern Scorer",
      description: "Technical pattern recognition and scoring",
      status: "error",
      enabled: false,
      lastRun: "15 min ago",
      performance: 0,
      errors: 5
    },
    {
      name: "Rumor Hype Flagger",
      description: "Filters out rumor-driven price spikes",
      status: "active",
      enabled: true,
      lastRun: "2 min ago",
      performance: 91,
      errors: 1
    },
    {
      name: "Catalyst Latency",
      description: "Measures time since last material news",
      status: "active",
      enabled: true,
      lastRun: "5 min ago",
      performance: 85,
      errors: 0
    },
    {
      name: "Cross Sync Guard",
      description: "Ensures multi-indicator alignment",
      status: "active",
      enabled: true,
      lastRun: "1 min ago",
      performance: 96,
      errors: 0
    },
    {
      name: "Confidence Scorer",
      description: "Aggregates subscores into confidence percentage",
      status: "active",
      enabled: true,
      lastRun: "30 sec ago",
      performance: 99,
      errors: 0
    },
    {
      name: "Stealth Builder Tracker",
      description: "Detects gradual accumulation patterns",
      status: "inactive",
      enabled: false,
      lastRun: "1 hour ago",
      performance: 75,
      errors: 0
    },
    {
      name: "Platinum Gatekeeper",
      description: "Strict risk gate for top-tier signals",
      status: "active",
      enabled: true,
      lastRun: "1 min ago",
      performance: 100,
      errors: 0
    }
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "active":
        return <CheckCircle className="h-4 w-4 text-success" />;
      case "inactive":
        return <XCircle className="h-4 w-4 text-muted-foreground" />;
      case "error":
        return <AlertCircle className="h-4 w-4 text-destructive" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "border-success text-success";
      case "inactive":
        return "border-muted text-muted-foreground";
      case "error":
        return "border-destructive text-destructive";
      default:
        return "";
    }
  };

  const getPerformanceColor = (performance: number) => {
    if (performance >= 90) return "text-success";
    if (performance >= 70) return "text-warning";
    return "text-destructive";
  };

  return (
    <div className="space-y-4">
      {/* Module Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4 bg-card shadow-card">
          <div className="flex items-center justify-between mb-2">
            <Cpu className="h-5 w-5 text-primary" />
            <Badge variant="outline" className="text-success border-success">HEALTHY</Badge>
          </div>
          <h3 className="text-sm font-medium text-muted-foreground">System Status</h3>
          <p className="text-2xl font-bold">12 / 15</p>
          <p className="text-xs text-muted-foreground mt-1">modules active</p>
        </Card>

        <Card className="p-4 bg-card shadow-card">
          <h3 className="text-sm font-medium text-muted-foreground mb-2">Avg Performance</h3>
          <p className="text-2xl font-bold text-success">94.2%</p>
          <p className="text-xs text-muted-foreground mt-1">efficiency rating</p>
        </Card>

        <Card className="p-4 bg-card shadow-card">
          <h3 className="text-sm font-medium text-muted-foreground mb-2">Total Errors</h3>
          <p className="text-2xl font-bold text-warning">8</p>
          <p className="text-xs text-muted-foreground mt-1">last 24 hours</p>
        </Card>

        <Card className="p-4 bg-card shadow-card">
          <h3 className="text-sm font-medium text-muted-foreground mb-2">Last Update</h3>
          <p className="text-2xl font-bold">30s</p>
          <p className="text-xs text-success mt-1">all systems synced</p>
        </Card>
      </div>

      {/* Module Controls */}
      <Card className="p-6 bg-card shadow-card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Module Management</h2>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" className="border-border">
              <Settings className="h-4 w-4 mr-1" />
              Configure
            </Button>
            <Button size="sm" className="bg-gradient-primary text-primary-foreground shadow-glow-primary">
              <RefreshCw className="h-4 w-4 mr-1" />
              Restart All
            </Button>
          </div>
        </div>

        <ScrollArea className="h-[500px]">
          <div className="space-y-3">
            {modules.map((module) => (
              <Card key={module.name} className="p-4 bg-secondary hover:bg-card-hover transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      {getStatusIcon(module.status)}
                      <h3 className="font-medium">{module.name}</h3>
                      <Badge variant="outline" className={getStatusColor(module.status)}>
                        {module.status.toUpperCase()}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">{module.description}</p>
                    <div className="flex items-center gap-4 text-xs">
                      <span className="text-muted-foreground">Last run: {module.lastRun}</span>
                      <span className={getPerformanceColor(module.performance)}>
                        Performance: {module.performance}%
                      </span>
                      {module.errors > 0 && (
                        <span className="text-destructive">Errors: {module.errors}</span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <Switch
                      checked={module.enabled}
                      className="data-[state=checked]:bg-primary"
                    />
                    <Button variant="ghost" size="sm">
                      <Settings className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                </Card>
              ))}
          </div>
        </ScrollArea>
      </Card>
    </div>
  );
};

export default ModuleStatus;