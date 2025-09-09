import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Search, Play, Pause, RefreshCw, Filter, TrendingUp } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription, SheetFooter } from "@/components/ui/sheet";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useBotStatus, useToggleScanning, useScanOnce } from "@/hooks/useBotControl";
import { useConfig, useUpdateConfig } from "@/hooks/useConfig";
import { useToast } from "@/hooks/use-toast";

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
  const { data: botStatus } = useBotStatus();
  const { data: config } = useConfig();
  const updateConfig = useUpdateConfig();
  const toggleScanning = useToggleScanning();
  const scanOnce = useScanOnce();
  const { toast } = useToast();
  
  const [scanProgress, setScanProgress] = useState(0);
  const [searchTerm, setSearchTerm] = useState("");
  const [showFilters, setShowFilters] = useState(false);
  
  // Filter states
  const [filters, setFilters] = useState({
    min_confidence: 0.75,
    max_price: 1000,
    include_platinum_only: false,
    sectors: "all",
    min_volume: 1000000
  });
  
  const isScanning = botStatus?.scanning || false;
  
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

  // Load filters from config
  useEffect(() => {
    if (config?.scanning?.filters) {
      setFilters(prev => ({ ...prev, ...config.scanning.filters }));
    }
  }, [config]);

  // Progress animation when scanning
  useEffect(() => {
    if (isScanning) {
      const interval = setInterval(() => {
        setScanProgress(prev => {
          if (prev >= 100) return 0;
          return prev + 10;
        });
      }, 500);
      return () => clearInterval(interval);
    } else {
      setScanProgress(0);
    }
  }, [isScanning]);

  const handleScan = () => {
    toggleScanning.mutate();
  };
  
  const handleScanOnce = () => {
    scanOnce.mutate();
  };
  
  const handleSaveFilters = async () => {
    if (config) {
      const updatedConfig = {
        ...config,
        scanning: {
          ...config.scanning,
          filters
        }
      };
      updateConfig.mutate(updatedConfig);
      setShowFilters(false);
      toast({
        title: "Filters saved",
        description: "Scanner filters have been updated",
      });
    }
  };

  const filteredResults = scanResults.filter(result =>
    result.symbol.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-4">
      {/* Scanner Controls */}
      <Card className="p-6 bg-card shadow-card">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Market Scanner</h2>
            <div className="flex gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleScanOnce}
                disabled={isScanning}
              >
                <RefreshCw className="h-4 w-4 mr-1" />
                Scan Once
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="border-border"
                onClick={() => setShowFilters(true)}
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
                    Stop Scanning
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4 mr-1" />
                    Start Scanning
                  </>
                )}
              </Button>
            </div>
          </div>
          
          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search symbols..."
              className="pl-10 bg-secondary border-border"
            />
          </div>
          
          {/* Scan Progress */}
          {isScanning && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Scanning markets...</span>
                <span className="text-primary">{scanProgress}%</span>
              </div>
              <Progress value={scanProgress} className="h-2" />
            </div>
          )}
        </div>
      </Card>
      
      {/* Scan Results */}
      <Card className="p-6 bg-card shadow-card">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">High Potential Movers</h3>
            <Badge variant="secondary" className="bg-primary text-primary-foreground">
              {filteredResults.length} Results
            </Badge>
          </div>
          
          <ScrollArea className="h-[400px]">
            <div className="space-y-3">
              {filteredResults.map((result) => (
                <div key={result.symbol} className="border border-border rounded-lg p-4 hover:bg-card-hover transition-colors">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-lg">{result.symbol}</span>
                        <Badge 
                          variant={result.change > 0 ? "default" : "destructive"}
                          className={result.change > 0 ? "bg-success text-success-foreground" : ""}
                        >
                          {result.change > 0 ? "+" : ""}{result.change}%
                        </Badge>
                      </div>
                      <div className="flex items-center gap-4 mt-1 text-sm text-muted-foreground">
                        <span>${result.price}</span>
                        <span>Vol: {result.volume}</span>
                        <span>Float: {result.float}</span>
                        <span>SI: {result.shortInterest}%</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-medium">
                        Squeeze: {result.squeezePotential}%
                      </div>
                      <div className="text-sm text-muted-foreground">
                        Momentum: {result.momentum}%
                      </div>
                      {result.catalysts > 0 && (
                        <Badge variant="outline" className="mt-1 border-warning text-warning">
                          {result.catalysts} Catalysts
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
        </div>
      </Card>
      
      {/* Scanner Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4 bg-card shadow-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted-foreground text-sm">Symbols Scanned</p>
              <p className="text-2xl font-bold">2,847</p>
            </div>
            <TrendingUp className="h-8 w-8 text-primary opacity-50" />
          </div>
        </Card>
        
        <Card className="p-4 bg-card shadow-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted-foreground text-sm">Potential Squeezes</p>
              <p className="text-2xl font-bold text-warning">12</p>
            </div>
            <TrendingUp className="h-8 w-8 text-warning opacity-50" />
          </div>
        </Card>
        
        <Card className="p-4 bg-card shadow-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted-foreground text-sm">High Momentum</p>
              <p className="text-2xl font-bold text-success">34</p>
            </div>
            <TrendingUp className="h-8 w-8 text-success opacity-50" />
          </div>
        </Card>
        
        <Card className="p-4 bg-card shadow-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted-foreground text-sm">New Catalysts</p>
              <p className="text-2xl font-bold text-primary">8</p>
            </div>
            <TrendingUp className="h-8 w-8 text-primary opacity-50" />
          </div>
        </Card>
      </div>
      
      {/* Filters Sheet */}
      <Sheet open={showFilters} onOpenChange={setShowFilters}>
        <SheetContent>
          <SheetHeader>
            <SheetTitle>Scanner Filters</SheetTitle>
            <SheetDescription>
              Configure market scanning parameters
            </SheetDescription>
          </SheetHeader>
          
          <div className="space-y-6 py-6">
            <div className="space-y-2">
              <Label htmlFor="confidence">Minimum Confidence</Label>
              <div className="flex items-center space-x-4">
                <Slider
                  id="confidence"
                  value={[filters.min_confidence * 100]}
                  onValueChange={(value) => setFilters({ ...filters, min_confidence: value[0] / 100 })}
                  max={100}
                  step={5}
                  className="flex-1"
                />
                <span className="w-12 text-sm text-muted-foreground">
                  {Math.round(filters.min_confidence * 100)}%
                </span>
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="max_price">Maximum Price</Label>
              <Input
                id="max_price"
                type="number"
                value={filters.max_price}
                onChange={(e) => setFilters({ ...filters, max_price: Number(e.target.value) })}
                placeholder="Enter max price..."
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="min_volume">Minimum Volume</Label>
              <Input
                id="min_volume"
                type="number"
                value={filters.min_volume}
                onChange={(e) => setFilters({ ...filters, min_volume: Number(e.target.value) })}
                placeholder="Enter minimum volume..."
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="sectors">Sectors</Label>
              <Select value={filters.sectors} onValueChange={(value) => setFilters({ ...filters, sectors: value })}>
                <SelectTrigger id="sectors">
                  <SelectValue placeholder="Select sectors" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Sectors</SelectItem>
                  <SelectItem value="technology">Technology</SelectItem>
                  <SelectItem value="healthcare">Healthcare</SelectItem>
                  <SelectItem value="finance">Finance</SelectItem>
                  <SelectItem value="energy">Energy</SelectItem>
                  <SelectItem value="consumer">Consumer</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="flex items-center justify-between">
              <Label htmlFor="platinum">Platinum Tier Only</Label>
              <Switch
                id="platinum"
                checked={filters.include_platinum_only}
                onCheckedChange={(checked) => setFilters({ ...filters, include_platinum_only: checked })}
              />
            </div>
          </div>
          
          <SheetFooter>
            <Button variant="outline" onClick={() => setShowFilters(false)}>
              Cancel
            </Button>
            <Button onClick={handleSaveFilters}>
              Save Filters
            </Button>
          </SheetFooter>
        </SheetContent>
      </Sheet>
    </div>
  );
};

export default MarketScanner;