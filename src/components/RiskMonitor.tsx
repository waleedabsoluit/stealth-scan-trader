import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Shield, AlertTriangle, TrendingDown, Activity } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from "recharts";

const RiskMonitor = () => {
  const riskData = [
    { time: "09:00", portfolio: 2.5, market: 3.2, position: 1.8 },
    { time: "10:00", portfolio: 3.1, market: 3.5, position: 2.2 },
    { time: "11:00", portfolio: 2.8, market: 4.1, position: 2.5 },
    { time: "12:00", portfolio: 3.5, market: 4.8, position: 3.1 },
    { time: "13:00", portfolio: 3.2, market: 4.2, position: 2.8 },
    { time: "14:00", portfolio: 2.9, market: 3.8, position: 2.4 },
    { time: "15:00", portfolio: 3.3, market: 4.5, position: 2.9 },
  ];

  const exposureData = [
    { sector: "Technology", exposure: 35, risk: "medium" },
    { sector: "Healthcare", exposure: 20, risk: "low" },
    { sector: "Finance", exposure: 15, risk: "high" },
    { sector: "Energy", exposure: 12, risk: "medium" },
    { sector: "Consumer", exposure: 18, risk: "low" },
  ];

  const getRiskColor = (level: string) => {
    switch (level) {
      case "low": return "text-success";
      case "medium": return "text-warning";
      case "high": return "text-destructive";
      default: return "text-muted-foreground";
    }
  };

  return (
    <div className="space-y-4">
      {/* Risk Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4 bg-card shadow-card">
          <div className="flex items-center justify-between mb-2">
            <Shield className="h-5 w-5 text-primary" />
            <Badge variant="outline" className="text-success border-success">LOW</Badge>
          </div>
          <h3 className="text-sm font-medium text-muted-foreground">Portfolio Risk</h3>
          <p className="text-2xl font-bold">3.2 / 10</p>
          <Progress value={32} className="mt-2 h-2" />
        </Card>

        <Card className="p-4 bg-card shadow-card">
          <div className="flex items-center justify-between mb-2">
            <Activity className="h-5 w-5 text-warning" />
            <Badge variant="outline" className="text-warning border-warning">MEDIUM</Badge>
          </div>
          <h3 className="text-sm font-medium text-muted-foreground">Market Volatility</h3>
          <p className="text-2xl font-bold">VIX: 18.5</p>
          <Progress value={55} className="mt-2 h-2" />
        </Card>

        <Card className="p-4 bg-card shadow-card">
          <div className="flex items-center justify-between mb-2">
            <TrendingDown className="h-5 w-5 text-destructive" />
            <span className="text-xs text-destructive">-2.5%</span>
          </div>
          <h3 className="text-sm font-medium text-muted-foreground">Max Drawdown</h3>
          <p className="text-2xl font-bold">$3,245</p>
          <Progress value={25} className="mt-2 h-2" />
        </Card>

        <Card className="p-4 bg-card shadow-card">
          <div className="flex items-center justify-between mb-2">
            <AlertTriangle className="h-5 w-5 text-warning" />
            <span className="text-xs text-muted-foreground">Active</span>
          </div>
          <h3 className="text-sm font-medium text-muted-foreground">Risk Alerts</h3>
          <p className="text-2xl font-bold">3</p>
          <div className="flex gap-1 mt-2">
            <div className="w-2 h-2 rounded-full bg-destructive animate-pulse" />
            <div className="w-2 h-2 rounded-full bg-warning animate-pulse" />
            <div className="w-2 h-2 rounded-full bg-warning" />
          </div>
        </Card>
      </div>

      {/* Risk Chart */}
      <Card className="p-6 bg-card shadow-card">
        <h3 className="text-lg font-semibold mb-4">Risk Metrics Timeline</h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={riskData}>
            <defs>
              <linearGradient id="portfolioGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.3} />
                <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="marketGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="hsl(var(--warning))" stopOpacity={0.3} />
                <stop offset="95%" stopColor="hsl(var(--warning))" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis dataKey="time" stroke="hsl(var(--muted-foreground))" />
            <YAxis stroke="hsl(var(--muted-foreground))" />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: "hsl(var(--card))", 
                border: "1px solid hsl(var(--border))",
                borderRadius: "var(--radius)"
              }} 
            />
            <Area 
              type="monotone" 
              dataKey="portfolio" 
              stroke="hsl(var(--primary))" 
              fill="url(#portfolioGradient)"
              strokeWidth={2}
            />
            <Area 
              type="monotone" 
              dataKey="market" 
              stroke="hsl(var(--warning))" 
              fill="url(#marketGradient)"
              strokeWidth={2}
            />
            <Line 
              type="monotone" 
              dataKey="position" 
              stroke="hsl(var(--success))" 
              strokeWidth={2}
              dot={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </Card>

      {/* Exposure Breakdown */}
      <Card className="p-6 bg-card shadow-card">
        <h3 className="text-lg font-semibold mb-4">Sector Exposure</h3>
        <div className="space-y-3">
          {exposureData.map((item) => (
            <div key={item.sector} className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium">{item.sector}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-muted-foreground">{item.exposure}%</span>
                    <Badge variant="outline" className={`${getRiskColor(item.risk)} border-current`}>
                      {item.risk.toUpperCase()}
                    </Badge>
                  </div>
                </div>
                <Progress value={item.exposure} className="h-2" />
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Active Alerts */}
      <div className="space-y-2">
        <Alert className="border-warning bg-warning/10">
          <AlertTriangle className="h-4 w-4 text-warning" />
          <AlertDescription className="text-warning">
            <strong>Position Size Warning:</strong> NVDA position exceeds 15% of portfolio allocation
          </AlertDescription>
        </Alert>
        <Alert className="border-destructive bg-destructive/10">
          <AlertTriangle className="h-4 w-4 text-destructive" />
          <AlertDescription className="text-destructive">
            <strong>Volatility Alert:</strong> Market volatility increased 35% in the last hour
          </AlertDescription>
        </Alert>
      </div>
    </div>
  );
};

export default RiskMonitor;