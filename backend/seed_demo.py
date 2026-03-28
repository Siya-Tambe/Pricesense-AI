"""
Run this once to seed 5 demo products with 60 days of realistic price history.
Usage: python seed_demo.py
"""

from models import create_tables, SessionLocal, Product, PriceHistory, Prediction
from predictor import run_prediction
from datetime import datetime, timedelta
import random
import math

def generate_price_history(base_price, days=60, volatility="medium", trend="down"):
    """Generate realistic price history with sale events and fluctuations."""
    prices = []
    current = base_price

    # Sale event windows (simulate Big Billion Days, festive sales etc.)
    sale_windows = [
        (10, 15),  # first sale window
        (35, 40),  # second sale window
    ]

    for day in range(days):
        in_sale = any(start <= day <= end for start, end in sale_windows)

        if volatility == "high":
            noise = random.uniform(-0.04, 0.04)
        elif volatility == "low":
            noise = random.uniform(-0.01, 0.01)
        else:
            noise = random.uniform(-0.025, 0.025)

        if in_sale:
            # Drop price during sale
            noise -= random.uniform(0.03, 0.08)
        else:
            # Slight recovery after sale
            if any(day == end + 1 for _, end in sale_windows):
                noise += random.uniform(0.02, 0.05)

        if trend == "down":
            noise -= 0.003
        elif trend == "up":
            noise += 0.003
        elif trend == "volatile":
            noise += math.sin(day / 5) * 0.02

        current = current * (1 + noise)
        current = max(current, base_price * 0.5)
        current = min(current, base_price * 1.3)
        prices.append(round(current, 2))

    return prices


DEMO_PRODUCTS = [
    {
        "name":       "boAt Rockerz 450 Bluetooth Headphones",
        "url":        "https://www.amazon.in/dp/B07Q3GNKV9",
        "platform":   "amazon",
        "thumbnail":  "https://m.media-amazon.com/images/I/61vNMcTIMsL._SL1500_.jpg",
        "base_price": 1799,
        "volatility": "high",
        "trend":      "down",
    },
    {
        "name":       "Noise ColorFit Pro 4 Smart Watch",
        "url":        "https://www.flipkart.com/noise-colorfit-pro-4/p/itm123",
        "platform":   "flipkart",
        "thumbnail":  "https://rukminim2.flixcart.com/image/416/416/xif0q/smartwatch/y/q/o/-original-imaghx9yzfhxbznd.jpeg",
        "base_price": 3499,
        "volatility": "high",
        "trend":      "volatile",
    },
    {
        "name":       "Redmi Note 13 5G (6GB RAM, 128GB)",
        "url":        "https://www.amazon.in/dp/B0CQS6LXNF",
        "platform":   "amazon",
        "thumbnail":  "https://m.media-amazon.com/images/I/71enDhoPKlL._SL1500_.jpg",
        "base_price": 14999,
        "volatility": "medium",
        "trend":      "down",
    },
    {
        "name":       "Fastrack Analog Watch for Men",
        "url":        "https://www.myntra.com/watches/fastrack/fastrack-men/123456",
        "platform":   "myntra",
        "thumbnail":  "https://assets.myntassets.com/h_1440,q_90,w_1080/v1/assets/images/1195068/2016/2/10/11455101184052-Fastrack-Men-Watches-2721455101183908-1.jpg",
        "base_price": 1295,
        "volatility": "medium",
        "trend":      "volatile",
    },
    {
        "name":       "Realme Buds Wireless 3 Neckband",
        "url":        "https://www.flipkart.com/realme-buds-wireless-3/p/itm456",
        "platform":   "flipkart",
        "thumbnail":  "https://rukminim2.flixcart.com/image/416/416/xif0q/headphone/m/s/b/-original-imaghxsgygzhhhbx.jpeg",
        "base_price": 1799,
        "volatility": "high",
        "trend":      "down",
    },
]


def seed():
    create_tables()
    db = SessionLocal()

    try:
        # Clear existing demo products first
        existing_demos = db.query(Product).filter(Product.is_demo == True).all()
        for p in existing_demos:
            db.query(PriceHistory).filter(PriceHistory.product_id == p.id).delete()
            db.query(Prediction).filter(Prediction.product_id == p.id).delete()
            db.delete(p)
        db.commit()
        print(f"Cleared {len(existing_demos)} existing demo products.")

        for item in DEMO_PRODUCTS:
            # Create product
            product = Product(
                user_id       = None,
                url           = item["url"],
                name          = item["name"],
                platform      = item["platform"],
                thumbnail     = item["thumbnail"],
                scrape_status = "success",
                is_demo       = True,
                created_at    = datetime.utcnow() - timedelta(days=60),
            )
            db.add(product)
            db.commit()
            db.refresh(product)

            # Generate price history
            prices = generate_price_history(
                item["base_price"],
                days       = 60,
                volatility = item["volatility"],
                trend      = item["trend"],
            )

            history_objs = []
            for day_offset, price in enumerate(prices):
                scraped_at = datetime.utcnow() - timedelta(days=60 - day_offset)
                ph = PriceHistory(
                    product_id    = product.id,
                    price         = price,
                    scraped_at    = scraped_at,
                    scrape_status = "success",
                )
                db.add(ph)
                history_objs.append({"price": price, "scraped_at": scraped_at})

            db.commit()

            # Update current price to last price
            product.current_price = prices[-1]
            product.last_fetched  = datetime.utcnow()
            db.commit()

            # Run prediction
            prediction_result = run_prediction(history_objs)
            if prediction_result:
                pred = Prediction(
                    product_id      = product.id,
                    predicted_price = prediction_result["predicted_price"],
                    confidence      = prediction_result["confidence"],
                    verdict         = prediction_result["verdict"],
                    reasoning       = prediction_result["reasoning"],
                    created_at      = datetime.utcnow(),
                )
                db.add(pred)
                db.commit()
                verdict = prediction_result["verdict"].upper()
            else:
                verdict = "N/A"

            print(f"✅ {item['name'][:40]:<40} ₹{prices[-1]:>8,.0f}  →  {verdict}")

        print(f"\n🎉 Done! {len(DEMO_PRODUCTS)} demo products seeded successfully.")
        print("Run your server and open the dashboard to see them!\n")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()