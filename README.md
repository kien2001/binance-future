# Binance Future Advisor — AI Trading Assistant (Groq)

A professional trading advisor for Binance Futures, powered by **Groq Llama-3.3-70b**. It analyzes real-time market data, computes technical indicators (RSI, MACD, EMA), and provides actionable trading signals.

## Project Structure
- `backend/`: FastAPI server and AI logic.
- `frontend/`: Premium Dark Mode interface.
- `.venv/`: Python virtual environment.

## Installation
1. Ensure you have Python 3.10+ installed.
2. The dependencies are already installed in the `.venv`. To update:
   ```powershell
   cd backend
   ..\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

## How to Run (Recommended)
You MUST run the project using the Python interpreter from the virtual environment to ensure all libraries (like `groq`) are recognized.

### Start the Server
From the root directory of the project:
```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000
```
*Note: If you are already inside the `backend/` folder, use `..\.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000`.*

### Access the App
Open your browser and navigate to:
[http://localhost:8000](http://localhost:8000)

## Hosting & Deployment (Docker)

To deploy the application professionally, use the provided Docker configuration. This ensures the environment is identical regardless of where you host it.

### 1. Build the Docker Image
From the root directory:
```bash
docker build -t binance-advisor .
```

### 2. Run the Container
```bash
docker run -p 8000:8000 -e GROQ_API_KEY="your_groq_api_key_here" binance-advisor
```

### 3. Deploy to Cloud
- **Railway/Render**: Simply connect your GitHub repository; they will automatically detect the `Dockerfile` and deploy it.
- **VPS**: Install Docker and use the commands above.
- **Environment Variables**: Make sure to set `GROQ_API_KEY` in your hosting provider's dashboard.

## Technical Features
- **AI Engine**: Groq (Llama-3.3-70b-versatile).
- **Data Source**: Official Binance Futures Public API.
- **Indicators**: RSI(14), MACD(12,26,9), EMA(50,200).
- **Risk Management**: Leverage suggestions, SL/TP levels, and confidence scoring.
