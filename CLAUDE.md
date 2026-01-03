# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RedArrow is a Korean stock trading system for short-term investments (day trading and scalping). It automatically selects stocks based on technical indicators, volume analysis, and market signals using real-time data from Korean brokerage APIs.

**Key Technology**: Python-based system using TA-Lib for technical indicators, supporting Korean Investment & Securities API (and others), with optional PostgreSQL/Redis for data persistence.

## Essential Commands

### Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Running the System
```bash
# Run main program
python src/main.py

# Validate configuration
python -m src.config.settings
```

### Development
```bash
# Test individual modules
python -m src.stock_selector.selector
python -m src.risk_manager.risk_control
python -m src.indicators.technical_indicators
```

### Monitoring
```bash
# View logs
tail -f logs/redarrow_$(date +%Y%m%d).log

# Check trade history
grep "매수\|매도" logs/redarrow_*.log
```

## Architecture

### Core System Flow

1. **main.py** (`RedArrowSystem` class) - Main orchestrator that:
   - Loads settings from `.env` and `config/config.yaml`
   - Checks market hours (09:00-15:30 KST)
   - Collects market data (currently stub, needs broker API integration)
   - Runs stock selection logic
   - Executes trades (simulation mode by default)
   - Monitors positions and triggers exits

2. **Stock Selection Pipeline** (`src/stock_selector/selector.py`):
   - Filters top N stocks by trading volume (default: 30)
   - Calculates scoring based on multiple signals (0-15+ points):
     - Volume surge detection (3 pts)
     - MA breakout (2 pts)
     - Golden cross (3 pts)
     - Volatility breakout (2 pts)
     - MACD buy signal (2 pts)
     - Stochastic signals (2 pts)
     - OBV rising (1 pt)
     - Support at MA (1 pt)
   - Selects stocks scoring >= 5 points (configurable)

3. **Risk Management** (`src/risk_manager/risk_control.py`):
   - Position sizing based on account risk percentage
   - Stop-loss: percentage-based AND MA-based
   - Trailing stop: tracks highest price since entry
   - Take-profit: percentage-based target
   - Overnight holding rules
   - Daily loss limits

4. **Technical Indicators** (`src/indicators/technical_indicators.py`):
   - Implements all indicators WITHOUT using TA-Lib directly (pure numpy/pandas)
   - MA, EMA, MACD, Stochastic, OBV, RSI, Bollinger Bands
   - Volatility breakout (Larry Williams strategy)
   - Golden/Dead cross detection

### Configuration System

**Two-tier configuration**:

1. **`.env`** - Broker API keys and runtime settings:
   - Automatically switches between `SIMULATION_*` and `REAL_*` keys based on `TRADING_MODE`
   - Database settings (currently optional/unused)
   - Risk parameters (override config.yaml if set)

2. **`config/config.yaml`** - Trading strategy parameters:
   - Stock selector thresholds
   - Technical indicator periods
   - Risk management rules
   - Market hours
   - Logging settings

**Settings class** (`src/config/settings.py`):
- Loads both files
- Validates required keys
- Provides typed access via properties
- Env vars override YAML values for risk settings

### Module Structure

```
src/
├── config/
│   └── settings.py           # Central config loader with validation
├── data_collectors/
│   └── broker_api.py         # Broker API integration (stub - needs implementation)
├── indicators/
│   └── technical_indicators.py  # All technical indicators (numpy/pandas based)
├── stock_selector/
│   └── selector.py           # Stock selection scoring logic
├── risk_manager/
│   └── risk_control.py       # Position sizing, stop-loss, take-profit
└── main.py                   # Main orchestrator
```

### Key Design Patterns

**Settings Auto-Selection**: The system automatically selects API keys based on `TRADING_MODE`:
- `simulation` → uses `SIMULATION_APP_KEY`, `SIMULATION_APP_SECRET`, `SIMULATION_ACCOUNT_NUMBER`
- `real` → uses `REAL_APP_KEY`, `REAL_APP_SECRET`, `REAL_ACCOUNT_NUMBER`

**Scoring-Based Selection**: Instead of hard rules, stocks are scored on multiple signals (0-15+ points). This allows flexible thresholds and easy tuning.

**Database Optional**: Database (PostgreSQL/Redis) settings exist but are NOT currently used. The system runs entirely in-memory. Database integration is planned for backtesting and trade history.

## Important Implementation Notes

### Korean Market Specifics

- **Market Hours**: 09:00-15:30 KST (checked in `is_market_open()`)
- **Position Close Time**: 15:20 (10 min before close)
- **VI Detection**: "Volatility Interruption" - Korean market circuit breaker (logic exists but needs real data)
- **Sector Synchronization**: Korean stocks often move in sector groups (referenced but not fully implemented)

### Broker API Integration

**CRITICAL**: The current `collect_market_data()` in main.py returns STUB DATA. To make this production-ready:

1. Implement `src/data_collectors/broker_api.py` with real API calls
2. Supported brokers (choose one):
   - Korea Investment & Securities (recommended - REST API)
   - Kiwoom Securities (Windows-only, ActiveX)
   - eBest Investment & Securities (xingAPI)
3. Required data:
   - Real-time prices (OHLCV)
   - Order book (bid/ask volumes)
   - Historical data (30+ days for indicators)
   - Stock metadata (sector, theme)

### Technical Indicators

**Do NOT use TA-Lib library directly in indicator calculations**. The `TechnicalIndicators` class implements all indicators using numpy/pandas for better control and debugging. TA-Lib is listed in requirements.txt but may be removed.

### Risk Management Rules

When implementing trade execution:
- ALWAYS call `check_max_positions()` before new trades
- Update `highest_price` on EVERY price tick
- Call `should_close_position()` frequently (every minute or tick)
- Respect `daily_loss_limit` - hard stop for the day
- In real mode, trailing stops prevent giving back gains

## Configuration Reference

### Critical Settings

**Stock Selection** (`config/config.yaml`):
- `top_volume_count`: 30 - Only consider top N stocks by trading volume
- `volume_surge_threshold`: 2.0 - Alert when volume is 2x average
- `min_selection_score`: 5 - Minimum score to trigger trade signal
- `k_value`: 0.5 - Volatility breakout K-factor (Larry Williams)

**Risk Management** (`config/config.yaml` or `.env`):
- `stop_loss_percent`: 2.5 - Hard stop at -2.5% loss
- `take_profit_percent`: 5.0 - Auto-exit at +5.0% gain
- `trailing_stop_percent`: 1.5 - Protect profits after peak
- `max_position_size`: 1000000 - Max KRW per position
- `max_positions`: 5 - Max concurrent holdings
- `overnight_hold`: false - Close all before market close by default

### Switching Modes

To switch from simulation to real trading:
```bash
# Edit .env
TRADING_MODE=real  # Change from simulation

# Ensure real API keys are set
REAL_APP_KEY=...
REAL_APP_SECRET=...
REAL_ACCOUNT_NUMBER=...
```

**WARNING**: `real` mode executes actual trades with real money.

## Common Modifications

### Adding a New Technical Indicator

1. Add calculation method to `src/indicators/technical_indicators.py`
2. Add check method to `src/stock_selector/selector.py`
3. Add scoring logic in `select_stocks()` method
4. Add configuration to `config/config.yaml` under `indicators:`

### Adjusting Stock Selection Criteria

The `select_stocks()` method in `selector.py` assigns points for each signal. To change:
- Modify point values (currently: volume_surge=3, golden_cross=3, etc.)
- Add/remove signals
- Change minimum score threshold (currently 5)

### Customizing Risk Rules

All risk logic is in `RiskManager` class:
- `check_stop_loss()` - Modify stop conditions
- `check_take_profit()` - Modify profit targets
- `calculate_trailing_stop()` - Adjust trailing logic
- `check_overnight_eligibility()` - Overnight holding rules

## Testing Strategy

**Before real trading**:
1. Run in `TRADING_MODE=simulation` for at least 2 weeks
2. Monitor `logs/redarrow_*.log` daily for:
   - Selection logic triggering correctly
   - Stop-loss activations
   - False signals
3. Paper trade with realistic position sizes
4. Verify Korean market hours handling
5. Test during high volatility days

## Deployment

### OCI Deployment
- Automated script: `scripts/oci_setup.sh`
- Creates systemd service for auto-start
- Includes log rotation and backup
- See `docs/05.Deploy/OCIDeployment.md`

### Manual Deployment
```bash
# Create systemd service
sudo cp scripts/redarrow.service /etc/systemd/system/
sudo systemctl enable redarrow
sudo systemctl start redarrow

# Monitor
sudo journalctl -u redarrow -f
```

## Known Limitations

1. **No Backtesting**: System runs real-time only. Historical backtesting not implemented.
2. **Database Unused**: PostgreSQL/Redis configured but not integrated.
3. **Stub Market Data**: `collect_market_data()` returns fake data - needs broker API.
4. **No News/Disclosure**: News and corporate disclosure monitoring mentioned but not implemented.
5. **Single Market**: Korean market only (KRX).

## Code Style

- All docstrings in Korean (matching team preference)
- Type hints in function signatures
- Logging uses standard library `logging` (not loguru despite being in requirements)
- Configuration validation on startup
- Fail-fast on missing API keys
