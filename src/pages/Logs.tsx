import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { FileText, Download, Trash2, RefreshCw, AlertCircle, Info, AlertTriangle } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/api/client";

interface LogEntry {
  timestamp: string;
  level: string;
  module?: string;
  message: string;
  data?: any;
}

interface LogStats {
  [key: string]: {
    size_mb: number;
    modified: string;
    lines: number;
  };
}

export default function Logs() {
  const { toast } = useToast();
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [stats, setStats] = useState<LogStats>({});
  const [loading, setLoading] = useState(false);
  const [selectedLog, setSelectedLog] = useState("main");
  const [selectedLevel, setSelectedLevel] = useState<string | undefined>(undefined);
  const [autoRefresh, setAutoRefresh] = useState(false);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const response = await api.get(`/api/logs?log_type=${selectedLog}&lines=200${selectedLevel ? `&level=${selectedLevel}` : ''}`);
      if (response.data.status === "success") {
        setLogs(response.data.data.logs);
      }
    } catch (error) {
      toast({
        title: "Error fetching logs",
        description: "Failed to retrieve log data",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await api.get('/api/logs/stats');
      if (response.data.status === "success") {
        setStats(response.data.data);
      }
    } catch (error) {
      console.error("Error fetching log stats:", error);
    }
  };

  const handleClearLogs = async (logType: string) => {
    try {
      await api.delete(`/api/logs/clear?log_type=${logType}`);
      toast({
        title: "Logs cleared",
        description: `${logType} logs have been cleared`,
      });
      fetchLogs();
      fetchStats();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to clear logs",
        variant: "destructive",
      });
    }
  };

  useEffect(() => {
    fetchLogs();
    fetchStats();
  }, [selectedLog, selectedLevel]);

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(() => {
        fetchLogs();
      }, 5000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, selectedLog, selectedLevel]);

  const getLevelIcon = (level: string) => {
    switch (level) {
      case "ERROR":
        return <AlertCircle className="h-4 w-4 text-destructive" />;
      case "WARNING":
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      default:
        return <Info className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const getLevelVariant = (level: string): "default" | "destructive" | "secondary" | "outline" => {
    switch (level) {
      case "ERROR":
        return "destructive";
      case "WARNING":
        return "secondary";
      case "DEBUG":
        return "outline";
      default:
        return "default";
    }
  };

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">System Logs</h1>
        <p className="text-muted-foreground">View and manage application logs</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="lg:col-span-1 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Log Files</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Select value={selectedLog} onValueChange={setSelectedLog}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="main">Main Log</SelectItem>
                  <SelectItem value="errors">Errors</SelectItem>
                  <SelectItem value="trading">Trading</SelectItem>
                  <SelectItem value="performance">Performance</SelectItem>
                  <SelectItem value="market">Market Data</SelectItem>
                </SelectContent>
              </Select>

              <Select value={selectedLevel} onValueChange={setSelectedLevel}>
                <SelectTrigger>
                  <SelectValue placeholder="All Levels" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Levels</SelectItem>
                  <SelectItem value="ERROR">Errors Only</SelectItem>
                  <SelectItem value="WARNING">Warnings</SelectItem>
                  <SelectItem value="INFO">Info</SelectItem>
                  <SelectItem value="DEBUG">Debug</SelectItem>
                </SelectContent>
              </Select>

              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Auto-refresh</span>
                <Button
                  variant={autoRefresh ? "default" : "outline"}
                  size="sm"
                  onClick={() => setAutoRefresh(!autoRefresh)}
                >
                  <RefreshCw className={`h-4 w-4 ${autoRefresh ? 'animate-spin' : ''}`} />
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Log Statistics</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {Object.entries(stats).map(([name, stat]) => (
                <div key={name} className="text-sm">
                  <div className="font-medium">{name}</div>
                  <div className="text-muted-foreground">
                    {stat.size_mb} MB • {stat.lines} lines
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          <div className="space-y-2">
            <Button 
              className="w-full" 
              variant="outline"
              onClick={() => fetchLogs()}
              disabled={loading}
            >
              <RefreshCw className="mr-2 h-4 w-4" />
              Refresh
            </Button>
            <Button 
              className="w-full" 
              variant="destructive"
              onClick={() => handleClearLogs(selectedLog)}
            >
              <Trash2 className="mr-2 h-4 w-4" />
              Clear Logs
            </Button>
          </div>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-3">
          <Card className="h-[800px]">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Log Entries</CardTitle>
                <Badge variant="secondary">{logs.length} entries</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[700px] pr-4">
                <div className="space-y-2">
                  {logs.map((log, index) => (
                    <div 
                      key={index} 
                      className="p-3 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
                    >
                      <div className="flex items-start justify-between mb-1">
                        <div className="flex items-center gap-2">
                          {getLevelIcon(log.level)}
                          <Badge variant={getLevelVariant(log.level)} className="text-xs">
                            {log.level}
                          </Badge>
                          {log.module && (
                            <span className="text-xs text-muted-foreground">
                              {log.module}
                            </span>
                          )}
                        </div>
                        <span className="text-xs text-muted-foreground">
                          {new Date(log.timestamp).toLocaleString()}
                        </span>
                      </div>
                      <div className="text-sm mt-1">
                        {log.message}
                      </div>
                      {log.data && (
                        <pre className="text-xs mt-2 p-2 bg-muted rounded overflow-x-auto">
                          {JSON.stringify(log.data, null, 2)}
                        </pre>
                      )}
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}