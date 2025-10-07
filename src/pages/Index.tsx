import { Activity, TrendingUp, DollarSign, BarChart3, Shield, Zap, Settings, Database, PlayCircle, StopCircle, FileText } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import MarketScanner from "@/components/MarketScanner";
import SignalsDashboard from "@/components/SignalsDashboard";
import RiskMonitor from "@/components/RiskMonitor";
import PerformanceMetrics from "@/components/PerformanceMetrics";
import ModuleStatus from "@/components/ModuleStatus";
import LiveTicker from "@/components/LiveTicker";
import { Badge } from "@/components/ui/badge";
import { useMarketStatus } from "@/hooks/useMarketData";
import { useBotStatus, useToggleAutoTrade, useToggleScanning } from "@/hooks/useBotControl";
import { LiveSignalsFeed } from "@/components/LiveSignalsFeed";
import { LivePositions } from "@/components/LivePositions";
import { BotControls } from "@/components/BotControls";

const Index = () => {
  const { data: marketStatus } = useMarketStatus();
  const { data: botStatus } = useBotStatus();
  const toggleAutoTrade = useToggleAutoTrade();
  const toggleScanning = useToggleScanning();
  
  const isLive = true;
  const isAutoTrading = botStatus?.auto_trading || false;
  const isScanning = botStatus?.scanning || false;
  
  const marketSession = marketStatus?.session || "REGULAR";

  const handleAutoTrade = () => {
    toggleAutoTrade.mutate();
  };

  const handleScan = () => {
    toggleScanning.mutate();
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-gradient-dark">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Zap className="h-8 w-8 text-primary" />
                <h1 className="text-2xl font-bold bg-gradient-primary bg-clip-text text-transparent">
                  STEALTH Bot
                </h1>
              </div>
              <Badge 
                variant={isLive ? "default" : "secondary"}
                className={isLive ? "bg-success text-success-foreground animate-pulse" : ""}
              >
                <Activity className="h-3 w-3 mr-1" />
                {isLive ? "LIVE" : "PAUSED"}
              </Badge>
              <Badge variant="outline" className="border-primary text-primary">
                {marketSession}
              </Badge>
            </div>
            <div className="flex items-center space-x-4">
              <LiveTicker />
              <Link to="/settings/data-sources">
                <Button variant="outline" size="sm">
                  <Database className="mr-2 h-4 w-4" />
                  Data Sources
                </Button>
              </Link>
              <Link to="/settings/risk">
                <Button variant="outline" size="sm">
                  <Settings className="mr-2 h-4 w-4" />
                  Risk Settings
                </Button>
              </Link>
              <Link to="/logs">
                <Button variant="outline" size="sm">
                  <FileText className="mr-2 h-4 w-4" />
                  View Logs
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Control Panel */}
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-center gap-4">
          <Button
            variant={isAutoTrading ? "destructive" : "default"}
            size="lg"
            onClick={handleAutoTrade}
            className="shadow-glow-primary"
          >
            {isAutoTrading ? <StopCircle className="mr-2 h-4 w-4" /> : <PlayCircle className="mr-2 h-4 w-4" />}
            {isAutoTrading ? "Stop Auto Trade" : "Start Auto Trade"}
          </Button>
          <Button
            variant={isScanning ? "secondary" : "outline"}
            size="lg"
            onClick={handleScan}
          >
            {isScanning ? <StopCircle className="mr-2 h-4 w-4" /> : <PlayCircle className="mr-2 h-4 w-4" />}
            {isScanning ? "Stop Scanning" : "Start Scanning"}
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        {/* Live Controls and Monitoring */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
          <BotControls />
          <LiveSignalsFeed />
          <LivePositions />
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card className="p-4 bg-card hover:bg-card-hover transition-colors shadow-card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-muted-foreground text-sm">Today's Signals</p>
                <p className="text-2xl font-bold text-primary">127</p>
                <p className="text-xs text-success flex items-center mt-1">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  +23.5%
                </p>
              </div>
              <BarChart3 className="h-8 w-8 text-primary opacity-50" />
            </div>
          </Card>

          <Card className="p-4 bg-card hover:bg-card-hover transition-colors shadow-card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-muted-foreground text-sm">Win Rate</p>
                <p className="text-2xl font-bold text-success">68.4%</p>
                <p className="text-xs text-muted-foreground mt-1">Last 30 days</p>
              </div>
              <TrendingUp className="h-8 w-8 text-success opacity-50" />
            </div>
          </Card>

          <Card className="p-4 bg-card hover:bg-card-hover transition-colors shadow-card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-muted-foreground text-sm">Total P&L</p>
                <p className="text-2xl font-bold text-success">+$24,532</p>
                <p className="text-xs text-success flex items-center mt-1">
                  <DollarSign className="h-3 w-3 mr-1" />
                  +12.3%
                </p>
              </div>
              <DollarSign className="h-8 w-8 text-success opacity-50" />
            </div>
          </Card>

          <Card className="p-4 bg-card hover:bg-card-hover transition-colors shadow-card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-muted-foreground text-sm">Risk Score</p>
                <p className="text-2xl font-bold text-warning">Medium</p>
                <p className="text-xs text-muted-foreground mt-1">3.2 / 10</p>
              </div>
              <Shield className="h-8 w-8 text-warning opacity-50" />
            </div>
          </Card>
        </div>

        {/* Main Dashboard Tabs */}
        <Tabs defaultValue="signals" className="space-y-4">
          <TabsList className="bg-secondary border border-border">
            <TabsTrigger value="signals" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
              Signals
            </TabsTrigger>
            <TabsTrigger value="scanner" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
              Market Scanner
            </TabsTrigger>
            <TabsTrigger value="risk" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
              Risk Monitor
            </TabsTrigger>
            <TabsTrigger value="performance" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
              Performance
            </TabsTrigger>
            <TabsTrigger value="modules" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
              Modules
            </TabsTrigger>
          </TabsList>

          <TabsContent value="signals" className="space-y-4">
            <SignalsDashboard />
          </TabsContent>

          <TabsContent value="scanner" className="space-y-4">
            <MarketScanner />
          </TabsContent>

          <TabsContent value="risk" className="space-y-4">
            <RiskMonitor />
          </TabsContent>

          <TabsContent value="performance" className="space-y-4">
            <PerformanceMetrics />
          </TabsContent>

          <TabsContent value="modules" className="space-y-4">
            <ModuleStatus />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default Index;