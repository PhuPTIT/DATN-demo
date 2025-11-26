#!/bin/bash
# Render deployment script for DATN-demo

# Backend service
echo "Creating backend service on Render..."
curl -X POST https://api.render.com/v1/services \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "datn-demo-api",
    "type": "web_service",
    "plan": "free",
    "runtime": "python",
    "buildCommand": "pip install -r backend/requirements.txt",
    "startCommand": "cd backend && python main.py",
    "repo": "https://github.com/PhuPTIT/DATN-demo",
    "branch": "main"
  }'

# Frontend service
echo "Creating frontend service on Render..."
curl -X POST https://api.render.com/v1/services \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "datn-demo-ui",
    "type": "web_service",
    "plan": "free",
    "runtime": "node",
    "buildCommand": "npm run build",
    "startCommand": "npm run preview",
    "repo": "https://github.com/PhuPTIT/DATN-demo",
    "branch": "main",
    "envVars": [
      {
        "key": "VITE_API_URL",
        "value": "https://datn-demo-api.onrender.com"
      }
    ]
  }'

echo "Deployment script completed!"
