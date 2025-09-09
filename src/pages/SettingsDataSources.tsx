import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Loader2, CheckCircle, XCircle, Database, AlertCircle, Plus, X } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/api/client";

const DEFAULT_SYMBOLS = [
  "SPY", "QQQ", "AAPL", "MSFT", "NVDA", "TSLA", "AMD", "META", "GOOGL", "AMZN",
  "NFLX", "DIS", "BA", "JPM", "GS", "V", "MA", "PYPL", "SQ", "COIN"
];

const SettingsDataSources = () => {
  const { toast } = useToast();
  const [provider, setProvider] = useState("yahoo");
  const [apiKey, setApiKey] = useState("");
  const [universe, setUniverse] = useState<string[]>(DEFAULT_SYMBOLS);
  const [newSymbol, setNewSymbol] = useState("");
  const [isTestingConnection, setIsTestingConnection] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<"idle" | "testing" | "success" | "error">("idle");
  const [testResult, setTestResult] = useState<any>(null);

  // Load current config on mount
  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      const response = await api.getConfig();
      const config = response.data.data;
      if (config?.integrations?.market_data) {
        setProvider(config.integrations.market_data.provider || "yahoo");
        setApiKey(config.integrations.market_data.api_key || "");
        setUniverse(config.integrations.market_data.universe || DEFAULT_SYMBOLS);
      }
    } catch (error) {
      console.error("Failed to load config:", error);
    }
  };

  const handleTestConnection = async () => {
    setIsTestingConnection(true);
    setConnectionStatus("testing");
    setTestResult(null);

    try {
      const response = await api.post("/api/market/test", {
        provider,
        api_key: apiKey,
        universe: universe.slice(0, 5) // Test with first 5 symbols
      });

      if (response.data.connected) {
        setConnectionStatus("success");
        setTestResult(response.data);
        toast({
          title: "Connection successful",
          description: "Market data provider is connected and working",
        });
      } else {
        setConnectionStatus("error");
        toast({
          title: "Connection failed",
          description: response.data.error || "Unable to connect to market data provider",
          variant: "destructive",
        });
      }
    } catch (error: any) {
      setConnectionStatus("error");
      toast({
        title: "Connection test failed",
        description: error.message || "Failed to test connection",
        variant: "destructive",
      });
    } finally {
      setIsTestingConnection(false);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);

    try {
      // Configure market data provider
      const response = await api.post("/api/market/configure", {
        provider,
        api_key: apiKey,
        universe
      });

      if (response.data.status === "success") {
        // Update main config
        const configResponse = await api.getConfig();
        const config = configResponse.data.data;
        
        config.integrations = config.integrations || {};
        config.integrations.market_data = {
          provider,
          api_key: apiKey,
          universe,
          websocket: false
        };

        await api.updateConfig(config);

        toast({
          title: "Settings saved",
          description: "Market data provider configured successfully",
        });
      }
    } catch (error: any) {
      toast({
        title: "Failed to save settings",
        description: error.message || "An error occurred while saving",
        variant: "destructive",
      });
    } finally {
      setIsSaving(false);
    }
  };

  const handleAddSymbol = () => {
    const symbol = newSymbol.trim().toUpperCase();
    if (symbol && !universe.includes(symbol)) {
      setUniverse([...universe, symbol]);
      setNewSymbol("");
    }
  };

  const handleRemoveSymbol = (symbol: string) => {
    setUniverse(universe.filter(s => s !== symbol));
  };

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            Market Data Sources
          </CardTitle>
          <CardDescription>
            Configure your market data provider and API settings
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Provider Selection */}
          <div className="space-y-2">
            <Label htmlFor="provider">Data Provider</Label>
            <Select value={provider} onValueChange={setProvider}>
              <SelectTrigger id="provider">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="yahoo">Yahoo Finance (Free)</SelectItem>
                <SelectItem value="polygon" disabled>Polygon.io (Coming Soon)</SelectItem>
                <SelectItem value="alpaca" disabled>Alpaca Markets (Coming Soon)</SelectItem>
                <SelectItem value="iex" disabled>IEX Cloud (Coming Soon)</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-sm text-muted-foreground">
              Yahoo Finance provides free real-time and historical market data
            </p>
          </div>

          {/* API Key Input */}
          <div className="space-y-2">
            <Label htmlFor="apiKey">API Key (Optional)</Label>
            <Input
              id="apiKey"
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="Enter API key if required"
            />
            <p className="text-sm text-muted-foreground">
              Yahoo Finance doesn't require an API key for basic data access
            </p>
          </div>

          {/* Trading Universe */}
          <div className="space-y-2">
            <Label>Trading Universe</Label>
            <div className="flex gap-2 mb-2">
              <Input
                value={newSymbol}
                onChange={(e) => setNewSymbol(e.target.value.toUpperCase())}
                placeholder="Add symbol (e.g., AAPL)"
                onKeyPress={(e) => e.key === 'Enter' && handleAddSymbol()}
              />
              <Button onClick={handleAddSymbol} size="sm">
                <Plus className="h-4 w-4" />
              </Button>
            </div>
            <div className="border rounded-lg p-3 max-h-48 overflow-y-auto">
              <div className="flex flex-wrap gap-2">
                {universe.map((symbol) => (
                  <Badge key={symbol} variant="secondary" className="gap-1">
                    {symbol}
                    <button
                      onClick={() => handleRemoveSymbol(symbol)}
                      className="ml-1 hover:text-destructive"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            </div>
            <p className="text-sm text-muted-foreground">
              {universe.length} symbols in your trading universe
            </p>
          </div>

          {/* Connection Status */}
          {connectionStatus !== "idle" && (
            <Alert className={
              connectionStatus === "success" ? "border-success" :
              connectionStatus === "error" ? "border-destructive" :
              ""
            }>
              {connectionStatus === "testing" && <Loader2 className="h-4 w-4 animate-spin" />}
              {connectionStatus === "success" && <CheckCircle className="h-4 w-4 text-success" />}
              {connectionStatus === "error" && <XCircle className="h-4 w-4 text-destructive" />}
              <AlertDescription>
                {connectionStatus === "testing" && "Testing connection..."}
                {connectionStatus === "success" && (
                  <div>
                    <p>Connection successful!</p>
                    {testResult?.test_quote && (
                      <p className="text-sm mt-1">
                        Test quote: {testResult.test_symbol} - ${testResult.test_quote.price?.toFixed(2)}
                      </p>
                    )}
                  </div>
                )}
                {connectionStatus === "error" && "Connection failed. Please check your settings."}
              </AlertDescription>
            </Alert>
          )}

          {/* Info Alert */}
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              Market data will be fetched in real-time during market hours. 
              The bot will automatically scan your universe for trading opportunities.
            </AlertDescription>
          </Alert>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <Button
              onClick={handleTestConnection}
              variant="outline"
              disabled={isTestingConnection}
            >
              {isTestingConnection ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Testing...
                </>
              ) : (
                "Test Connection"
              )}
            </Button>
            <Button
              onClick={handleSave}
              disabled={isSaving || universe.length === 0}
            >
              {isSaving ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                "Save Settings"
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SettingsDataSources;