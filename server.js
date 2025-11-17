import express from 'express';
import cors from 'cors';
import { exec } from 'child_process';
import { promisify } from 'util';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { readFileSync } from 'fs';

const execAsync = promisify(exec);
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.json());

// Serve static files from public directory
app.use(express.static('public'));

// Endpoint to run emotion/facial detection
app.post('/api/detect-emotion-facial', async (req, res) => {
  try {
    const mainPyPath = join(__dirname, 'main.py');
    
    // Execute the Python script
    const { stdout, stderr } = await execAsync(`python "${mainPyPath}"`, {
      timeout: 60000, // 60 second timeout
      maxBuffer: 10 * 1024 * 1024 // 10MB buffer
    });
    
    if (stderr && !stdout) {
      return res.status(500).json({
        error: 'Script execution failed',
        message: stderr
      });
    }
    
    // Parse JSON output
    try {
      const results = JSON.parse(stdout);
      return res.json({
        results: results,
        message: 'Emotion and facial expression detection completed successfully'
      });
    } catch (parseError) {
      // If not JSON, return as text
      return res.json({
        results: stdout,
        message: 'Processing completed'
      });
    }
  } catch (error) {
    console.error('Error:', error);
    return res.status(500).json({
      error: 'Server error',
      message: error.message
    });
  }
});

// Endpoint to run process video
app.post('/api/process-video', async (req, res) => {
  try {
    const processVideoPath = join(__dirname, 'process_video.py');
    
    // Execute the Python script
    const { stdout, stderr } = await execAsync(`python "${processVideoPath}"`, {
      timeout: 30000, // 30 second timeout
      maxBuffer: 10 * 1024 * 1024 // 10MB buffer
    });
    
    if (stderr && !stdout) {
      return res.status(500).json({
        error: 'Script execution failed',
        message: stderr
      });
    }
    
    // Parse JSON output
    try {
      const results = JSON.parse(stdout);
      return res.json({
        results: results,
        message: 'Video processing completed successfully'
      });
    } catch (parseError) {
      // If not JSON, return as text
      return res.json({
        results: stdout,
        message: 'Processing completed'
      });
    }
  } catch (error) {
    console.error('Error:', error);
    return res.status(500).json({
      error: 'Server error',
      message: error.message
    });
  }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'healthy' });
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
  console.log(`API endpoints:`);
  console.log(`  - http://localhost:${PORT}/api/process-video`);
  console.log(`  - http://localhost:${PORT}/api/detect-emotion-facial`);
});

