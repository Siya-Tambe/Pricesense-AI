from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from sqlalchemy.orm import Session
from models import SessionLocal, Product, PriceHistory, Prediction
from scraper import scrape_product
from predictor import run_prediction
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def fetch_price_for_product(product_id: int):
    db: Session = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return

        logger.info(f"Fetching price for: {product.name} ({product.url})")
        result = scrape_product(product.url)

        if result["price"] is not None:
            price_entry = PriceHistory(
                product_id=product.id,
                price=result["price"],
                scraped_at=datetime.utcnow(),
                scrape_status="success",
            )
            db.add(price_entry)

            product.current_price = result["price"]
            product.last_fetched = datetime.utcnow()
            product.scrape_status = "success"

            if not product.name and result["name"]:
                product.name = result["name"]
            if not product.thumbnail and result["thumbnail"]:
                product.thumbnail = result["thumbnail"]

            db.commit()
            logger.info(f"Price saved: ₹{result['price']} for {product.name}")

            run_prediction_for_product(product.id, db)

            check_price_alert(product, result["price"], db)

        else:
            product.scrape_status = result.get("status", "error")
            product.last_fetched = datetime.utcnow()
            db.commit()
            logger.warning(f"Could not fetch price for {product.url}: {result.get('status')}")

    except Exception as e:
        logger.error(f"Error fetching product {product_id}: {str(e)}")
        db.rollback()
    finally:
        db.close()


def run_prediction_for_product(product_id: int, db: Session):
    try:
        history = (
            db.query(PriceHistory)
            .filter(PriceHistory.product_id == product_id)
            .order_by(PriceHistory.scraped_at)
            .all()
        )

        if len(history) < 2:
            return

        history_data = [
            {"price": h.price, "scraped_at": h.scraped_at}
            for h in history
        ]

        result = run_prediction(history_data)
        if not result:
            return

        prediction = Prediction(
            product_id=product_id,
            predicted_price=result["predicted_price"],
            confidence=result["confidence"],
            verdict=result["verdict"],
            reasoning=result["reasoning"],
            created_at=datetime.utcnow(),
        )
        db.add(prediction)
        db.commit()
        logger.info(f"Prediction saved for product {product_id}: {result['verdict']} ({result['confidence']} confidence)")

    except Exception as e:
        logger.error(f"Error running prediction for product {product_id}: {str(e)}")
        db.rollback()


def check_price_alert(product: Product, current_price: float, db: Session):
    try:
        if not product.alert_enabled or product.alert_price is None:
            return
        if current_price <= product.alert_price:
            logger.info(
                f"ALERT TRIGGERED: {product.name} dropped to ₹{current_price} "
                f"(target: ₹{product.alert_price})"
            )
    except Exception as e:
        logger.error(f"Error checking alert for product {product.id}: {str(e)}")


def fetch_all_products():
    db: Session = SessionLocal()
    try:
        products = db.query(Product).all()
        logger.info(f"Scheduled fetch: checking {len(products)} products")
        product_ids = [p.id for p in products]
    finally:
        db.close()

    for product_id in product_ids:
        try:
            fetch_price_for_product(product_id)
        except Exception as e:
            logger.error(f"Error in scheduled fetch for product {product_id}: {str(e)}")


def start_scheduler():
    scheduler.add_job(
        fetch_all_products,
        trigger=IntervalTrigger(hours=8),
        id="fetch_all_prices",
        name="Fetch all product prices",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started — prices will be fetched every 8 hours")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")