"""
Database models and configuration for SentimentTrade
Implements user authentication, watchlist, and trade tracking
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.sql import func
from sqlalchemy.schema import ForeignKey
from datetime import datetime
from typing import Optional, List, Dict, Any
import os
from config import config

# Database URL - can be configured via environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sentimenttrade.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

class User(Base):
    """User model for authentication and personalization"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    watchlist_items = relationship("WatchlistItem", back_populates="user", cascade="all, delete-orphan")
    trade_confirmations = relationship("TradeConfirmation", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreferences", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"

class WatchlistItem(Base):
    """Watchlist item model for user's tracked symbols"""
    __tablename__ = "watchlist_items"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symbol = Column(String, nullable=False, index=True)
    signal_preferences = Column(JSON, nullable=True)  # RSI thresholds, timeframes, etc.
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="watchlist_items")
    
    def __repr__(self):
        return f"<WatchlistItem(id={self.id}, user_id={self.user_id}, symbol='{self.symbol}')>"

class Signal(Base):
    """Signal model for storing generated trading signals"""
    __tablename__ = "signals"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False, index=True)
    recommendation = Column(String, nullable=False)  # BUY, SELL, HOLD
    confidence = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)
    target_price = Column(Float, nullable=False)
    sentiment = Column(Float, nullable=False)
    risk_reward_ratio = Column(Float, nullable=True)
    indicators = Column(JSON, nullable=True)  # Technical indicators data
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    trade_confirmations = relationship("TradeConfirmation", back_populates="signal")
    
    def __repr__(self):
        return f"<Signal(id={self.id}, symbol='{self.symbol}', recommendation='{self.recommendation}')>"

class TradeConfirmation(Base):
    """Trade confirmation model for tracking user's actual trades"""
    __tablename__ = "trade_confirmations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    signal_id = Column(Integer, ForeignKey("signals.id"), nullable=False)
    symbol = Column(String, nullable=False, index=True)
    recommendation = Column(String, nullable=False)
    
    # Trade execution details
    executed = Column(Boolean, default=False)
    execution_price = Column(Float, nullable=True)
    quantity = Column(Float, nullable=True)
    execution_time = Column(DateTime, nullable=True)
    
    # Performance tracking
    pnl = Column(Float, nullable=True)  # Profit/Loss
    pnl_percentage = Column(Float, nullable=True)
    
    # User notes and feedback
    notes = Column(Text, nullable=True)
    user_rating = Column(Integer, nullable=True)  # 1-5 rating of signal quality
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="trade_confirmations")
    signal = relationship("Signal", back_populates="trade_confirmations")
    
    def __repr__(self):
        return f"<TradeConfirmation(id={self.id}, symbol='{self.symbol}', executed={self.executed})>"

class UserSession(Base):
    """User session model for JWT token management"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token_jti = Column(String, unique=True, nullable=False)  # JWT ID
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id})>"


class UserPreferences(Base):
    """User preferences model for trading settings and personalization"""
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Trading Strategy Settings
    risk_appetite = Column(String, default="moderate")  # low, moderate, high
    strategy = Column(String, default="default")  # default, aggressive, conservative, momentum
    min_confidence = Column(Float, default=0.7)  # minimum confidence for signals (0.5-0.95)
    max_daily_signals = Column(Integer, default=10)  # maximum signals per day (5-50)
    
    # Notification Settings
    notification_enabled = Column(Boolean, default=True)
    email_alerts = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    signal_threshold = Column(Float, default=0.8)  # only notify for high-confidence signals
    
    # Advanced Settings
    auto_execute_trades = Column(Boolean, default=False)  # future feature
    max_position_size = Column(Float, default=1000.0)  # maximum position size in USD
    stop_loss_percentage = Column(Float, default=0.05)  # default 5% stop loss
    take_profit_percentage = Column(Float, default=0.15)  # default 15% take profit
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="preferences")
    
    def __repr__(self):
        return f"<UserPreferences(id={self.id}, user_id={self.user_id}, strategy='{self.strategy}')>"

# Database utility functions
def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")

def drop_tables():
    """Drop all database tables (use with caution!)"""
    Base.metadata.drop_all(bind=engine)
    print("⚠️ All database tables dropped")

def reset_database():
    """Reset database (drop and recreate tables)"""
    drop_tables()
    create_tables()
    print("🔄 Database reset completed")

# Database initialization
def init_database():
    """Initialize database with tables"""
    try:
        create_tables()
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    # Test database setup
    print("🗄️ Testing SentimentTrade Database Setup")
    print("=" * 50)
    
    # Initialize database
    if init_database():
        print("✅ Database initialized successfully")
        
        # Test connection
        try:
            db = next(get_db())
            
            # Test query
            user_count = db.query(User).count()
            signal_count = db.query(Signal).count()
            
            print(f"📊 Database Statistics:")
            print(f"   Users: {user_count}")
            print(f"   Signals: {signal_count}")
            print(f"   Database URL: {DATABASE_URL}")
            
            db.close()
            print("✅ Database connection test successful")
            
        except Exception as e:
            print(f"❌ Database connection test failed: {e}")
    else:
        print("❌ Database initialization failed")
