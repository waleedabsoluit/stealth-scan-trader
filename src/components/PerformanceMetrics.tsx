import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { TrendingUp, TrendingDown, DollarSign, Percent, BarChart3 } from "lucide-react";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";

const PerformanceMetrics = () => {
  const dailyPnL = [
    { date: "Mon", profit: 2450, loss: -890, net: 1560 },
    { date: "Tue", profit: 3200, loss: -1200, net: 2000 },
    { date: "Wed", profit: 1800, loss: -2100, net: -300 },
    { date: "Thu", profit: 4500, loss: -1500, net: 3000 },
    { date: "Fri", profit: 3800, loss: -900, net: 2900 },
  ];

  const winRateData = [
    { name: "Wins", value: 68, color: "hsl(var(--success))" },
    { name: "Losses", value: 32, color: "hsl(var(--destructive))" },
  ];

  const tierPerformance = [
    { tier: "PLATINUM", winRate: 92, avgReturn: 8.5, trades: 24 },
    { tier: "GOLD", winRate: 78, avgReturn: 5.2, trades: 45 },
    { tier: "SILVER", winRate: 65, avgReturn: 3.1, trades: 89 },
    { tier: "BRONZE", winRate: 52, avgReturn: 1.8, trades: 142 },
  ];

  const monthlyReturns = [
    { month: "Jan", return: 12.5 },
    { month: "Feb", return: 8.3 },
    { month: "Mar", return: -2.1 },
    { month: "Apr", return: 15.7 },
    { month: "May", return: 10.2 },
    { month: "Jun", return: 7.8 },
  ];

  return (
    <div className="space-y-4">
      {/* Performance Summary */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card className="p-4 bg-card shadow-card">
          <div className="flex items-center justify-between mb-2">
            <DollarSign className="h-5 w-5 text-success" />
            <Badge variant="outline" className="text-success border-success">+12.3%</Badge>
          </div>
          <h3 className="text-sm font-medium text-muted-foreground">Total P&L</h3>
          <p className="text-2xl font-bold text-success">+$24,532</p>
        </Card>

        <Card className="p-4 bg-card shadow-card">
          <div className="flex items-center justify-between mb-2">
            <Percent className="h-5 w-5 text-primary" />
            <TrendingUp className="h-4 w-4 text-success" />
          </div>
          <h3 className="text-sm font-medium text-muted-foreground">Win Rate</h3>
          <p className="text-2xl font-bold">68.4%</p>
        </Card>

        <Card className="p-4 bg-card shadow-card">
          <div className="flex items-center justify-between mb-2">
            <BarChart3 className="h-5 w-5 text-warning" />
            <span className="text-xs text-muted-foreground">1.85</span>
          </div>
          <h3 className="text-sm font-medium text-muted-foreground">Sharpe Ratio</h3>
          <p className="text-2xl font-bold">1.85</p>
        </Card>

        <Card className="p-4 bg-card shadow-card">
          <div className="flex items-center justify-between mb-2">
            <TrendingDown className="h-5 w-5 text-destructive" />
            <span className="text-xs text-destructive">-5.2%</span>
          </div>
          <h3 className="text-sm font-medium text-muted-foreground">Max Drawdown</h3>
          <p className="text-2xl font-bold">$4,250</p>
        </Card>

        <Card className="p-4 bg-card shadow-card">
          <div className="flex items-center justify-between mb-2">
            <DollarSign className="h-5 w-5 text-primary" />
            <Badge variant="outline">300</Badge>
          </div>
          <h3 className="text-sm font-medium text-muted-foreground">Total Trades</h3>
          <p className="text-2xl font-bold">300</p>
        </Card>
      </div>

      {/* Charts */}
      <Tabs defaultValue="pnl" className="space-y-4">
        <TabsList className="bg-secondary border border-border">
          <TabsTrigger value="pnl">P&L Analysis</TabsTrigger>
          <TabsTrigger value="winrate">Win Rate</TabsTrigger>
          <TabsTrigger value="tiers">Tier Performance</TabsTrigger>
          <TabsTrigger value="monthly">Monthly Returns</TabsTrigger>
        </TabsList>

        <TabsContent value="pnl">
          <Card className="p-6 bg-card shadow-card">
            <h3 className="text-lg font-semibold mb-4">Daily P&L Breakdown</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={dailyPnL}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="date" stroke="hsl(var(--muted-foreground))" />
                <YAxis stroke="hsl(var(--muted-foreground))" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: "hsl(var(--card))", 
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "var(--radius)"
                  }} 
                />
                <Bar dataKey="profit" fill="hsl(var(--success))" />
                <Bar dataKey="loss" fill="hsl(var(--destructive))" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </TabsContent>

        <TabsContent value="winrate">
          <Card className="p-6 bg-card shadow-card">
            <h3 className="text-lg font-semibold mb-4">Win/Loss Distribution</h3>
            <div className="flex items-center justify-around">
              <ResponsiveContainer width="50%" height={300}>
                <PieChart>
                  <Pie
                    data={winRateData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {winRateData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-muted-foreground">Win Rate</p>
                  <p className="text-3xl font-bold text-success">68.4%</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Avg Win</p>
                  <p className="text-2xl font-bold">+$425</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Avg Loss</p>
                  <p className="text-2xl font-bold text-destructive">-$185</p>
                </div>
              </div>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="tiers">
          <Card className="p-6 bg-card shadow-card">
            <h3 className="text-lg font-semibold mb-4">Performance by Signal Tier</h3>
            <div className="space-y-4">
              {tierPerformance.map((tier) => (
                <div key={tier.tier} className="flex items-center justify-between p-4 rounded-lg bg-secondary">
                  <div className="flex items-center gap-4">
                    <Badge className={
                      tier.tier === "PLATINUM" ? "bg-gradient-accent text-accent-foreground" :
                      tier.tier === "GOLD" ? "bg-warning text-warning-foreground" :
                      tier.tier === "SILVER" ? "bg-muted text-foreground" :
                      "bg-secondary text-secondary-foreground"
                    }>
                      {tier.tier}
                    </Badge>
                    <div>
                      <p className="text-sm text-muted-foreground">{tier.trades} trades</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-8">
                    <div className="text-right">
                      <p className="text-xs text-muted-foreground">Win Rate</p>
                      <p className="text-lg font-bold text-success">{tier.winRate}%</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-muted-foreground">Avg Return</p>
                      <p className="text-lg font-bold">+{tier.avgReturn}%</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="monthly">
          <Card className="p-6 bg-card shadow-card">
            <h3 className="text-lg font-semibold mb-4">Monthly Returns</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={monthlyReturns}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="month" stroke="hsl(var(--muted-foreground))" />
                <YAxis stroke="hsl(var(--muted-foreground))" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: "hsl(var(--card))", 
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "var(--radius)"
                  }} 
                />
                <Line 
                  type="monotone" 
                  dataKey="return" 
                  stroke="hsl(var(--primary))" 
                  strokeWidth={3}
                  dot={{ fill: "hsl(var(--primary))", strokeWidth: 2, r: 6 }}
                  activeDot={{ r: 8 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default PerformanceMetrics;