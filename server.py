"""
Flask Backend Server
Handles API requests to process video feeds
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import subprocess
import json
import sys
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

@app.route('/api/process-video', methods=['POST'])
def process_video():
    """
    Execute the video processing Python script and return results
    """
    try:
        # Get the path to the Python script
        script_path = os.path.join(os.path.dirname(__file__), 'process_video.py')
        
        # Execute the Python script
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )
        
        if result.returncode != 0:
            return jsonify({
                'error': 'Script execution failed',
                'message': result.stderr
            }), 500
        
        # Parse the JSON output from the script
        try:
            script_output = json.loads(result.stdout)
        except json.JSONDecodeError:
            # If output is not JSON, return as message
            return jsonify({
                'results': result.stdout,
                'message': 'Processing completed'
            }), 200
        
        return jsonify({
            'results': script_output,
            'message': 'Video processing completed successfully'
        }), 200
        
    except subprocess.TimeoutExpired:
        return jsonify({
            'error': 'Processing timeout',
            'message': 'Video processing took too long'
        }), 500
    except Exception as e:
        return jsonify({
            'error': 'Server error',
            'message': str(e)
        }), 500

@app.route('/api/detect-emotion-facial', methods=['POST'])
def detect_emotion_facial():
    """
    Execute the main.py script that combines emotion and facial expression detection
    """
    try:
        # Get the path to the main.py script
        script_path = os.path.join(os.path.dirname(__file__), 'main.py')
        
        # Execute the Python script
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout for video processing
        )
        
        if result.returncode != 0:
            return jsonify({
                'error': 'Script execution failed',
                'message': result.stderr
            }), 500
        
        # Parse the JSON output from the script
        try:
            script_output = json.loads(result.stdout)
        except json.JSONDecodeError:
            # If output is not JSON, return as message
            return jsonify({
                'results': result.stdout,
                'message': 'Processing completed'
            }), 200
        
        return jsonify({
            'results': script_output,
            'message': 'Emotion and facial expression detection completed successfully'
        }), 200
        
    except subprocess.TimeoutExpired:
        return jsonify({
            'error': 'Processing timeout',
            'message': 'Detection took too long'
        }), 500
    except Exception as e:
        return jsonify({
            'error': 'Server error',
            'message': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    print("Starting Flask server on http://localhost:5000")
    print("API endpoints:")
    print("  - http://localhost:5000/api/process-video")
    print("  - http://localhost:5000/api/detect-emotion-facial")
    app.run(debug=True, port=5000)

