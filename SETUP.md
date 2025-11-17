# Setup Instructions

## Overview
This project includes:
1. A landing page with an animated Explore button
2. A dashboard page with video feed and processing buttons
3. A Node.js backend server that executes Python scripts for video processing

## Setup Steps

### 1. Install Node.js Dependencies
```bash
npm install
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start the Application
Run both the Node.js server and frontend dev server together:
```bash
npm start
```

This will start:
- Node.js server on `http://localhost:3000` (executes Python scripts)
- Vite dev server on `http://localhost:5173` (frontend)

**OR** run them separately:

**Terminal 1 - Node.js Server:**
```bash
npm run server
```

**Terminal 2 - Frontend Dev Server:**
```bash
npm run dev
```

### 4. Usage
1. Open the landing page in your browser (usually `http://localhost:5173`)
2. Click the "Explore >" button to navigate to the login page
3. Login and access the dashboard
4. On the dashboard:
   - Click "Facial/Emotion" button to run emotion and facial expression detection
   - Click "Gesture Detection" button to run video processing
5. Results will be displayed in the results container below the buttons

## Files Structure
- `index.html` - Landing page with Explore button
- `public/dashboard.html` - Dashboard page with video feed and processing buttons
- `public/login.html` - Login page
- `main.py` - Main Python script that combines emotion and facial expression detection
- `process_video.py` - Python script for video processing
- `emotion_Detection.py` - Emotion detection module
- `facial_expression.py` - Facial expression detection module
- `server.js` - Node.js/Express backend server that executes Python scripts
- `requirements.txt` - Python dependencies

## Modifying the Python Scripts
- Edit `main.py` to modify emotion and facial expression detection
- Edit `process_video.py` to modify video processing logic
- Both scripts should output JSON which is automatically parsed and displayed on the dashboard

## Notes
- The Node.js server runs Python scripts when API endpoints are called
- Make sure Python is installed and accessible from command line
- The emotion detection requires `emotion_detection_model_50epochs.h5` model file in the project root
- If the model file is missing, facial expression detection will still work, but emotion detection will show "Emotion model not available"

