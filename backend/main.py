from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import os
from dotenv import load_dotenv

from models import create_tables, get_db, Product, PriceHistory, Prediction
from scraper import scrape_product, detect_platform
from predictor import run_prediction
from scheduler import start_scheduler, stop_scheduler, fetch_price_for_product, run_prediction_for_product

load_dotenv()

app = FastAPI(title="PriceSense API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pydantic schemas ────────────────────────────────────────────

class TrackRequest(BaseModel):
    url: str

class AlertRequest(BaseModel):
    product_id: int
    alert_price: float
    enabled: bool = True


# ── Startup / shutdown ──────────────────────────────────────────

@app.on_event("startup")
def on_startup():
    create_tables()
    start_scheduler()


@app.on_event("shutdown")
def on_shutdown():
    stop_scheduler()


# ── Health check ────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "PriceSense API is running", "version": "1.0.0"}


# ── Track a new product ─────────────────────────────────────────

@app.post("/track")
def track_product(request: TrackRequest, db: Session = Depends(get_db)):
    url = request.url.strip()

    platform = detect_platform(url)
    if platform == "unknown":
        raise HTTPException(
            status_code=400,
            detail="Unsupported platform. Please use Amazon, Flipkart, Myntra, or Croma URLs."
        )

    existing = db.query(Product).filter(Product.url == url).first()
    if existing:
        return {
            "message": "Product already being tracked",
            "product_id": existing.id,
            "product": format_product(existing, db),
        }

    result = scrape_product(url)

    product = Product(
        url=url,
        name=result.get("name") or "Unknown Product",
        platform=platform,
        thumbnail=result.get("thumbnail"),
        current_price=result.get("price"),
        last_fetched=datetime.utcnow(),
        scrape_status=result.get("status", "success"),
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    if result.get("price"):
        price_entry = PriceHistory(
            product_id=product.id,
            price=result["price"],
            scraped_at=datetime.utcnow(),
            scrape_status="success",
        )
        db.add(price_entry)
        db.commit()

    return {
        "message": "Product is now being tracked",
        "product_id": product.id,
        "product": format_product(product, db),
    }


# ── Get all tracked products ────────────────────────────────────

@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).order_by(Product.created_at.desc()).all()
    return [format_product(p, db) for p in products]


# ── Get a single product with full details ──────────────────────

@app.get("/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    history = (
        db.query(PriceHistory)
        .filter(PriceHistory.product_id == product_id)
        .order_by(PriceHistory.scraped_at)
        .all()
    )

    prediction = (
        db.query(Prediction)
        .filter(Prediction.product_id == product_id)
        .order_by(Prediction.created_at.desc())
        .first()
    )

    prices = [h.price for h in history if h.price]
    history_data = [{"price": h.price, "scraped_at": h.scraped_at} for h in history]
    fresh_prediction = run_prediction(history_data) if len(history_data) >= 2 else None

    return {
        "id": product.id,
        "url": product.url,
        "name": product.name,
        "platform": product.platform,
        "thumbnail": product.thumbnail,
        "current_price": product.current_price,
        "last_fetched": product.last_fetched,
        "scrape_status": product.scrape_status,
        "created_at": product.created_at,
        "alert_price": product.alert_price,
        "alert_enabled": product.alert_enabled,
        "days_tracked": len(set(h.scraped_at.date() for h in history)) if history else 0,
        "stats": {
            "all_time_low": min(prices) if prices else None,
            "all_time_high": max(prices) if prices else None,
            "average_price": round(sum(prices) / len(prices), 2) if prices else None,
        },
        "prediction": {
            "verdict": fresh_prediction["verdict"] if fresh_prediction else None,
            "confidence": fresh_prediction["confidence"] if fresh_prediction else None,
            "reasoning": fresh_prediction["reasoning"] if fresh_prediction else None,
            "forecast_day3": fresh_prediction["forecast_day3"] if fresh_prediction else None,
            "forecast_day7": fresh_prediction["forecast_day7"] if fresh_prediction else None,
            "stats": fresh_prediction["stats"] if fresh_prediction else None,
        },
        "price_history": [
            {
                "price": h.price,
                "date": h.scraped_at.isoformat(),
            }
            for h in history
        ],
    }


# ── Manually refresh a product price ───────────────────────────

@app.post("/products/{product_id}/refresh")
def refresh_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    fetch_price_for_product(product_id)
    db.refresh(product)

    return {"message": "Price refreshed", "product": format_product(product, db)}


# ── Set a price alert ───────────────────────────────────────────

@app.post("/alerts")
def set_alert(request: AlertRequest, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == request.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.alert_price = request.alert_price
    product.alert_enabled = request.enabled
    db.commit()

    return {
        "message": "Alert set successfully",
        "product_id": product.id,
        "alert_price": product.alert_price,
        "alert_enabled": product.alert_enabled,
    }


# ── Delete a tracked product ────────────────────────────────────

@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.query(PriceHistory).filter(PriceHistory.product_id == product_id).delete()
    db.query(Prediction).filter(Prediction.product_id == product_id).delete()
    db.delete(product)
    db.commit()

    return {"message": "Product deleted successfully"}


# ── Helper: format product for list view ───────────────────────

def format_product(product: Product, db: Session) -> dict:
    prediction = (
        db.query(Prediction)
        .filter(Prediction.product_id == product.id)
        .order_by(Prediction.created_at.desc())
        .first()
    )

    days_tracked = db.query(PriceHistory).filter(
        PriceHistory.product_id == product.id
    ).count()

    last_fetched_str = None
    if product.last_fetched:
        diff = datetime.utcnow() - product.last_fetched
        hours = int(diff.total_seconds() // 3600)
        if hours < 1:
            last_fetched_str = "Just now"
        elif hours == 1:
            last_fetched_str = "1 hour ago"
        else:
            last_fetched_str = f"{hours} hours ago"

    return {
        "id": product.id,
        "name": product.name,
        "platform": product.platform,
        "thumbnail": product.thumbnail,
        "current_price": product.current_price,
        "scrape_status": product.scrape_status,
        "last_fetched": last_fetched_str,
        "days_tracked": days_tracked,
        "alert_price": product.alert_price,
        "alert_enabled": product.alert_enabled,
        "verdict": prediction.verdict if prediction else None,
        "confidence": prediction.confidence if prediction else None,
    }