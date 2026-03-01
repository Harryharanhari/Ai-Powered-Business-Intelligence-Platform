# 🤖 Enterprise AI Business Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-lightgrey.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An advanced, production-ready AI-powered Business Intelligence (BI) platform designed for modern data teams. This platform integrates cutting-edge Machine Learning models and Large Language Models (LLMs) to transform raw data into actionable business intelligence.

---

## 🌟 Key Features

### 📊 Automated Data Science
- **Auto EDA**: Instant statistical profiling and interactive visualizations (Plotly) for uploaded CSVs.
- **AutoML Leaderboard**: Automatically compete and rank multiple models (**Random Forest, Gradient Boosting, Linear Regression**) to find the best fit for your KPIs.

### 🔮 Predictive Analytics
- **Time-Series Forecasting**: Enterprise-grade forecasting using **Prophet (Meta)** and deep learning **LSTM** models.
- **Anomaly Detection**: Proactive risk monitoring using **Isolation Forest** and Z-Score algorithms to flag critical outliers.

### 🤖 Generative AI & NLP
- **AI Business Assistant**: A conversational interface powered by **LangChain** and **Ollama (Llama 3)**. Ask natural language questions like *"What is the average revenue per region?"* or *"Compare Q4 sales vs Q3"*.
- **Data Grounding**: The AI is grounded in your specific dataset, ensuring highly accurate and context-aware responses.

### 📄 Enterprise Reporting
- **Automated PDF Reports**: Generate comprehensive executive summaries including EDA insights and forecast results with a single click.

---

## 🛠 Tech Stack

- **Backend**: Python, Flask, SQLAlchemy
- **AI/ML**: Scikit-learn, Meta Prophet, TensorFlow/Keras
- **LLM Orchestration**: LangChain, Ollama (Llama 3)
- **Frontend**: Bootstrap 5, Plotly.js, FontAwesome
- **Deployment**: Docker, Gunicorn

---

## � Quick Start

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com/) (running locally)
- Docker (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai-bi-platform.git
   cd ai-bi-platform
   ```

2. **Setup virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**
   Create a `.env` file in the root:
   ```env
   SECRET_KEY=your_secure_random_key
   DATABASE_URL=sqlite:///app.db
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3
   ```

4. **Initialize Database & Run**
   ```bash
   python run.py
   ```

---

## 🐳 Docker Deployment

The platform is fully containerized for easy scaling and deployment.

```bash
docker-compose up --build
```
*Note: Gunicorn is configured with a 120s timeout to handle intensive AI analysis tasks.*

---

## 🏗 Modular Architecture

```text
├── ai_services/      # Dedicated ML & LLM logic
├── app/              # Core Flask application
│   ├── routes/       # API endpoints & View logic
│   ├── models/       # Database schemas
│   ├── templates/    # Dynamic HTML interfaces
│   └── static/        # CSS/JS assets
├── uploads/          # Secure dataset storage
└── reports/          # Generated PDF business reports
```

## 🤝 Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements.

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.
