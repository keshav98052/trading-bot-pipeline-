 Autonomous AI Trading Pipeline & Analytics Dashboard



An end-to-end, locally hosted algorithmic trading system that automates market analysis and paper trading. The system uses Natural Language Processing (NLP) to quantify news sentiment, feeds live indicators into a Machine Learning classifier to generate daily predictive signals, executes automated trades, and visualizes real-time performance through an interactive web interface.



 🏗️ System Architecture



The pipeline separates data ingestion/execution from training to optimize execution speed and maintain clean, modular decoupled layers:



1. The Laboratory (`Model_Training_Lab.ipynb`): An offline research environment used to clean historical data, engineer features, and train the ensemble machine learning brain.

2. The Executioner (`trading_bot.py`): An autonomous background service that wakes up daily on an infinite event loop to pull data, run NLP/ML inference, make trade decisions, and commit telemetry.

3. The Database (`market_memory.db`): A persistent SQLite database handling localized structured logging of features, news text, mathematical sentiment scores, and historical AI signals.

4. The Monitor (`dashboard.py`): A frontend Business Intelligence (BI) web interface connecting directly to the localized database and Alpaca Brokerage API to stream live account metrics and telemetry.



 🚀 Key Features



 Live Market Data Ingestion: Real-time asset bars and global financial news fetched programmatically via the Alpaca Market Data API.

 NLP Sentiment Analysis: Raw headline extraction processed via NLTK's VADER (Valence Aware Dictionary and sEntiment Reasoner) to generate normalized compound sentiment metrics (-1.0 to +1.0).

 Predictive Machine Learning: An ensemble Random Forest Classifier mapping asset momentum alongside text sentiment scores to compute binary market directives (Buy/Sell).

 Deterministic Scheduling: Background execution managed by a lightweight event loop, optimized for international market alignment (configured for US market open synchronization).

 Robust UI Monitoring: Interactive metrics displaying Total Portfolio Value, Available Buying Power, historical log tracking, and programmatic duplicate filtering for state tracking.



 🛠️ Tech Stack & Dependencies



 Language: Python 3.10+

 Database: SQLite3

 APIs & Brokerage: `alpaca-py`

 Machine Learning & NLP: `scikit-learn`, `joblib`, `nltk`

 Data Manipulation: `pandas`, `numpy`

 Automation & Scheduling: `schedule`

 Frontend Web Framework: `streamlit`



 📦 Installation & Setup



1. Clone the repository to your local machine:

&x20;  ```bash

&x20;  git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git)

&x20;  cd YOUR_REPOSITORY_NAME



Install the necessary system dependencies:



pip install alpaca-py scikit-learn joblib nltk pandas numpy schedule streamlit



Open trading_bot.py and dashboard.py to insert your active Alpaca Paper Trading API keys:



ALPACA_KEY = "YOUR_PAPER_KEY_HERE"

ALPACA_SECRET = "YOUR_SECRET_KEY_HERE"



How to Run

Because the core application runs as a decoupled architecture, you must initialize both the background execution engine and the frontend monitoring dashboard in separate terminal windows.



1. Initialize the Execution Engine

Open a terminal window, navigate to your root folder, and execute the core automated loop:





python trading_bot.py



Note: The service will initialize, download required lexical data dependencies, and confirm state tracking with a persistent status indicator.



2. Launch the Monitoring UI

Open a secondary terminal window, maintaining the active background execution instance, and start the web framework:





streamlit run dashboard.py



The application will automatically resolve networking rules and initialize your default system browser to navigate to the interface (typically hosted at http://localhost:8501).



📈 Future Roadmap

Move localized background infrastructure to cloud-native virtual server hosting (AWS EC2 / GCP Compute Engine) for true 24/7/365 resilience.



Replace the placeholder static text analysis vectors with advanced transformer models (HuggingFace / FinBERT) for hyper-domain financial text parsing.



Expand database tracking to manage multi-variable target metrics and deep order execution history metrics.

