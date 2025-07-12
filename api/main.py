"""
FastAPI REST API for SentimentTrade Mobile App
Provides endpoints for mobile applications to get trading signals
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import sys
import os
from pathlib import Path
import asyncio
from datetime import datetime, timedelta
import logging

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from ai_trade_signal_enhanced import run_agent, TradingSignalGenerator
from config import config
from logger import logger

# Configure API logging
logging.basicConfig(level=logging.INFO)
api_logger = logging.getLogger("SentimentTradeAPI")

# FastAPI app
app = FastAPI(
    title="SentimentTrade API",
    description="REST API for AI-driven trading signals",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for mobile apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class SignalRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol (e.g., AAPL, MSFT)", example="AAPL")
    include_indicators: bool = Field(True, description="Include technical indicators in response")
    
class SignalResponse(BaseModel):
    symbol: str
    timestamp: str
    recommendation: str  # BUY, SELL, HOLD
    confidence: float  # 0.0 to 1.0
    current_price: float
    entry_price: float
    stop_loss: float
    target_price: float
    sentiment: float  # -1.0 to 1.0
    indicators: Optional[Dict[str, Any]] = None
    risk_reward_ratio: Optional[float] = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    config_valid: bool
    missing_keys: List[str]
    warnings: List[str]

class MultiSignalRequest(BaseModel):
    symbols: List[str] = Field(..., description="List of stock symbols", example=["AAPL", "MSFT", "GOOGL"])
    include_indicators: bool = Field(True, description="Include technical indicators in response")

class MultiSignalResponse(BaseModel):
    signals: List[SignalResponse]
    timestamp: str
    total_symbols: int
    successful_signals: int
    failed_signals: int

# Global signal generator instance
signal_generator = None

def get_signal_generator():
    """Get or create signal generator instance"""
    global signal_generator
    if signal_generator is None:
        signal_generator = TradingSignalGenerator()
    return signal_generator

def calculate_risk_reward_ratio(entry_price: float, stop_loss: float, target_price: float, recommendation: str) -> float:
    """Calculate risk/reward ratio"""
    try:
        if recommendation == "BUY":
            risk = abs(entry_price - stop_loss)
            reward = abs(target_price - entry_price)
        elif recommendation == "SELL":
            risk = abs(stop_loss - entry_price)
            reward = abs(entry_price - target_price)
        else:
            return 0.0
        
        return reward / risk if risk > 0 else 0.0
    except:
        return 0.0

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "SentimentTrade API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Check configuration
        config_validation = config.validate_config()
        
        return HealthResponse(
            status="healthy" if config_validation['valid'] else "degraded",
            timestamp=datetime.now().isoformat(),
            version="1.0.0",
            config_valid=config_validation['valid'],
            missing_keys=config_validation['missing_keys'],
            warnings=config_validation['warnings']
        )
    except Exception as e:
        api_logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.post("/signal", response_model=SignalResponse)
async def get_trading_signal(request: SignalRequest):
    """Get trading signal for a single symbol"""
    try:
        api_logger.info(f"Generating signal for {request.symbol}")
        
        # Validate symbol
        symbol = request.symbol.upper().strip()
        if not symbol or len(symbol) > 10:
            raise HTTPException(status_code=400, detail="Invalid symbol")
        
        # Generate signal
        generator = get_signal_generator()
        signal_data = generator.generate_signal(symbol)
        
        # Calculate additional metrics
        risk_reward = calculate_risk_reward_ratio(
            signal_data['entry_price'],
            signal_data['stop_loss'],
            signal_data['target_price'],
            signal_data['recommendation']
        )
        
        # Prepare response
        response = SignalResponse(
            symbol=signal_data['symbol'],
            timestamp=signal_data['timestamp'],
            recommendation=signal_data['recommendation'],
            confidence=signal_data['confidence'],
            current_price=signal_data['current_price'],
            entry_price=signal_data['entry_price'],
            stop_loss=signal_data['stop_loss'],
            target_price=signal_data['target_price'],
            sentiment=signal_data['sentiment'],
            risk_reward_ratio=risk_reward,
            error=signal_data.get('error')
        )
        
        # Include indicators if requested
        if request.include_indicators:
            response.indicators = signal_data.get('indicators', {})
        
        api_logger.info(f"Signal generated for {symbol}: {signal_data['recommendation']} (confidence: {signal_data['confidence']:.2%})")
        
        return response
        
    except Exception as e:
        api_logger.error(f"Error generating signal for {request.symbol}: {e}")
        
        # Return error response instead of raising HTTP exception
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
            risk_reward_ratio=0.0,
            error=str(e)
        )

@app.post("/signals", response_model=MultiSignalResponse)
async def get_multiple_signals(request: MultiSignalRequest):
    """Get trading signals for multiple symbols"""
    try:
        api_logger.info(f"Generating signals for {len(request.symbols)} symbols")
        
        # Validate symbols
        symbols = [s.upper().strip() for s in request.symbols if s.strip()]
        if not symbols or len(symbols) > 20:  # Limit to 20 symbols
            raise HTTPException(status_code=400, detail="Invalid symbols list (max 20)")
        
        signals = []
        successful = 0
        failed = 0
        
        generator = get_signal_generator()
        
        # Generate signals for each symbol
        for symbol in symbols:
            try:
                signal_data = generator.generate_signal(symbol)
                
                # Calculate risk/reward ratio
                risk_reward = calculate_risk_reward_ratio(
                    signal_data['entry_price'],
                    signal_data['stop_loss'],
                    signal_data['target_price'],
                    signal_data['recommendation']
                )
                
                # Create response
                signal_response = SignalResponse(
                    symbol=signal_data['symbol'],
                    timestamp=signal_data['timestamp'],
                    recommendation=signal_data['recommendation'],
                    confidence=signal_data['confidence'],
                    current_price=signal_data['current_price'],
                    entry_price=signal_data['entry_price'],
                    stop_loss=signal_data['stop_loss'],
                    target_price=signal_data['target_price'],
                    sentiment=signal_data['sentiment'],
                    risk_reward_ratio=risk_reward,
                    error=signal_data.get('error')
                )
                
                # Include indicators if requested
                if request.include_indicators:
                    signal_response.indicators = signal_data.get('indicators', {})
                
                signals.append(signal_response)
                
                if signal_data.get('error'):
                    failed += 1
                else:
                    successful += 1
                    
            except Exception as e:
                api_logger.error(f"Error generating signal for {symbol}: {e}")
                
                # Add error signal
                signals.append(SignalResponse(
                    symbol=symbol,
                    timestamp=datetime.now().isoformat(),
                    recommendation="HOLD",
                    confidence=0.0,
                    current_price=0.0,
                    entry_price=0.0,
                    stop_loss=0.0,
                    target_price=0.0,
                    sentiment=0.0,
                    risk_reward_ratio=0.0,
                    error=str(e)
                ))
                failed += 1
        
        return MultiSignalResponse(
            signals=signals,
            timestamp=datetime.now().isoformat(),
            total_symbols=len(symbols),
            successful_signals=successful,
            failed_signals=failed
        )
        
    except Exception as e:
        api_logger.error(f"Error generating multiple signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/config", response_model=Dict[str, Any])
async def get_config():
    """Get current configuration (without sensitive data)"""
    try:
        validation = config.validate_config()
        
        return {
            "stock_symbol": config.STOCK_SYMBOL,
            "position_size": config.POSITION_SIZE,
            "rsi_period": config.RSI_PERIOD,
            "rsi_oversold": config.RSI_OVERSOLD,
            "rsi_overbought": config.RSI_OVERBOUGHT,
            "macd_fast": config.MACD_FAST,
            "macd_slow": config.MACD_SLOW,
            "macd_signal": config.MACD_SIGNAL,
            "atr_period": config.ATR_PERIOD,
            "atr_stop_multiplier": config.ATR_STOP_MULTIPLIER,
            "atr_target_multiplier": config.ATR_TARGET_MULTIPLIER,
            "sentiment_bullish_threshold": config.SENTIMENT_BULLISH_THRESHOLD,
            "sentiment_bearish_threshold": config.SENTIMENT_BEARISH_THRESHOLD,
            "trading_start_hour": config.TRADING_START_HOUR,
            "trading_end_hour": config.TRADING_END_HOUR,
            "max_daily_loss": config.MAX_DAILY_LOSS,
            "config_valid": validation['valid'],
            "missing_keys": validation['missing_keys'],
            "warnings": validation['warnings']
        }
    except Exception as e:
        api_logger.error(f"Error getting config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/symbols/popular", response_model=List[str])
async def get_popular_symbols():
    """Get list of popular trading symbols"""
    return [
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
        "META", "NVDA", "NFLX", "AMD", "INTC",
        "BABA", "DIS", "PYPL", "ADBE", "CRM",
        "ORCL", "IBM", "UBER", "LYFT", "SNAP"
    ]

if __name__ == "__main__":
    import uvicorn
    
    # Check configuration on startup
    validation = config.validate_config()
    if not validation['valid']:
        print("⚠️  Warning: Missing required API keys:")
        for key in validation['missing_keys']:
            print(f"   - {key}")
        print("API will run but signals may not work properly without API keys.")
    
    print("🚀 Starting SentimentTrade API...")
    print("📱 Mobile app can connect to: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
