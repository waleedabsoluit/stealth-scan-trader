import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Search, Play, Pause, RefreshCw, Filter, TrendingUp } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";

interface ScanResult {
  symbol: string;
  price: number;
  volume: string;
  change: number;
  float: string;
  shortInterest: number;
  squeezePotential: number;
  momentum: number;
  catalysts: number;
}

const MarketScanner = () => {
  const [isScanning, setIsScanning] = useState(false);
  const [scanProgress, setScanProgress] = useState(0);
  const [searchTerm, setSearchTerm] = useState("");
  
  const [scanResults] = useState<ScanResult[]>([
    {
      symbol: "GME",
      price: 25.43,
      volume: "45.2M",
      change: 12.5,
      float: "65M",
      shortInterest: 24.5,
      squeezePotential: 85,
      momentum: 92,
      catalysts: 3
    },
    {
      symbol: "AMC",
      price: 5.67,
      volume: "89.3M",
      change: 8.2,
      float: "520M",
      shortInterest: 18.3,
      squeezePotential: 72,
      momentum: 78,
      catalysts: 2
    },
    {
      symbol: "BBBY",
      price: 0.89,
      volume: "125M",
      change: 45.2,
      float: "117M",
      shortInterest: 35.2,
      squeezePotential: 95,
      momentum: 88,
      catalysts: 5
    }
  ]);

  const handleScan = () => {
    setIsScanning(!isScanning);
    if (!isScanning) {
      let progress = 0;
      const interval = setInterval(() => {
        progress += 10;
        setScanProgress(progress);
        if (progress >= 100) {
          clearInterval(interval);
          setIsScanning(false);
        }
      }, 500);
    }
  };

  return (
    <div className="space-y-4">
      {/* Scanner Controls */}
      <Card className="p-6 bg-card shadow-card">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Market Scanner</h2>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                className="border-border"
              >
                <Filter className="h-4 w-4 mr-1" />
                Filters
              </Button>
              <Button
                onClick={handleScan}
                size="sm"
                className={isScanning ? "bg-destructive text-destructive-foreground" : "bg-gradient-primary text-primary-foreground shadow-glow-primary"}
              >
                {isScanning ? (
                  <>
                    <Pause className="h-4 w-4 mr-1" />
                    Stop
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4 mr-1" />
                    Scan
                  </>
                )}
              </Button>
            </div>
          </div>

          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search symbols..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 bg-input border-border"
            />
          </div>

          {/* Scan Progress */}
          {isScanning && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Scanning universe...</span>
                <span className="text-primary">{scanProgress}%</span>
              </div>
              <Progress value={scanProgress} className="h-2" />
            </div>
          )}
        </div>
      </Card>

      {/* Scan Results */}
      <Card className="bg-card shadow-card">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">High Potential Movers</h3>
            <Button variant="ghost" size="sm">
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>

          <ScrollArea className="h-[400px]">
            <div className="space-y-3">
              {scanResults.map((result) => (
                <Card key={result.symbol} className="p-4 bg-secondary hover:bg-card-hover transition-all hover:shadow-glow-primary cursor-pointer">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-lg font-bold">{result.symbol}</span>
                          <Badge variant={result.change > 10 ? "default" : "secondary"} className={result.change > 10 ? "bg-success text-success-foreground" : ""}>
                            <TrendingUp className="h-3 w-3 mr-1" />
                            {result.change > 0 ? "+" : ""}{result.change}%
                          </Badge>
                        </div>
                        <div className="flex items-center gap-4 mt-1 text-sm text-muted-foreground">
                          <span>${result.price}</span>
                          <span>Vol: {result.volume}</span>
                          <span>Float: {result.float}</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex flex-col items-end gap-2">
                      <div className="flex gap-2">
                        <div className="text-right">
                          <p className="text-xs text-muted-foreground">Squeeze</p>
                          <div className="flex items-center gap-1">
                            <Progress value={result.squeezePotential} className="w-16 h-2" />
                            <span className="text-xs font-medium">{result.squeezePotential}%</span>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-xs text-muted-foreground">Momentum</p>
                          <div className="flex items-center gap-1">
                            <Progress value={result.momentum} className="w-16 h-2" />
                            <span className="text-xs font-medium">{result.momentum}%</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 text-xs">
                        <Badge variant="outline" className="border-warning text-warning">
                          SI: {result.shortInterest}%
                        </Badge>
                        <Badge variant="outline" className="border-primary text-primary">
                          {result.catalysts} catalysts
                        </Badge>
                      </div>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </ScrollArea>
        </div>
      </Card>

      {/* Scanner Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4 bg-card shadow-card">
          <h3 className="text-sm font-medium text-muted-foreground mb-2">Symbols Scanned</h3>
          <p className="text-2xl font-bold">8,452</p>
        </Card>
        <Card className="p-4 bg-card shadow-card">
          <h3 className="text-sm font-medium text-muted-foreground mb-2">Potential Squeezes</h3>
          <p className="text-2xl font-bold text-warning">12</p>
        </Card>
        <Card className="p-4 bg-card shadow-card">
          <h3 className="text-sm font-medium text-muted-foreground mb-2">High Momentum</h3>
          <p className="text-2xl font-bold text-success">34</p>
        </Card>
        <Card className="p-4 bg-card shadow-card">
          <h3 className="text-sm font-medium text-muted-foreground mb-2">New Catalysts</h3>
          <p className="text-2xl font-bold text-primary">67</p>
        </Card>
      </div>
    </div>
  );
};

export default MarketScanner;