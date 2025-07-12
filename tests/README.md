# SentimentTrade Test Suite

Organized testing structure for the SentimentTrade platform.

## 📁 Directory Structure

```
tests/
├── unit/                    # Individual component tests
│   ├── test_preferences.py  # User preferences functionality
│   └── test_simple_refactor.py # Basic component validation
├── integration/             # Cross-component integration tests
│   └── test_refactored_architecture.py # Full system integration
├── demos/                   # Feature demonstrations and plotting utilities
│   ├── demo_preferences.py  # Preferences system showcase
│   ├── demo_enhanced_features.py # Enhanced API features
│   ├── demo_api_features.py # API functionality examples
│   ├── demo_plots.py        # Visualization and plotting demonstrations
│   └── etf_comparison_plots.py # ETF comparison visualization utilities
└── README.md               # This file
```

## 🚀 Running Tests

### Run All Tests
```bash
python run_tests.py
```

### Run Individual Test Categories

**Unit Tests:**
```bash
python tests/unit/test_simple_refactor.py
python tests/unit/test_preferences.py
```

**Integration Tests:**
```bash
python tests/integration/test_refactored_architecture.py
```

**Demonstrations:**
```bash
python tests/demos/demo_preferences.py
python tests/demos/demo_enhanced_features.py
python tests/demos/demo_api_features.py
```

**Visualization Demos:**
```bash
python tests/demos/demo_plots.py
python tests/demos/etf_comparison_plots.py
```

## 🧪 Test Categories

### **Unit Tests**
- **Purpose**: Test individual components in isolation
- **Scope**: Single classes, functions, or modules
- **Dependencies**: Minimal external dependencies
- **Speed**: Fast execution

### **Integration Tests**
- **Purpose**: Test component interactions
- **Scope**: Multiple modules working together
- **Dependencies**: Database, API endpoints
- **Speed**: Moderate execution time

### **Demonstrations**
- **Purpose**: Showcase features and workflows
- **Scope**: End-to-end functionality examples
- **Dependencies**: Full system setup
- **Speed**: Slower, comprehensive examples

### **Visualization Demos**
- **Purpose**: Generate sample charts and performance visualizations
- **Scope**: Plotting utilities and chart generation
- **Dependencies**: Matplotlib, Seaborn, historical data
- **Output**: PNG files saved to `visualizations/sample_outputs/`

## 📋 Test Requirements

### **Prerequisites**
- Python 3.8+
- All project dependencies installed
- Database initialized (for integration tests)
- API server running (for API tests)
- Matplotlib, Seaborn (for visualization demos)

### **Environment Setup**
```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from src.database import init_database; init_database()"

# Start API server (for API tests)
python api/main_enhanced.py &
```

## 🎯 Test Coverage

### **Components Tested**
- ✅ Trading Configuration System
- ✅ Technical Indicators Utility
- ✅ Strategy Factory Pattern
- ✅ User Preferences Integration
- ✅ Database Models and Relationships
- ✅ API Endpoints and Authentication
- ✅ Mobile App Integration Points
- ✅ Visualization and Plotting Systems
- ✅ ETF vs Stock Performance Comparisons

### **Test Scenarios**
- ✅ Default configuration loading
- ✅ User preference overrides
- ✅ Technical indicator calculations
- ✅ Strategy creation and analysis
- ✅ Database CRUD operations
- ✅ API request/response validation
- ✅ Error handling and edge cases
- ✅ Performance visualization generation
- ✅ ETF comparison chart creation

## 🎨 Visualization Demos

### **demo_plots.py**
Generates comprehensive performance dashboards including:
- Strategy performance comparisons
- Risk-adjusted return analysis
- Equity curve visualizations
- Trade distribution charts

### **etf_comparison_plots.py**
Creates ETF-specific comparison charts:
- ETF vs individual stock performance
- Sector-based performance analysis
- Risk-return scatter plots
- Time-series performance comparisons

### **Output Location**
All generated visualizations are saved to:
```
visualizations/sample_outputs/
├── etf_detailed_analysis_*.png
├── nvda_detailed_analysis_*.png
├── strategy_comparison_*.png
├── etf_vs_stocks_comparison_*.png
└── sentimenttrade_performance_dashboard_*.png
```

## 🔧 Adding New Tests

### **Unit Test Template**
```python
#!/usr/bin/env python3
"""
Test for [Component Name]
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_component_functionality():
    """Test specific component functionality"""
    try:
        # Test implementation
        assert True  # Replace with actual test
        print("✅ Test passed")
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_component_functionality()
    sys.exit(0 if success else 1)
```

### **Visualization Demo Template**
```python
#!/usr/bin/env python3
"""
Visualization demo for [Feature Name]
"""

import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def create_sample_visualization():
    """Create sample visualization"""
    try:
        # Create plot
        plt.figure(figsize=(12, 8))
        # Add plotting code here
        
        # Save to visualizations directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"../visualizations/sample_outputs/sample_chart_{timestamp}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Visualization saved: {filename}")
        return True
    except Exception as e:
        print(f"❌ Visualization failed: {e}")
        return False

if __name__ == "__main__":
    success = create_sample_visualization()
    sys.exit(0 if success else 1)
```

## 📊 Continuous Integration

### **Pre-commit Checks**
```bash
# Run all tests before committing
python run_tests.py

# Run specific test category
python run_tests.py --category unit

# Generate fresh visualizations
python tests/demos/demo_plots.py
```

### **Automated Testing**
- Tests can be integrated with CI/CD pipelines
- Each test returns proper exit codes (0 = success, 1 = failure)
- Structured output for automated parsing
- Visualization demos can be run to generate sample outputs

## 🎉 Best Practices

### **Test Organization**
- ✅ One test file per major component
- ✅ Clear, descriptive test names
- ✅ Proper setup and teardown
- ✅ Independent test execution

### **Test Quality**
- ✅ Test both success and failure cases
- ✅ Use realistic test data
- ✅ Include edge case testing
- ✅ Provide clear error messages

### **Visualization Standards**
- ✅ High-resolution output (300 DPI)
- ✅ Consistent color schemes
- ✅ Clear labels and legends
- ✅ Timestamped filenames

### **Maintenance**
- ✅ Update tests when features change
- ✅ Remove obsolete tests
- ✅ Keep test documentation current
- ✅ Regular test execution
- ✅ Archive old visualization outputs

This organized test structure ensures reliable, maintainable testing for the SentimentTrade platform! 🚀
