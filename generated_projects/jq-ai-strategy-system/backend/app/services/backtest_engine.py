import random
import datetime

def run_quick_backtest(code: str) -> dict:
    """Simulate a quick backtest and return summary metrics."""
    total_return = round(random.uniform(-5, 20), 2)
    annual_return = round(random.uniform(-3, 15), 2)
    max_drawdown = round(random.uniform(-20, -2), 2)
    sharpe = round(random.uniform(0.5, 2.5), 2)
    # Generate mock daily returns for chart
    days = 60
    start_date = datetime.date.today() - datetime.timedelta(days=days)
    dates = [(start_date + datetime.timedelta(days=i)).isoformat() for i in range(days)]
    nav = [100]
    for i in range(1, days):
        r = random.uniform(-0.03, 0.03)
        nav.append(round(nav[-1] * (1+r), 2))
    net_value_curve = [{"date": d, "value": v} for d, v in zip(dates, nav)]
    return {
        "total_return_pct": total_return,
        "annual_return_pct": annual_return,
        "max_drawdown_pct": max_drawdown,
        "sharpe_ratio": sharpe,
        "net_value_curve": net_value_curve,
        "summary": f"快速回测结果：总收益率{total_return}%，年化收益{annual_return}%，最大回撤{max_drawdown}%，夏普比率{sharpe}"
    }

def run_full_backtest(code: str) -> dict:
    """Simulate a full performance backtest with more detailed metrics."""
    total_return = round(random.uniform(-5, 30), 2)
    annual_return = round(random.uniform(-3, 20), 2)
    max_drawdown = round(random.uniform(-25, -3), 2)
    sharpe = round(random.uniform(0.3, 3.0), 2)
    win_rate = round(random.uniform(40, 70), 1)
    trades_count = random.randint(10, 100)
    # Generate net value curve
    days = 252
    start_date = datetime.date.today() - datetime.timedelta(days=days)
    dates = [(start_date + datetime.timedelta(days=i)).isoformat() for i in range(days)]
    nav = [100]
    for i in range(1, days):
        r = random.uniform(-0.04, 0.04)
        nav.append(round(nav[-1] * (1+r), 2))
    net_value_curve = [{"date": d, "value": v} for d, v in zip(dates, nav)]
    # Drawdown curve
    peak = 100
    drawdown_curve = []
    for v in nav:
        if v > peak:
            peak = v
        drawdown = round((v - peak) / peak * 100, 2)
        drawdown_curve.append({"date": dates[len(drawdown_curve)], "value": drawdown})
    # Monthly returns heatmap (mock)
    monthly_returns = {}
    for month in range(1, 13):
        monthly_returns[str(month)] = round(random.uniform(-5, 8), 1)
    # Transaction records
    transactions = []
    for i in range(min(20, trades_count)):
        tr = {
            "date": (datetime.date.today() - datetime.timedelta(days=random.randint(1, days))).isoformat(),
            "action": random.choice(["买入", "卖出"]),
            "price": round(random.uniform(10, 50), 2),
            "shares": random.randint(100, 1000),
            "pnl": round(random.uniform(-500, 1500), 2)
        }
        transactions.append(tr)
    transactions.sort(key=lambda x: x["date"], reverse=True)
    return {
        "total_return_pct": total_return,
        "annual_return_pct": annual_return,
        "max_drawdown_pct": max_drawdown,
        "sharpe_ratio": sharpe,
        "win_rate_pct": win_rate,
        "num_trades": trades_count,
        "net_value_curve": net_value_curve,
        "drawdown_curve": drawdown_curve,
        "monthly_returns": monthly_returns,
        "transactions": transactions
    }
