# User Preferences System

Complete backend implementation for user trading preferences in SentimentTrade, integrating seamlessly with the mobile app settings screen.

## 🎯 Overview

The user preferences system allows users to customize their trading experience through:
- **Risk Appetite Selection**: Conservative, Moderate, or Aggressive
- **Trading Strategy Selection**: Currently "Default" with more strategies coming soon
- **Signal Settings**: Minimum confidence levels and daily signal limits
- **Notification Preferences**: Email alerts and push notifications
- **Advanced Settings**: Stop-loss percentages, take-profit targets, and position sizing

## 📊 Database Schema

### UserPreferences Table
```sql
CREATE TABLE user_preferences (
    id INTEGER PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id),
    risk_appetite VARCHAR DEFAULT 'moderate',  -- low, moderate, high
    strategy VARCHAR DEFAULT 'default',        -- default, aggressive, conservative, momentum
    min_confidence FLOAT DEFAULT 0.7,         -- 0.5-0.95
    max_daily_signals INTEGER DEFAULT 10,     -- 5-50
    notification_enabled BOOLEAN DEFAULT TRUE,
    email_alerts BOOLEAN DEFAULT TRUE,
    push_notifications BOOLEAN DEFAULT TRUE,
    signal_threshold FLOAT DEFAULT 0.8,       -- notification threshold
    auto_execute_trades BOOLEAN DEFAULT FALSE, -- future feature
    max_position_size FLOAT DEFAULT 1000.0,   -- USD
    stop_loss_percentage FLOAT DEFAULT 0.05,  -- 5%
    take_profit_percentage FLOAT DEFAULT 0.15, -- 15%
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## 🔌 API Endpoints

### Get User Preferences
```http
GET /user/preferences
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
    "id": 1,
    "user_id": 123,
    "risk_appetite": "moderate",
    "strategy": "default",
    "min_confidence": 0.7,
    "max_daily_signals": 10,
    "notification_enabled": true,
    "email_alerts": true,
    "push_notifications": true,
    "signal_threshold": 0.8,
    "auto_execute_trades": false,
    "max_position_size": 1000.0,
    "stop_loss_percentage": 0.05,
    "take_profit_percentage": 0.15,
    "created_at": "2024-07-12T03:00:00Z",
    "updated_at": "2024-07-12T03:00:00Z"
}
```

### Update User Preferences
```http
PUT /user/preferences
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
    "risk_appetite": "high",
    "min_confidence": 0.6,
    "max_daily_signals": 20
}
```

**Response:**
```json
{
    "message": "Preferences updated successfully",
    "preferences": { /* updated preferences object */ }
}
```

### Get Available Strategies
```http
GET /user/preferences/strategies
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
    "strategies": [
        {
            "name": "default",
            "display_name": "Default Strategy",
            "description": "Balanced approach with moderate risk",
            "risk_level": "moderate",
            "available": true
        },
        {
            "name": "aggressive",
            "display_name": "Aggressive Growth",
            "description": "Higher risk, higher potential returns",
            "risk_level": "high",
            "available": false
        }
    ],
    "current_strategy": "default"
}
```

### Get Risk Profiles
```http
GET /user/preferences/risk-profiles
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
    "risk_profiles": [
        {
            "name": "low",
            "display_name": "Conservative",
            "description": "Lower risk, steady returns",
            "recommended_confidence": 0.8,
            "max_daily_signals": 5
        },
        {
            "name": "moderate",
            "display_name": "Moderate",
            "description": "Balanced risk and reward",
            "recommended_confidence": 0.7,
            "max_daily_signals": 10
        },
        {
            "name": "high",
            "display_name": "Aggressive",
            "description": "Higher risk tolerance",
            "recommended_confidence": 0.6,
            "max_daily_signals": 20
        }
    ],
    "current_risk_appetite": "moderate"
}
```

### Apply Risk Profile Defaults
```http
POST /user/preferences/apply-risk-profile
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
    "risk_appetite": "high"
}
```

### Get Preferences Summary
```http
GET /user/preferences/summary
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
    "preferences": { /* full preferences object */ },
    "current_strategy": { /* strategy info */ },
    "current_risk_profile": { /* risk profile info */ },
    "available_strategies": [ /* all strategies */ ],
    "risk_profiles": [ /* all risk profiles */ ],
    "recommendations": { /* recommended settings */ }
}
```

## 🏗️ Architecture

### Components

1. **Database Models** (`src/database.py`)
   - `UserPreferences` - SQLAlchemy model
   - Relationship with `User` model

2. **Pydantic Models** (`src/preferences_models.py`)
   - Request/response validation
   - Type safety and documentation

3. **Business Logic** (`src/preferences_service.py`)
   - `PreferencesService` class
   - CRUD operations and business rules

4. **API Endpoints** (`api/main_enhanced.py`)
   - FastAPI routes with authentication
   - Error handling and validation

### Service Layer Methods

```python
class PreferencesService:
    def get_user_preferences(user_id: int) -> UserPreferences
    def create_default_preferences(user_id: int) -> UserPreferences
    def get_or_create_preferences(user_id: int) -> UserPreferences
    def update_preferences(user_id: int, update: UserPreferencesUpdate) -> UserPreferences
    def get_available_strategies() -> List[StrategyInfo]
    def get_risk_profiles() -> List[RiskProfileInfo]
    def apply_risk_profile_defaults(user_id: int, risk_appetite: str) -> UserPreferences
    def get_preferences_summary(user_id: int) -> Dict[str, Any]
```

## 📱 Mobile App Integration

The mobile app's settings screen integrates with these endpoints:

### Flutter API Service
```dart
// lib/services/api_service.dart
Future<Map<String, dynamic>> getTradingPreferences()
Future<Map<String, dynamic>> updateTradingPreferences(Map<String, dynamic> preferences)
```

### Settings Screen Features
- **Trading Strategy Selector**: Radio buttons with "Coming Soon" badges
- **Risk Appetite Selector**: Conservative, Moderate, Aggressive options
- **Signal Settings**: Sliders for confidence and daily limits
- **Real-time Updates**: Immediate save with success/error feedback

## 🎛️ Default Settings by Risk Profile

### Conservative (Low Risk)
- **Min Confidence**: 80%
- **Max Daily Signals**: 5
- **Stop Loss**: 3%
- **Take Profit**: 10%

### Moderate (Balanced)
- **Min Confidence**: 70%
- **Max Daily Signals**: 10
- **Stop Loss**: 5%
- **Take Profit**: 15%

### Aggressive (High Risk)
- **Min Confidence**: 60%
- **Max Daily Signals**: 20
- **Stop Loss**: 7%
- **Take Profit**: 25%

## 🚀 Future Strategy Expansion

The system is designed to easily add new trading strategies:

### Adding a New Strategy

1. **Update Available Strategies**:
   ```python
   # In preferences_service.py
   StrategyInfo(
       name="momentum",
       display_name="Momentum Trading",
       description="Follow market trends",
       risk_level="moderate",
       available=True  # Enable when ready
   )
   ```

2. **Implement Strategy Logic**:
   ```python
   # In ai_trade_signal_enhanced.py
   def generate_momentum_signal(self, symbol: str):
       # Strategy-specific logic
   ```

3. **Update Mobile App**:
   ```dart
   // Remove isComingSoon: true from strategy option
   _buildStrategyOption('momentum', 'Momentum Trading', 
       'Follow market trends', isComingSoon: false)
   ```

## 🧪 Testing

### Run Preferences Tests
```bash
# Test database and service layer
python test_preferences.py

# Demo complete functionality
python demo_preferences.py

# Test with API server running
python api/main_enhanced.py &
python test_preferences.py  # Select 'y' for API tests
```

### Test Results
- ✅ Database models and relationships
- ✅ Preferences service business logic
- ✅ API endpoints with authentication
- ✅ Mobile app integration points
- ✅ Default preference creation
- ✅ Risk profile application
- ✅ Strategy availability validation

## 📊 Usage Analytics

The preferences system enables tracking:
- **Popular Risk Profiles**: Which risk levels users prefer
- **Strategy Adoption**: When new strategies are released
- **Setting Changes**: How users adjust their preferences over time
- **Signal Effectiveness**: Performance by preference settings

## 🔒 Security & Validation

### Input Validation
- **Risk Appetite**: Must be 'low', 'moderate', or 'high'
- **Strategy**: Must be available (not "coming soon")
- **Confidence Range**: 0.5 to 0.95 (50% to 95%)
- **Daily Signals**: 5 to 50 signals maximum
- **Percentages**: Reasonable ranges for stop-loss and take-profit

### Authentication
- All endpoints require valid JWT token
- User can only access/modify their own preferences
- Automatic preference creation on first access

## 🎉 Success Metrics

The preferences system successfully provides:
- ✅ **Complete Mobile Integration**: All settings screens functional
- ✅ **Scalable Architecture**: Easy to add new strategies and options
- ✅ **User Personalization**: Tailored trading experience
- ✅ **Risk Management**: Appropriate defaults by risk profile
- ✅ **Future-Ready**: Framework for advanced features

This preferences system transforms SentimentTrade from a one-size-fits-all solution into a personalized trading platform that adapts to each user's risk tolerance and trading style!
