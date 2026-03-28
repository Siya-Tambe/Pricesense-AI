from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pricesense.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ── User ────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id           = Column(Integer, primary_key=True, index=True)
    email        = Column(String, unique=True, index=True, nullable=False)
    name         = Column(String, nullable=False)
    password     = Column(String, nullable=False)
    created_at   = Column(DateTime, default=datetime.utcnow)
    is_active    = Column(Boolean, default=True)

    products     = relationship("Product", back_populates="owner", cascade="all, delete")


# ── Product ─────────────────────────────────────────────────────

class Product(Base):
    __tablename__ = "products"

    id            = Column(Integer, primary_key=True, index=True)
    user_id       = Column(Integer, ForeignKey("users.id"), nullable=True)
    url           = Column(String, index=True)
    name          = Column(String)
    platform      = Column(String)
    thumbnail     = Column(String, nullable=True)
    current_price = Column(Float, nullable=True)
    last_fetched  = Column(DateTime, nullable=True)
    scrape_status = Column(String, default="pending")
    created_at    = Column(DateTime, default=datetime.utcnow)
    alert_price   = Column(Float, nullable=True)
    alert_enabled = Column(Boolean, default=False)
    is_demo       = Column(Boolean, default=False)

    owner         = relationship("User", back_populates="products")


# ── Price History ────────────────────────────────────────────────

class PriceHistory(Base):
    __tablename__ = "price_history"

    id            = Column(Integer, primary_key=True, index=True)
    product_id    = Column(Integer, ForeignKey("products.id"), index=True)
    price         = Column(Float)
    scraped_at    = Column(DateTime, default=datetime.utcnow)
    scrape_status = Column(String, default="success")


# ── Prediction ───────────────────────────────────────────────────

class Prediction(Base):
    __tablename__ = "predictions"

    id              = Column(Integer, primary_key=True, index=True)
    product_id      = Column(Integer, ForeignKey("products.id"), index=True)
    predicted_price = Column(Float)
    confidence      = Column(String)
    verdict         = Column(String)
    reasoning       = Column(Text, nullable=True)
    created_at      = Column(DateTime, default=datetime.utcnow)
    actual_price    = Column(Float, nullable=True)


# ── DB helpers ───────────────────────────────────────────────────

def create_tables():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()