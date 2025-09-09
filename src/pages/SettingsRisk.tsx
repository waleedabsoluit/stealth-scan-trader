import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { AlertTriangle, Shield, TrendingUp, DollarSign, Save } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/api/client";

export default function SettingsRisk() {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [settings, setSettings] = useState({
    maxPortfolioRisk: 0.5,
    maxPositionSize: 10000,
    maxDailyLoss: 5000,
    maxPositions: 10,
    stopLossPercent: 2,
    takeProfitPercent: 5,
    trailingStop: false,
    trailingStopPercent: 1,
    autoCloseOnAlert: true,
    marginCallLevel: 25,
    riskPerTrade: 2,
    diversificationRequired: true,
    correlationLimit: 0.7
  });

  const handleSave = async () => {
    setLoading(true);
    try {
      await api.post('/api/risk/settings', settings);
      toast({
        title: "Settings saved",
        description: "Risk management settings have been updated",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to save risk settings",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Risk Management Settings</h1>
        <p className="text-muted-foreground">Configure risk parameters and safety limits for your trading bot</p>
      </div>

      <Tabs defaultValue="limits" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="limits">Position Limits</TabsTrigger>
          <TabsTrigger value="stops">Stop Loss</TabsTrigger>
          <TabsTrigger value="portfolio">Portfolio Risk</TabsTrigger>
          <TabsTrigger value="alerts">Risk Alerts</TabsTrigger>
        </TabsList>

        <TabsContent value="limits" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <DollarSign className="h-5 w-5" />
                Position Limits
              </CardTitle>
              <CardDescription>Set maximum position sizes and limits</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label>Max Position Size: ${settings.maxPositionSize}</Label>
                <Slider
                  value={[settings.maxPositionSize]}
                  onValueChange={([value]) => setSettings({ ...settings, maxPositionSize: value })}
                  min={1000}
                  max={50000}
                  step={1000}
                />
              </div>

              <div className="space-y-2">
                <Label>Max Open Positions: {settings.maxPositions}</Label>
                <Slider
                  value={[settings.maxPositions]}
                  onValueChange={([value]) => setSettings({ ...settings, maxPositions: value })}
                  min={1}
                  max={20}
                  step={1}
                />
              </div>

              <div className="space-y-2">
                <Label>Risk Per Trade: {settings.riskPerTrade}%</Label>
                <Slider
                  value={[settings.riskPerTrade]}
                  onValueChange={([value]) => setSettings({ ...settings, riskPerTrade: value })}
                  min={0.5}
                  max={5}
                  step={0.5}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="stops" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Stop Loss Configuration
              </CardTitle>
              <CardDescription>Configure stop loss and take profit settings</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label>Stop Loss: {settings.stopLossPercent}%</Label>
                <Slider
                  value={[settings.stopLossPercent]}
                  onValueChange={([value]) => setSettings({ ...settings, stopLossPercent: value })}
                  min={0.5}
                  max={10}
                  step={0.5}
                />
              </div>

              <div className="space-y-2">
                <Label>Take Profit: {settings.takeProfitPercent}%</Label>
                <Slider
                  value={[settings.takeProfitPercent]}
                  onValueChange={([value]) => setSettings({ ...settings, takeProfitPercent: value })}
                  min={1}
                  max={20}
                  step={1}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label>Trailing Stop</Label>
                  <p className="text-sm text-muted-foreground">Enable dynamic stop loss adjustment</p>
                </div>
                <Switch
                  checked={settings.trailingStop}
                  onCheckedChange={(checked) => setSettings({ ...settings, trailingStop: checked })}
                />
              </div>

              {settings.trailingStop && (
                <div className="space-y-2">
                  <Label>Trailing Stop Distance: {settings.trailingStopPercent}%</Label>
                  <Slider
                    value={[settings.trailingStopPercent]}
                    onValueChange={([value]) => setSettings({ ...settings, trailingStopPercent: value })}
                    min={0.5}
                    max={5}
                    step={0.5}
                  />
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="portfolio" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Portfolio Risk Management
              </CardTitle>
              <CardDescription>Overall portfolio risk parameters</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label>Max Portfolio Risk: {(settings.maxPortfolioRisk * 100).toFixed(0)}%</Label>
                <Slider
                  value={[settings.maxPortfolioRisk * 100]}
                  onValueChange={([value]) => setSettings({ ...settings, maxPortfolioRisk: value / 100 })}
                  min={10}
                  max={100}
                  step={5}
                />
              </div>

              <div className="space-y-2">
                <Label>Max Daily Loss: ${settings.maxDailyLoss}</Label>
                <Slider
                  value={[settings.maxDailyLoss]}
                  onValueChange={([value]) => setSettings({ ...settings, maxDailyLoss: value })}
                  min={1000}
                  max={20000}
                  step={500}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label>Require Diversification</Label>
                  <p className="text-sm text-muted-foreground">Enforce position diversification rules</p>
                </div>
                <Switch
                  checked={settings.diversificationRequired}
                  onCheckedChange={(checked) => setSettings({ ...settings, diversificationRequired: checked })}
                />
              </div>

              <div className="space-y-2">
                <Label>Correlation Limit: {settings.correlationLimit}</Label>
                <Slider
                  value={[settings.correlationLimit]}
                  onValueChange={([value]) => setSettings({ ...settings, correlationLimit: value })}
                  min={0.3}
                  max={1}
                  step={0.1}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="alerts" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5" />
                Risk Alerts & Actions
              </CardTitle>
              <CardDescription>Configure risk alerts and automatic actions</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <Label>Auto-Close on High Risk Alert</Label>
                  <p className="text-sm text-muted-foreground">Automatically close positions on critical alerts</p>
                </div>
                <Switch
                  checked={settings.autoCloseOnAlert}
                  onCheckedChange={(checked) => setSettings({ ...settings, autoCloseOnAlert: checked })}
                />
              </div>

              <div className="space-y-2">
                <Label>Margin Call Level: {settings.marginCallLevel}%</Label>
                <Slider
                  value={[settings.marginCallLevel]}
                  onValueChange={([value]) => setSettings({ ...settings, marginCallLevel: value })}
                  min={10}
                  max={50}
                  step={5}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>High Risk Threshold</Label>
                  <Input type="number" placeholder="0.7" defaultValue="0.7" />
                </div>
                <div>
                  <Label>Critical Risk Threshold</Label>
                  <Input type="number" placeholder="0.9" defaultValue="0.9" />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <div className="flex justify-end mt-6">
        <Button onClick={handleSave} disabled={loading} size="lg">
          <Save className="mr-2 h-4 w-4" />
          {loading ? "Saving..." : "Save Risk Settings"}
        </Button>
      </div>
    </div>
  );
}