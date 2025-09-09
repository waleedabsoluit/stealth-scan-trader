import { useEffect, useState } from "react";
import { TrendingUp, TrendingDown, Loader2 } from "lucide-react";
import { useMarketQuotes } from "@/hooks/useMarketData";

const TICKER_SYMBOLS = ["SPY", "QQQ", "NVDA", "TSLA", "AAPL"];

const LiveTicker = () => {
  const { data: quotes, isLoading } = useMarketQuotes(TICKER_SYMBOLS);
  const [offset, setOffset] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setOffset((prev) => (prev - 1) % (TICKER_SYMBOLS.length * 200));
    }, 50);
    return () => clearInterval(interval);
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 text-muted-foreground">
        <Loader2 className="h-4 w-4 animate-spin" />
        <span className="text-sm">Loading market data...</span>
      </div>
    );
  }

  const tickers = TICKER_SYMBOLS.map(symbol => {
    const quote = quotes?.[symbol];
    return {
      symbol,
      price: quote?.price || 0,
      change: quote?.change_percent || 0,
    };
  });

  return (
    <div className="overflow-hidden w-96">
      <div 
        className="flex gap-6 whitespace-nowrap"
        style={{ transform: `translateX(${offset}px)` }}
      >
        {[...tickers, ...tickers].map((ticker, index) => (
          <div key={index} className="flex items-center gap-2">
            <span className="font-medium text-sm">{ticker.symbol}</span>
            <span className="text-sm">
              ${ticker.price > 0 ? ticker.price.toFixed(2) : '—'}
            </span>
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