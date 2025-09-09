import { useEffect, useState } from "react";
import { TrendingUp, TrendingDown } from "lucide-react";

interface TickerItem {
  symbol: string;
  price: number;
  change: number;
}

const LiveTicker = () => {
  const [tickers] = useState<TickerItem[]>([
    { symbol: "SPY", price: 445.32, change: 0.45 },
    { symbol: "QQQ", price: 385.67, change: -0.23 },
    { symbol: "VIX", price: 18.45, change: 2.34 },
    { symbol: "DXY", price: 104.23, change: -0.12 },
    { symbol: "BTC", price: 68542, change: 3.21 },
  ]);

  const [offset, setOffset] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setOffset((prev) => (prev - 1) % (tickers.length * 150));
    }, 50);
    return () => clearInterval(interval);
  }, [tickers.length]);

  return (
    <div className="overflow-hidden w-96">
      <div 
        className="flex gap-6 whitespace-nowrap"
        style={{ transform: `translateX(${offset}px)` }}
      >
        {[...tickers, ...tickers].map((ticker, index) => (
          <div key={index} className="flex items-center gap-2">
            <span className="font-medium text-sm">{ticker.symbol}</span>
            <span className="text-sm">${ticker.price.toLocaleString()}</span>
            <div className={`flex items-center gap-1 text-sm ${ticker.change >= 0 ? "text-success" : "text-destructive"}`}>
              {ticker.change >= 0 ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
              {Math.abs(ticker.change).toFixed(2)}%
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default LiveTicker;