"""
Main Video Processing Script
Combines Emotion Detection and Facial Expression Analysis
"""
import cv2
import numpy as np
import json
import sys
import os
from datetime import datetime

# Import the detection modules
try:
    from emotion_Detection import EmotionDetector
    from facial_expression import classify_face
    import mediapipe as mp
    mp_holistic = mp.solutions.holistic.Holistic(static_image_mode=False, min_detection_confidence=0.5)
except ImportError as e:
    print(f"Error importing modules: {e}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Error initializing modules: {e}", file=sys.stderr)
    sys.exit(1)

class CombinedDetector:
    def __init__(self):
        """Initialize both emotion and facial expression detectors"""
        try:
            # Try to initialize emotion detector (may fail if model file not found)
            try:
                self.emotion_detector = EmotionDetector()
                self.emotion_available = True
            except Exception as e:
                print(f"Warning: Emotion detector not available: {e}", file=sys.stderr)
                self.emotion_available = False
                self.emotion_detector = None
            
            self.mp_holistic = mp_holistic
            self.mp_drawing = mp.solutions.drawing_utils
        except Exception as e:
            print(f"Error initializing detectors: {e}", file=sys.stderr)
            raise
    
    def process_frame(self, frame):
        """
        Process a single frame and return both emotion and facial expression results
        
        Args:
            frame: BGR image frame from video capture
            
        Returns:
            dict: Combined results with emotion and facial expression
        """
        results = {
            "emotion": None,
            "facial_expression": None,
            "face_detected": False,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            # Convert BGR to RGB for MediaPipe
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_rgb.flags.writeable = False
            
            # Process with MediaPipe for facial landmarks
            mp_results = self.mp_holistic.process(frame_rgb)
            
            frame_rgb.flags.writeable = True
            
            # Get facial expression using MediaPipe landmarks
            if mp_results.face_landmarks:
                results["face_detected"] = True
                results["facial_expression"] = classify_face(mp_results.face_landmarks)
                
                # Extract face region for emotion detection
                # Get bounding box from landmarks
                h, w, _ = frame.shape
                x_coords = [landmark.x * w for landmark in mp_results.face_landmarks.landmark]
                y_coords = [landmark.y * h for landmark in mp_results.face_landmarks.landmark]
                
                x_min = int(min(x_coords))
                x_max = int(max(x_coords))
                y_min = int(min(y_coords))
                y_max = int(max(y_coords))
                
                # Add padding
                padding = 20
                x_min = max(0, x_min - padding)
                y_min = max(0, y_min - padding)
                x_max = min(w, x_max + padding)
                y_max = min(h, y_max + padding)
                
                # Extract face region
                face_roi = frame[y_min:y_max, x_min:x_max]
                
                if face_roi.size > 0 and self.emotion_available:
                    try:
                        # Get emotion from emotion detector
                        results["emotion"] = self.emotion_detector.detect_emotions(face_roi)
                    except Exception as e:
                        print(f"Error in emotion detection: {e}", file=sys.stderr)
                        results["emotion"] = "Unknown"
                elif not self.emotion_available:
                    results["emotion"] = "Emotion model not available"
            else:
                results["face_detected"] = False
                results["facial_expression"] = "Face Not Detected"
                
        except Exception as e:
            print(f"Error processing frame: {e}", file=sys.stderr)
            results["error"] = str(e)
        
        return results
    
    def process_video_stream(self, num_frames=10):
        """
        Process video stream from webcam and return combined results
        
        Args:
            num_frames: Number of frames to process (default: 10)
            
        Returns:
            dict: Combined analysis results
        """
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            return {
                "error": "Cannot open camera",
                "status": "failed"
            }
        
        all_results = []
        frame_count = 0
        
        try:
            while frame_count < num_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Process frame
                frame_result = self.process_frame(frame)
                if frame_result.get("face_detected"):
                    all_results.append(frame_result)
                
                frame_count += 1
                
        except Exception as e:
            return {
                "error": str(e),
                "status": "failed"
            }
        finally:
            cap.release()
        
        # Aggregate results
        if all_results:
            emotions = [r["emotion"] for r in all_results if r.get("emotion")]
            expressions = [r["facial_expression"] for r in all_results if r.get("facial_expression")]
            
            # Get most common emotion and expression
            emotion_counts = {}
            expression_counts = {}
            
            for emotion in emotions:
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            
            for expression in expressions:
                expression_counts[expression] = expression_counts.get(expression, 0) + 1
            
            most_common_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else "No Detection"
            most_common_expression = max(expression_counts.items(), key=lambda x: x[1])[0] if expression_counts else "No Detection"
            
            return {
                "status": "completed",
                "frames_processed": frame_count,
                "detections_found": len(all_results),
                "emotion_detection": {
                    "detected_emotion": most_common_emotion,
                    "confidence": emotion_counts.get(most_common_emotion, 0) / len(all_results) if all_results else 0,
                    "all_emotions": emotions
                },
                "facial_expression": {
                    "detected_expression": most_common_expression,
                    "confidence": expression_counts.get(most_common_expression, 0) / len(all_results) if all_results else 0,
                    "all_expressions": expressions
                },
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            return {
                "status": "completed",
                "frames_processed": frame_count,
                "detections_found": 0,
                "message": "No face detected in video stream",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }


def main():
    """Main function to process video and return results"""
    try:
        detector = CombinedDetector()
        results = detector.process_video_stream(num_frames=10)
        print(json.dumps(results, indent=2))
    except Exception as e:
        error_result = {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        print(json.dumps(error_result, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()

