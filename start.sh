#!/bin/bash
# Start CTV Ad Intelligence Dashboard
# Launches FastAPI backend + React frontend

echo "🚀 Starting CTV Ad Intelligence Dashboard..."

# Kill any existing processes on our ports
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:5173 | xargs kill -9 2>/dev/null

# Start FastAPI backend (uses conda Python so duckdb is available)
echo "📡 Starting API server on http://localhost:8000..."
python -m uvicorn api.main:app --reload --port 8000 &
BACKEND_PID=$!

# Start React frontend
echo "🎨 Starting React frontend on http://localhost:5173..."
cd frontend && npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Dashboard running at: http://localhost:5173"
echo "   API running at:       http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop both servers."

# Trap Ctrl+C to kill both processes
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
