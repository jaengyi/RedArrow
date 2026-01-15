# GEMINI.md - RedArrow Project

## Project Overview

RedArrow is a sophisticated, automated stock trading system designed for short-term strategies like day trading and scalping. Written in Python, it operates on a continuous loop during market hours, identifying and acting on trading opportunities in real-time.

The system's architecture is modular, with distinct components for data collection, technical analysis, stock selection, and risk management. It leverages a combination of real-time market data and historical analysis to make trading decisions. Configuration is a key aspect of the system, with settings managed through a `config.yaml` file for strategy parameters and a `.env` file for sensitive data like API keys and database credentials.

### Core Technologies

*   **Programming Language:** Python 3
*   **Key Libraries:**
    *   **Data Analysis:** Pandas, NumPy
    *   **Technical Indicators:** TA-Lib
    *   **API Communication:** requests, websocket-client, aiohttp
    *   **Database/Caching:** PostgreSQL (historical data), Redis (real-time caching)
    *   **Configuration:** PyYAML, python-dotenv
    *   **Logging:** Loguru
    *   **Scheduling:** APScheduler
*   **Broker Integration:** The system is designed to connect to brokerage APIs, with Korean Investment & Securities being the primary example.

### Architecture

The system is designed with a layered architecture:

1.  **Configuration Layer:** Manages all settings, from API keys to trading strategy parameters.
2.  **Data Layer:** Interfaces with PostgreSQL for historical data and Redis for caching. It also includes the broker API integration for real-time data.
3.  **Core Engine:** The heart of the system, orchestrating the main trading loop.
4.  **Business Logic Modules:**
    *   `TechnicalIndicators`: Calculates various technical indicators (MA, MACD, RSI, etc.).
    *   `StockSelector`: Implements the core logic for identifying promising stocks based on a scoring system.
    *   `RiskManager`: Enforces risk management rules, such as stop-loss and take-profit levels.

## Key Files

| File Path                                 | Description                                                                                                                              |
| ----------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `src/main.py`                             | The main entry point of the application. It contains the primary execution loop and orchestrates the other modules.                        |
| `config/config.yaml`                      | The central configuration file for strategy parameters, technical indicator settings, and risk management rules.                       |
| `.env.example`                            | An example file for environment variables. A `.env` file must be created from this to store sensitive information.                       |
| `requirements.txt`                        | A list of all the Python dependencies required for the project.                                                                          |
| `src/config/settings.py`                  | A Python script that loads, validates, and provides access to the settings from both `config.yaml` and the `.env` file.                       |
| `src/stock_selector/selector.py`          | Implements the logic for selecting stocks based on the rules and scoring defined in the system design.                                     |
| `src/risk_manager/risk_control.py`        | Contains the logic for managing risk, including setting stop-loss and take-profit orders.                                                  |
| `src/data_collectors/broker_api.py`       | Provides an interface for communicating with the brokerage's API for data retrieval and order execution.                                   |
| `docs/03.Design/SystemDesign_20251231.md` | A detailed document outlining the system's architecture, module design, data models, and processing flows. A must-read for developers.   |
| `scripts/`                                | A directory containing shell scripts for starting, stopping, and checking the status of the application (`start.sh`, `stop.sh`, `status.sh`). |

## Building and Running

### 1. Prerequisites

Before running the application, you need to have the following installed:

*   Python 3
*   PostgreSQL
*   Redis
*   TA-Lib

Refer to the `README.md` file for detailed installation instructions for these prerequisites.

### 2. Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd RedArrow
    ```

2.  **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    *   Copy the example `.env` file: `cp .env.example .env`
    *   Edit the `.env` file and provide your brokerage API keys, database credentials, and other required settings.

5.  **Configure the application:**
    *   Review and edit `config/config.yaml` to set your desired trading strategy parameters.

### 3. Running the Application

The application is managed through the shell scripts in the `scripts/` directory.

*   **Start the application:**
    ```bash
    ./scripts/start.sh
    ```
    This will start the application in the background.

*   **Check the status:**
    ```bash
    ./scripts/status.sh
    ```

*   **View logs:**
    ```bash
    tail -f logs/redarrow_*.log
    ```

*   **Stop the application:**
    ```bash
    ./scripts/stop.sh
    ```

## Development Conventions

*   **Configuration Management:** All configurations are clearly separated from the code. Sensitive information is stored in `.env`, while strategy parameters are in `config/config.yaml`. The `src/config/settings.py` module provides a clean interface to access these settings.
*   **Modularity:** The codebase is well-structured into modules with distinct responsibilities (e.g., `data_collectors`, `indicators`, `stock_selector`, `risk_manager`).
*   **Error Handling:** The `main.py` file includes basic error handling and logging for key events and failures.
*   **Lifecycle Management:** The use of shell scripts for starting, stopping, and checking the status of the application provides a standardized way to manage the application's lifecycle.
*   **Documentation:** The project includes extensive documentation in the `docs/` directory, covering requirements, analysis, and design. This is a great resource for understanding the project in depth.
