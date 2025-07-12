"""
Pydantic models for user preferences API
Handles request/response validation for trading preferences
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class UserPreferencesBase(BaseModel):
    """Base model for user preferences"""
    risk_appetite: str = Field(default="moderate", description="Risk appetite level")
    strategy: str = Field(default="default", description="Trading strategy")
    min_confidence: float = Field(default=0.7, ge=0.5, le=0.95, description="Minimum signal confidence")
    max_daily_signals: int = Field(default=10, ge=5, le=50, description="Maximum daily signals")
    notification_enabled: bool = Field(default=True, description="Enable notifications")
    email_alerts: bool = Field(default=True, description="Enable email alerts")
    push_notifications: bool = Field(default=True, description="Enable push notifications")
    signal_threshold: float = Field(default=0.8, ge=0.5, le=0.95, description="Notification threshold")
    auto_execute_trades: bool = Field(default=False, description="Auto-execute trades")
    max_position_size: float = Field(default=1000.0, ge=100.0, le=100000.0, description="Max position size")
    stop_loss_percentage: float = Field(default=0.05, ge=0.01, le=0.5, description="Stop loss percentage")
    take_profit_percentage: float = Field(default=0.15, ge=0.05, le=1.0, description="Take profit percentage")

    @validator('risk_appetite')
    def validate_risk_appetite(cls, v):
        allowed_values = ['low', 'moderate', 'high']
        if v not in allowed_values:
            raise ValueError(f'risk_appetite must be one of {allowed_values}')
        return v

    @validator('strategy')
    def validate_strategy(cls, v):
        allowed_values = ['default', 'aggressive', 'conservative', 'momentum']
        if v not in allowed_values:
            raise ValueError(f'strategy must be one of {allowed_values}')
        return v

class UserPreferencesCreate(UserPreferencesBase):
    """Model for creating user preferences"""
    pass

class UserPreferencesUpdate(BaseModel):
    """Model for updating user preferences (all fields optional)"""
    risk_appetite: Optional[str] = None
    strategy: Optional[str] = None
    min_confidence: Optional[float] = Field(None, ge=0.5, le=0.95)
    max_daily_signals: Optional[int] = Field(None, ge=5, le=50)
    notification_enabled: Optional[bool] = None
    email_alerts: Optional[bool] = None
    push_notifications: Optional[bool] = None
    signal_threshold: Optional[float] = Field(None, ge=0.5, le=0.95)
    auto_execute_trades: Optional[bool] = None
    max_position_size: Optional[float] = Field(None, ge=100.0, le=100000.0)
    stop_loss_percentage: Optional[float] = Field(None, ge=0.01, le=0.5)
    take_profit_percentage: Optional[float] = Field(None, ge=0.05, le=1.0)

    @validator('risk_appetite')
    def validate_risk_appetite(cls, v):
        if v is not None:
            allowed_values = ['low', 'moderate', 'high']
            if v not in allowed_values:
                raise ValueError(f'risk_appetite must be one of {allowed_values}')
        return v

    @validator('strategy')
    def validate_strategy(cls, v):
        if v is not None:
            allowed_values = ['default', 'aggressive', 'conservative', 'momentum']
            if v not in allowed_values:
                raise ValueError(f'strategy must be one of {allowed_values}')
        return v

class UserPreferencesResponse(UserPreferencesBase):
    """Model for user preferences response"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PreferencesUpdateResponse(BaseModel):
    """Response model for preferences update"""
    message: str
    preferences: UserPreferencesResponse

class StrategyInfo(BaseModel):
    """Information about available trading strategies"""
    name: str
    display_name: str
    description: str
    risk_level: str
    available: bool

class AvailableStrategiesResponse(BaseModel):
    """Response model for available strategies"""
    strategies: List[StrategyInfo]
    current_strategy: str

class RiskProfileInfo(BaseModel):
    """Information about risk profiles"""
    name: str
    display_name: str
    description: str
    recommended_confidence: float
    max_daily_signals: int

class RiskProfilesResponse(BaseModel):
    """Response model for risk profiles"""
    risk_profiles: List[RiskProfileInfo]
    current_risk_appetite: str
