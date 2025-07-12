"""
Enhanced FastAPI server for SentimentTrade with user authentication,
watchlist management, and trade tracking capabilities
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field, EmailStr
from typing import Dict, List, Optional, Any
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Import our enhanced modules
from database import get_db, init_database, User, WatchlistItem, Signal, TradeConfirmation, UserPreferences
from auth import (
    AuthService, UserCreate, UserLogin, UserResponse, Token,
    get_current_user, get_current_user_optional
)
from ai_trade_signal_enhanced import TradingSignalGenerator
from preferences_service import get_preferences_service
from preferences_models import (
    UserPreferencesResponse, UserPreferencesUpdate, PreferencesUpdateResponse,
    AvailableStrategiesResponse, RiskProfilesResponse
)
from config import config
from logger import logger

# Initialize database
init_database()

# FastAPI app
app = FastAPI(
    title="SentimentTrade Enhanced API",
    description="AI-powered trading signals with user management, watchlist, and trade tracking",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class SignalRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol", example="AAPL")
    include_indicators: bool = Field(True, description="Include technical indicators")

class SignalResponse(BaseModel):
    id: Optional[int] = None
    symbol: str
    timestamp: str
    recommendation: str
    confidence: float
    current_price: float
    entry_price: float
    stop_loss: float
    target_price: float
    sentiment: float
    risk_reward_ratio: Optional[float] = None
    indicators: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class WatchlistItemCreate(BaseModel):
    symbol: str = Field(..., description="Stock symbol", example="AAPL")
    signal_preferences: Optional[Dict[str, Any]] = Field(None, description="Signal preferences")
    notes: Optional[str] = Field(None, description="User notes")

class WatchlistItemResponse(BaseModel):
    id: int
    symbol: str
    signal_preferences: Optional[Dict[str, Any]]
    notes: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class TradeConfirmationCreate(BaseModel):
    signal_id: int = Field(..., description="Signal ID")
    executed: bool = Field(..., description="Whether trade was executed")
    execution_price: Optional[float] = Field(None, description="Actual execution price")
    quantity: Optional[float] = Field(None, description="Trade quantity")
    notes: Optional[str] = Field(None, description="User notes")
    user_rating: Optional[int] = Field(None, description="Signal rating 1-5", ge=1, le=5)

class TradeConfirmationResponse(BaseModel):
    id: int
    symbol: str
    recommendation: str
    executed: bool
    execution_price: Optional[float]
    quantity: Optional[float]
    pnl: Optional[float]
    pnl_percentage: Optional[float]
    notes: Optional[str]
    user_rating: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_signals: int
    executed_trades: int
    win_rate: float
    total_pnl: float
    avg_confidence: float
    best_performing_symbol: Optional[str]
    recent_activity: List[Dict[str, Any]]

# Global signal generator
signal_generator = TradingSignalGenerator()

# Utility functions
def store_signal(db: Session, signal_data: Dict[str, Any]) -> Signal:
    """Store signal in database"""
    db_signal = Signal(
        symbol=signal_data['symbol'],
        recommendation=signal_data['recommendation'],
        confidence=signal_data['confidence'],
        current_price=signal_data['current_price'],
        entry_price=signal_data['entry_price'],
        stop_loss=signal_data['stop_loss'],
        target_price=signal_data['target_price'],
        sentiment=signal_data['sentiment'],
        risk_reward_ratio=signal_data.get('risk_reward_ratio'),
        indicators=signal_data.get('indicators')
    )
    
    db.add(db_signal)
    db.commit()
    db.refresh(db_signal)
    
    return db_signal

def calculate_pnl(entry_price: float, exit_price: float, quantity: float, recommendation: str) -> tuple:
    """Calculate P&L and percentage"""
    if recommendation == "BUY":
        pnl = (exit_price - entry_price) * quantity
        pnl_percentage = ((exit_price - entry_price) / entry_price) * 100
    else:  # SELL
        pnl = (entry_price - exit_price) * quantity
        pnl_percentage = ((entry_price - exit_price) / entry_price) * 100
    
    return pnl, pnl_percentage

# Authentication endpoints
@app.post("/auth/register", response_model=Dict[str, Any])
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register new user"""
    try:
        auth_service = AuthService(db)
        result = auth_service.register_user(user)
        logger.info(f"New user registered: {user.email}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/auth/login", response_model=Dict[str, Any])
async def login(user: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    try:
        auth_service = AuthService(db)
        result = auth_service.login_user(user)
        logger.info(f"User logged in: {user.email}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.post("/auth/logout")
async def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Logout user"""
    # Note: In a real implementation, you'd extract JTI from the token
    return {"message": "Logged out successfully"}

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse.from_orm(current_user)

# Enhanced signal endpoints
@app.post("/signal", response_model=SignalResponse)
async def get_trading_signal(
    request: SignalRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Get trading signal for a symbol"""
    try:
        # Generate signal
        signal_data = signal_generator.generate_signal(request.symbol.upper())
        
        # Store signal in database
        db_signal = store_signal(db, signal_data)
        
        # Calculate risk/reward ratio
        if signal_data['recommendation'] != 'HOLD':
            if signal_data['recommendation'] == 'BUY':
                risk = abs(signal_data['entry_price'] - signal_data['stop_loss'])
                reward = abs(signal_data['target_price'] - signal_data['entry_price'])
            else:  # SELL
                risk = abs(signal_data['stop_loss'] - signal_data['entry_price'])
                reward = abs(signal_data['entry_price'] - signal_data['target_price'])
            
            signal_data['risk_reward_ratio'] = reward / risk if risk > 0 else 0.0
        
        # Create response
        response = SignalResponse(
            id=db_signal.id,
            **signal_data
        )
        
        if request.include_indicators:
            response.indicators = signal_data.get('indicators', {})
        
        logger.info(f"Signal generated for {request.symbol}: {signal_data['recommendation']}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating signal for {request.symbol}: {e}")
        return SignalResponse(
            symbol=request.symbol.upper(),
            timestamp=datetime.now().isoformat(),
            recommendation="HOLD",
            confidence=0.0,
            current_price=0.0,
            entry_price=0.0,
            stop_loss=0.0,
            target_price=0.0,
            sentiment=0.0,
            error=str(e)
        )

# Watchlist endpoints
@app.post("/watchlist", response_model=WatchlistItemResponse)
async def add_to_watchlist(
    item: WatchlistItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add symbol to user's watchlist"""
    # Check if already exists
    existing = db.query(WatchlistItem).filter(
        WatchlistItem.user_id == current_user.id,
        WatchlistItem.symbol == item.symbol.upper(),
        WatchlistItem.is_active == True
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Symbol already in watchlist")
    
    # Create watchlist item
    db_item = WatchlistItem(
        user_id=current_user.id,
        symbol=item.symbol.upper(),
        signal_preferences=item.signal_preferences,
        notes=item.notes
    )
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    logger.info(f"Added {item.symbol} to watchlist for user {current_user.email}")
    
    return WatchlistItemResponse.from_orm(db_item)

@app.get("/watchlist", response_model=List[WatchlistItemResponse])
async def get_watchlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's watchlist"""
    items = db.query(WatchlistItem).filter(
        WatchlistItem.user_id == current_user.id,
        WatchlistItem.is_active == True
    ).order_by(WatchlistItem.created_at.desc()).all()
    
    return [WatchlistItemResponse.from_orm(item) for item in items]

@app.delete("/watchlist/{symbol}")
async def remove_from_watchlist(
    symbol: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove symbol from watchlist"""
    item = db.query(WatchlistItem).filter(
        WatchlistItem.user_id == current_user.id,
        WatchlistItem.symbol == symbol.upper(),
        WatchlistItem.is_active == True
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Symbol not found in watchlist")
    
    item.is_active = False
    db.commit()
    
    logger.info(f"Removed {symbol} from watchlist for user {current_user.email}")
    
    return {"message": f"Removed {symbol} from watchlist"}

# Trade confirmation endpoints
@app.post("/trade-confirmation", response_model=TradeConfirmationResponse)
async def confirm_trade(
    confirmation: TradeConfirmationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Confirm trade execution"""
    # Get signal
    signal = db.query(Signal).filter(Signal.id == confirmation.signal_id).first()
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    
    # Calculate P&L if executed
    pnl = None
    pnl_percentage = None
    if confirmation.executed and confirmation.execution_price and confirmation.quantity:
        pnl, pnl_percentage = calculate_pnl(
            signal.entry_price,
            confirmation.execution_price,
            confirmation.quantity,
            signal.recommendation
        )
    
    # Create trade confirmation
    db_confirmation = TradeConfirmation(
        user_id=current_user.id,
        signal_id=confirmation.signal_id,
        symbol=signal.symbol,
        recommendation=signal.recommendation,
        executed=confirmation.executed,
        execution_price=confirmation.execution_price,
        quantity=confirmation.quantity,
        execution_time=datetime.utcnow() if confirmation.executed else None,
        pnl=pnl,
        pnl_percentage=pnl_percentage,
        notes=confirmation.notes,
        user_rating=confirmation.user_rating
    )
    
    db.add(db_confirmation)
    db.commit()
    db.refresh(db_confirmation)
    
    logger.info(f"Trade confirmation recorded for {signal.symbol} by user {current_user.email}")
    
    return TradeConfirmationResponse.from_orm(db_confirmation)

@app.get("/trade-confirmations", response_model=List[TradeConfirmationResponse])
async def get_trade_confirmations(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's trade confirmations"""
    confirmations = db.query(TradeConfirmation).filter(
        TradeConfirmation.user_id == current_user.id
    ).order_by(TradeConfirmation.created_at.desc()).limit(limit).all()
    
    return [TradeConfirmationResponse.from_orm(conf) for conf in confirmations]

# Dashboard endpoint
@app.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user dashboard statistics"""
    # Get user's trade confirmations
    confirmations = db.query(TradeConfirmation).filter(
        TradeConfirmation.user_id == current_user.id
    ).all()
    
    total_signals = len(confirmations)
    executed_trades = len([c for c in confirmations if c.executed])
    
    # Calculate win rate
    profitable_trades = len([c for c in confirmations if c.pnl and c.pnl > 0])
    win_rate = (profitable_trades / executed_trades * 100) if executed_trades > 0 else 0
    
    # Calculate total P&L
    total_pnl = sum([c.pnl for c in confirmations if c.pnl]) or 0
    
    # Calculate average confidence (from signals)
    signal_ids = [c.signal_id for c in confirmations]
    if signal_ids:
        signals = db.query(Signal).filter(Signal.id.in_(signal_ids)).all()
        avg_confidence = sum([s.confidence for s in signals]) / len(signals) if signals else 0
    else:
        avg_confidence = 0
    
    # Best performing symbol
    symbol_pnl = {}
    for conf in confirmations:
        if conf.pnl:
            symbol_pnl[conf.symbol] = symbol_pnl.get(conf.symbol, 0) + conf.pnl
    
    best_performing_symbol = max(symbol_pnl, key=symbol_pnl.get) if symbol_pnl else None
    
    # Recent activity
    recent_confirmations = db.query(TradeConfirmation).filter(
        TradeConfirmation.user_id == current_user.id
    ).order_by(TradeConfirmation.created_at.desc()).limit(5).all()
    
    recent_activity = []
    for conf in recent_confirmations:
        recent_activity.append({
            "symbol": conf.symbol,
            "recommendation": conf.recommendation,
            "executed": conf.executed,
            "pnl": conf.pnl,
            "created_at": conf.created_at.isoformat()
        })
    
    return DashboardStats(
        total_signals=total_signals,
        executed_trades=executed_trades,
        win_rate=win_rate,
        total_pnl=total_pnl,
        avg_confidence=avg_confidence,
        best_performing_symbol=best_performing_symbol,
        recent_activity=recent_activity
    )

# User Preferences Endpoints
@app.get("/user/preferences", response_model=UserPreferencesResponse)
async def get_user_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's trading preferences"""
    try:
        preferences_service = get_preferences_service(db)
        preferences = preferences_service.get_or_create_preferences(current_user.id)
        
        logger.info(f"Retrieved preferences for user {current_user.id}")
        return preferences
        
    except Exception as e:
        logger.error(f"Error retrieving preferences for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve preferences"
        )

@app.put("/user/preferences", response_model=PreferencesUpdateResponse)
async def update_user_preferences(
    preferences_update: UserPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's trading preferences"""
    try:
        preferences_service = get_preferences_service(db)
        
        # Validate strategy availability if strategy is being updated
        if preferences_update.strategy is not None:
            if not preferences_service.validate_strategy_availability(preferences_update.strategy):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Strategy '{preferences_update.strategy}' is not currently available"
                )
        
        updated_preferences = preferences_service.update_preferences(
            current_user.id, 
            preferences_update
        )
        
        logger.info(f"Updated preferences for user {current_user.id}")
        
        return PreferencesUpdateResponse(
            message="Preferences updated successfully",
            preferences=updated_preferences
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating preferences for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update preferences"
        )

@app.get("/user/preferences/strategies", response_model=AvailableStrategiesResponse)
async def get_available_strategies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of available trading strategies"""
    try:
        preferences_service = get_preferences_service(db)
        strategies = preferences_service.get_available_strategies()
        
        # Get current user's strategy
        preferences = preferences_service.get_or_create_preferences(current_user.id)
        
        return AvailableStrategiesResponse(
            strategies=strategies,
            current_strategy=preferences.strategy
        )
        
    except Exception as e:
        logger.error(f"Error retrieving strategies for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve strategies"
        )

@app.get("/user/preferences/risk-profiles", response_model=RiskProfilesResponse)
async def get_risk_profiles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of available risk profiles"""
    try:
        preferences_service = get_preferences_service(db)
        risk_profiles = preferences_service.get_risk_profiles()
        
        # Get current user's risk appetite
        preferences = preferences_service.get_or_create_preferences(current_user.id)
        
        return RiskProfilesResponse(
            risk_profiles=risk_profiles,
            current_risk_appetite=preferences.risk_appetite
        )
        
    except Exception as e:
        logger.error(f"Error retrieving risk profiles for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve risk profiles"
        )

@app.post("/user/preferences/apply-risk-profile")
async def apply_risk_profile(
    risk_appetite: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Apply default settings based on selected risk profile"""
    try:
        # Validate risk appetite
        valid_risk_levels = ['low', 'moderate', 'high']
        if risk_appetite not in valid_risk_levels:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid risk appetite. Must be one of: {valid_risk_levels}"
            )
        
        preferences_service = get_preferences_service(db)
        updated_preferences = preferences_service.apply_risk_profile_defaults(
            current_user.id, 
            risk_appetite
        )
        
        logger.info(f"Applied risk profile '{risk_appetite}' for user {current_user.id}")
        
        return PreferencesUpdateResponse(
            message=f"Risk profile '{risk_appetite}' applied successfully",
            preferences=updated_preferences
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error applying risk profile for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to apply risk profile"
        )

@app.get("/user/preferences/summary")
async def get_preferences_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive preferences summary with recommendations"""
    try:
        preferences_service = get_preferences_service(db)
        summary = preferences_service.get_preferences_summary(current_user.id)
        
        return {
            "preferences": summary["preferences"],
            "current_strategy": summary["current_strategy"],
            "current_risk_profile": summary["current_risk_profile"],
            "available_strategies": summary["available_strategies"],
            "risk_profiles": summary["risk_profiles"],
            "recommendations": summary["recommendations"]
        }
        
    except Exception as e:
        logger.error(f"Error retrieving preferences summary for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve preferences summary"
        )

# Legacy endpoints (for backward compatibility)
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "SentimentTrade Enhanced API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    config_validation = config.validate_config()
    
    return {
        "status": "healthy" if config_validation['valid'] else "degraded",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "features": {
            "user_auth": True,
            "watchlist": True,
            "trade_tracking": True,
            "dashboard": True,
            "preferences": True
        },
        "config_valid": config_validation['valid'],
        "missing_keys": config_validation['missing_keys'],
        "warnings": config_validation['warnings']
    }

@app.get("/symbols/popular", response_model=List[str])
async def get_popular_symbols():
    """Get popular trading symbols"""
    return [
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
        "META", "NVDA", "NFLX", "AMD", "INTC",
        "BABA", "DIS", "PYPL", "ADBE", "CRM"
    ]

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting SentimentTrade Enhanced API...")
    print("📱 Features: User Auth, Watchlist, Trade Tracking, Dashboard")
    print("📚 API Documentation: http://localhost:8000/docs")
    
    uvicorn.run(
        "main_enhanced:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
