import statistics
from datetime import datetime, timedelta
from typing import Optional


def calculate_moving_average(prices: list[float], window: int = 3) -> list[float]:
    if len(prices) < window:
        return prices
    result = []
    for i in range(len(prices)):
        if i < window - 1:
            result.append(prices[i])
        else:
            avg = sum(prices[i - window + 1 : i + 1]) / window
            result.append(avg)
    return result


def calculate_linear_trend(prices: list[float]) -> float:
    n = len(prices)
    if n < 2:
        return 0.0
    x_vals = list(range(n))
    x_mean = sum(x_vals) / n
    y_mean = sum(prices) / n
    numerator = sum((x_vals[i] - x_mean) * (prices[i] - y_mean) for i in range(n))
    denominator = sum((x - x_mean) ** 2 for x in x_vals)
    if denominator == 0:
        return 0.0
    slope = numerator / denominator
    return slope


def calculate_volatility(prices: list[float]) -> float:
    if len(prices) < 2:
        return 0.0
    try:
        std = statistics.stdev(prices)
        mean = statistics.mean(prices)
        if mean == 0:
            return 0.0
        return (std / mean) * 100
    except Exception:
        return 0.0


def forecast_next_7_days(prices: list[float]) -> dict:
    if len(prices) < 3:
        return {"day3": None, "day7": None}

    smoothed = calculate_moving_average(prices, window=min(3, len(prices)))
    slope = calculate_linear_trend(smoothed)
    last_price = prices[-1]

    day3_forecast = last_price + (slope * 3)
    day7_forecast = last_price + (slope * 7)

    day3_forecast = max(day3_forecast, last_price * 0.5)
    day7_forecast = max(day7_forecast, last_price * 0.5)

    return {
        "day3": round(day3_forecast, 2),
        "day7": round(day7_forecast, 2),
    }


def determine_confidence(prices: list[float]) -> str:
    days = len(prices)
    volatility = calculate_volatility(prices)

    if days >= 15 and volatility < 5:
        return "high"
    elif days >= 7 and volatility < 15:
        return "medium"
    else:
        return "low"


def get_verdict(
    current_price: float,
    forecast: dict,
    confidence: str,
    all_time_low: float,
) -> str:
    if forecast["day7"] is None:
        return "watching"

    day7 = forecast["day7"]
    price_change_pct = ((day7 - current_price) / current_price) * 100

    near_all_time_low = current_price <= (all_time_low * 1.05)

    if near_all_time_low:
        return "buy"

    if price_change_pct <= -3 and confidence in ("medium", "high"):
        return "wait"
    elif price_change_pct >= 3:
        return "buy"
    else:
        return "watching"


def build_reasoning(
    verdict: str,
    current_price: float,
    forecast: dict,
    confidence: str,
    volatility: float,
    all_time_low: float,
    all_time_high: float,
) -> str:
    price_change_pct = 0.0
    if forecast["day7"] is not None:
        price_change_pct = ((forecast["day7"] - current_price) / current_price) * 100

    volatility_label = "low" if volatility < 5 else "moderate" if volatility < 15 else "high"
    confidence_label = confidence.capitalize()

    if verdict == "buy":
        if current_price <= (all_time_low * 1.05):
            return (
                f"This product is currently priced near its all-time low of ₹{all_time_low:,.0f}. "
                f"Historically, prices at this level don't stay low for long. "
                f"With {confidence_label.lower()} confidence and {volatility_label} price volatility, now is a good time to buy."
            )
        else:
            return (
                f"Prices are predicted to rise by {abs(price_change_pct):.1f}% over the next 7 days "
                f"(forecast: ₹{forecast['day7']:,.0f}). "
                f"Volatility is {volatility_label} and confidence is {confidence_label.lower()}. "
                f"Buying now avoids paying more later."
            )
    elif verdict == "wait":
        return (
            f"Prices are expected to drop by {abs(price_change_pct):.1f}% within 7 days "
            f"(forecast: ₹{forecast['day7']:,.0f}). "
            f"The trend is downward with {volatility_label} volatility. "
            f"Confidence level is {confidence_label.lower()} — waiting is the smarter move right now."
        )
    else:
        return (
            f"The price trend is unclear at the moment. "
            f"Forecast for day 7 is ₹{forecast['day7']:,.0f} — a change of {price_change_pct:+.1f}%. "
            f"Volatility is {volatility_label} and confidence is {confidence_label.lower()}. "
            f"We recommend watching this product for a few more days before deciding."
        )


def run_prediction(price_history: list[dict]) -> Optional[dict]:
    if len(price_history) < 2:
        return None

    sorted_history = sorted(price_history, key=lambda x: x["scraped_at"])
    prices = [entry["price"] for entry in sorted_history if entry["price"] is not None]

    if len(prices) < 2:
        return None

    current_price = prices[-1]
    all_time_low = min(prices)
    all_time_high = max(prices)
    volatility = calculate_volatility(prices)
    forecast = forecast_next_7_days(prices)
    confidence = determine_confidence(prices)
    verdict = get_verdict(current_price, forecast, confidence, all_time_low)
    reasoning = build_reasoning(
        verdict, current_price, forecast, confidence,
        volatility, all_time_low, all_time_high
    )

    return {
        "verdict": verdict,
        "confidence": confidence,
        "predicted_price": forecast["day7"],
        "forecast_day3": forecast["day3"],
        "forecast_day7": forecast["day7"],
        "reasoning": reasoning,
        "stats": {
            "current_price": round(current_price, 2),
            "all_time_low": round(all_time_low, 2),
            "all_time_high": round(all_time_high, 2),
            "volatility": round(volatility, 2),
            "days_tracked": len(prices),
            "price_change_pct": round(
                ((forecast["day7"] - current_price) / current_price) * 100, 2
            ) if forecast["day7"] else 0,
        },
    }