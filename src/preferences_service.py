"""
User preferences service
Handles business logic for trading preferences management
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import UserPreferences, User
from preferences_models import (
    UserPreferencesCreate, 
    UserPreferencesUpdate, 
    StrategyInfo, 
    RiskProfileInfo
)
from typing import Optional, List, Dict, Any
from datetime import datetime

class PreferencesService:
    """Service class for managing user preferences"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_preferences(self, user_id: int) -> Optional[UserPreferences]:
        """Get user preferences by user ID"""
        return self.db.query(UserPreferences).filter(
            UserPreferences.user_id == user_id
        ).first()
    
    def create_default_preferences(self, user_id: int) -> UserPreferences:
        """Create default preferences for a new user"""
        preferences = UserPreferences(
            user_id=user_id,
            risk_appetite="moderate",
            strategy="default",
            min_confidence=0.7,
            max_daily_signals=10,
            notification_enabled=True,
            email_alerts=True,
            push_notifications=True,
            signal_threshold=0.8,
            auto_execute_trades=False,
            max_position_size=1000.0,
            stop_loss_percentage=0.05,
            take_profit_percentage=0.15
        )
        
        try:
            self.db.add(preferences)
            self.db.commit()
            self.db.refresh(preferences)
            return preferences
        except IntegrityError:
            self.db.rollback()
            # If preferences already exist, return existing ones
            return self.get_user_preferences(user_id)
    
    def get_or_create_preferences(self, user_id: int) -> UserPreferences:
        """Get existing preferences or create default ones"""
        preferences = self.get_user_preferences(user_id)
        if not preferences:
            preferences = self.create_default_preferences(user_id)
        return preferences
    
    def update_preferences(
        self, 
        user_id: int, 
        preferences_update: UserPreferencesUpdate
    ) -> Optional[UserPreferences]:
        """Update user preferences"""
        preferences = self.get_or_create_preferences(user_id)
        
        # Update only provided fields
        update_data = preferences_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(preferences, field, value)
        
        preferences.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            self.db.refresh(preferences)
            return preferences
        except Exception as e:
            self.db.rollback()
            raise e
    
    def delete_preferences(self, user_id: int) -> bool:
        """Delete user preferences"""
        preferences = self.get_user_preferences(user_id)
        if preferences:
            self.db.delete(preferences)
            self.db.commit()
            return True
        return False
    
    def get_available_strategies(self) -> List[StrategyInfo]:
        """Get list of available trading strategies"""
        strategies = [
            StrategyInfo(
                name="default",
                display_name="Default Strategy",
                description="Balanced approach with moderate risk and steady returns",
                risk_level="moderate",
                available=True
            ),
            StrategyInfo(
                name="aggressive",
                display_name="Aggressive Growth",
                description="Higher risk strategy targeting maximum returns",
                risk_level="high",
                available=False  # Coming soon
            ),
            StrategyInfo(
                name="conservative",
                display_name="Conservative",
                description="Lower risk strategy focusing on capital preservation",
                risk_level="low",
                available=False  # Coming soon
            ),
            StrategyInfo(
                name="momentum",
                display_name="Momentum Trading",
                description="Follow market trends and momentum indicators",
                risk_level="moderate",
                available=False  # Coming soon
            )
        ]
        return strategies
    
    def get_risk_profiles(self) -> List[RiskProfileInfo]:
        """Get list of available risk profiles"""
        profiles = [
            RiskProfileInfo(
                name="low",
                display_name="Conservative",
                description="Lower risk, steady returns with capital preservation focus",
                recommended_confidence=0.8,
                max_daily_signals=5
            ),
            RiskProfileInfo(
                name="moderate",
                display_name="Moderate",
                description="Balanced risk and reward with diversified approach",
                recommended_confidence=0.7,
                max_daily_signals=10
            ),
            RiskProfileInfo(
                name="high",
                display_name="Aggressive",
                description="Higher risk tolerance for maximum growth potential",
                recommended_confidence=0.6,
                max_daily_signals=20
            )
        ]
        return profiles
    
    def validate_strategy_availability(self, strategy: str) -> bool:
        """Check if a strategy is currently available"""
        available_strategies = [s.name for s in self.get_available_strategies() if s.available]
        return strategy in available_strategies
    
    def get_strategy_recommendations(self, risk_appetite: str) -> Dict[str, Any]:
        """Get strategy recommendations based on risk appetite"""
        recommendations = {
            "low": {
                "recommended_strategy": "default",  # Conservative not available yet
                "min_confidence": 0.8,
                "max_daily_signals": 5,
                "stop_loss_percentage": 0.03,
                "take_profit_percentage": 0.10
            },
            "moderate": {
                "recommended_strategy": "default",
                "min_confidence": 0.7,
                "max_daily_signals": 10,
                "stop_loss_percentage": 0.05,
                "take_profit_percentage": 0.15
            },
            "high": {
                "recommended_strategy": "default",  # Aggressive not available yet
                "min_confidence": 0.6,
                "max_daily_signals": 20,
                "stop_loss_percentage": 0.07,
                "take_profit_percentage": 0.25
            }
        }
        return recommendations.get(risk_appetite, recommendations["moderate"])
    
    def apply_risk_profile_defaults(self, user_id: int, risk_appetite: str) -> UserPreferences:
        """Apply default settings based on risk profile"""
        recommendations = self.get_strategy_recommendations(risk_appetite)
        
        update_data = UserPreferencesUpdate(
            risk_appetite=risk_appetite,
            strategy=recommendations["recommended_strategy"],
            min_confidence=recommendations["min_confidence"],
            max_daily_signals=recommendations["max_daily_signals"],
            stop_loss_percentage=recommendations["stop_loss_percentage"],
            take_profit_percentage=recommendations["take_profit_percentage"]
        )
        
        return self.update_preferences(user_id, update_data)
    
    def get_preferences_summary(self, user_id: int) -> Dict[str, Any]:
        """Get a summary of user preferences for display"""
        preferences = self.get_or_create_preferences(user_id)
        strategies = self.get_available_strategies()
        risk_profiles = self.get_risk_profiles()
        
        # Find current strategy and risk profile info
        current_strategy = next((s for s in strategies if s.name == preferences.strategy), None)
        current_risk_profile = next((r for r in risk_profiles if r.name == preferences.risk_appetite), None)
        
        return {
            "preferences": preferences,
            "current_strategy": current_strategy,
            "current_risk_profile": current_risk_profile,
            "available_strategies": strategies,
            "risk_profiles": risk_profiles,
            "recommendations": self.get_strategy_recommendations(preferences.risk_appetite)
        }

def get_preferences_service(db: Session) -> PreferencesService:
    """Factory function to create preferences service"""
    return PreferencesService(db)
