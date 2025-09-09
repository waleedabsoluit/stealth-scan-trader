import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ArrowUp, ArrowDown, Clock, DollarSign, AlertTriangle, CheckCircle, XCircle } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

interface Signal {
  id: string;
  symbol: string;
  tier: "PLATINUM" | "GOLD" | "SILVER" | "BRONZE";
  confidence: number;
  entry: number;
  current: number;
  change: number;
  volume: string;
  obvSlope: number;
  vwapDistance: number;
  timestamp: string;
  status: "ACTIVE" | "CLOSED" | "PENDING";
}

const SignalsDashboard = () => {
  const [signals] = useState<Signal[]>([
    {
      id: "1",
      symbol: "NVDA",
      tier: "PLATINUM",
      confidence: 92,
      entry: 850.25,
      current: 868.40,
      change: 2.13,
      volume: "125M",
      obvSlope: 0.82,
      vwapDistance: 1.2,
      timestamp: "09:45:23",
      status: "ACTIVE"
    },
    {
      id: "2",
      symbol: "TSLA",
      tier: "GOLD",
      confidence: 78,
      entry: 242.10,
      current: 238.95,
      change: -1.30,
      volume: "89M",
      obvSlope: 0.65,
      vwapDistance: -0.8,
      timestamp: "10:12:45",
      status: "ACTIVE"
    },
    {
      id: "3",
      symbol: "AMD",
      tier: "PLATINUM",
      confidence: 88,
      entry: 165.50,
      current: 172.35,
      change: 4.14,
      volume: "95M",
      obvSlope: 0.91,
      vwapDistance: 2.1,
      timestamp: "10:35:12",
      status: "ACTIVE"
    },
    {
      id: "4",
      symbol: "AAPL",
      tier: "SILVER",
      confidence: 65,
      entry: 195.25,
      current: 196.10,
      change: 0.44,
      volume: "75M",
      obvSlope: 0.45,
      vwapDistance: 0.3,
      timestamp: "11:02:34",
      status: "PENDING"
    }
  ]);

  const handleExecute = async (signalId: string) => {
    try {
      await api.post(`/api/signals/${signalId}/execute`);
      toast({
        title: "Signal executed",
        description: "Trade order has been placed",
      });
    } catch (error) {
      toast({
        title: "Execution failed",
        description: "Failed to execute signal",
        variant: "destructive",
      });
    }
  };

  const getTierColor = (tier: string) => {
    switch (tier) {
      case "PLATINUM": return "bg-gradient-accent text-accent-foreground";
      case "GOLD": return "bg-warning text-warning-foreground";
      case "SILVER": return "bg-muted text-foreground";
      case "BRONZE": return "bg-secondary text-secondary-foreground";
      default: return "bg-secondary";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "ACTIVE": return <CheckCircle className="h-4 w-4 text-success" />;
      case "CLOSED": return <XCircle className="h-4 w-4 text-muted-foreground" />;
      case "PENDING": return <Clock className="h-4 w-4 text-warning" />;
      default: return null;
    }
  };

  return (
    <div className="space-y-4">
      <Card className="bg-card shadow-card">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Active Signals</h2>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" className="border-primary text-primary hover:bg-primary hover:text-primary-foreground">
                <AlertTriangle className="h-4 w-4 mr-1" />
                Risk Settings
              </Button>
              <Button size="sm" className="bg-gradient-primary text-primary-foreground shadow-glow-primary">
                Auto Trade
              </Button>
            </div>
          </div>

          <ScrollArea className="h-[400px]">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Symbol</TableHead>
                  <TableHead>Tier</TableHead>
                  <TableHead>Confidence</TableHead>
                  <TableHead>Entry</TableHead>
                  <TableHead>Current</TableHead>
                  <TableHead>Change %</TableHead>
                  <TableHead>Volume</TableHead>
                  <TableHead>OBV Slope</TableHead>
                  <TableHead>VWAP Dist</TableHead>
                  <TableHead>Time</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {signals.map((signal) => (
                  <TableRow key={signal.id} className="hover:bg-card-hover transition-colors">
                    <TableCell className="font-medium">{signal.symbol}</TableCell>
                    <TableCell>
                      <Badge className={getTierColor(signal.tier)}>
                        {signal.tier}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <span className={signal.confidence > 80 ? "text-success" : signal.confidence > 60 ? "text-warning" : "text-destructive"}>
                          {signal.confidence}%
                        </span>
                      </div>
                    </TableCell>
                    <TableCell>${signal.entry.toFixed(2)}</TableCell>
                    <TableCell>${signal.current.toFixed(2)}</TableCell>
                    <TableCell>
                      <div className={`flex items-center gap-1 ${signal.change >= 0 ? "text-success" : "text-destructive"}`}>
                        {signal.change >= 0 ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />}
                        {Math.abs(signal.change).toFixed(2)}%
                      </div>
                    </TableCell>
                    <TableCell>{signal.volume}</TableCell>
                    <TableCell>
                      <span className={signal.obvSlope > 0.7 ? "text-success" : "text-warning"}>
                        {signal.obvSlope.toFixed(2)}
                      </span>
                    </TableCell>
                    <TableCell>
                      <span className={signal.vwapDistance > 0 ? "text-success" : "text-destructive"}>
                        {signal.vwapDistance.toFixed(1)}%
                      </span>
                    </TableCell>
                    <TableCell className="text-muted-foreground">{signal.timestamp}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        {getStatusIcon(signal.status)}
                        <span className="text-xs">{signal.status}</span>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </ScrollArea>
        </div>
      </Card>

      {/* Signal Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4 bg-card shadow-card">
          <h3 className="text-sm font-medium text-muted-foreground mb-2">Platinum Signals</h3>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-accent">2</span>
            <span className="text-xs text-success">+100% win rate</span>
          </div>
        </Card>
        <Card className="p-4 bg-card shadow-card">
          <h3 className="text-sm font-medium text-muted-foreground mb-2">Average Confidence</h3>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-primary">80.75%</span>
            <span className="text-xs text-muted-foreground">Last hour</span>
          </div>
        </Card>
        <Card className="p-4 bg-card shadow-card">
          <h3 className="text-sm font-medium text-muted-foreground mb-2">Active Positions</h3>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold">3</span>
            <span className="text-xs text-success">$2,845 profit</span>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default SignalsDashboard;