from crewai.tools import BaseTool
from typing import Type, Any, Dict, List
from pydantic import BaseModel, Field
import base64
import json
import os
import tempfile

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    cv2 = None
    np = None


class VideoAnalysisInput(BaseModel):
    """Input schema for video analysis tool."""
    video_path: str = Field(..., description="Path to the video file to analyze")
    max_frames: int = Field(default=10, description="Maximum number of frames to extract and analyze")
    analysis_focus: str = Field(default="comprehensive", description="Focus of analysis: 'comprehensive', 'patterns', 'indicators', 'levels'")


class VideoAnalysisTool(BaseTool):
    name: str = "video_analysis_tool"
    description: str = (
        "Analyze trading chart videos using multimodal LLM vision capabilities. "
        "Extracts frames from video and identifies trading pairs, technical indicators, "
        "chart patterns, support/resistance levels, and trend analysis."
    )
    args_schema: Type[BaseModel] = VideoAnalysisInput

    def __init__(self):
        super().__init__()
        if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        else:
            self.client = None

    def _extract_frames(self, video_path: str, max_frames: int = 10):
        """Extract frames from video file."""
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Could not open video file: {video_path}")
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            frame_indices = np.linspace(0, total_frames - 1, max_frames, dtype=int)
            
            frames = []
            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if ret:
                    frames.append(frame)
            
            cap.release()
            return frames
            
        except Exception as e:
            raise Exception(f"Error extracting frames from video: {str(e)}")

    def _encode_frame_to_base64(self, frame) -> str:
        """Convert frame to base64 string for API."""
        try:
            _, buffer = cv2.imencode('.jpg', frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            return frame_base64
        except Exception as e:
            raise Exception(f"Error encoding frame to base64: {str(e)}")

    def _analyze_frames_with_llm(self, frames: List[np.ndarray], analysis_focus: str) -> Dict[str, Any]:
        """Analyze frames using OpenAI's multimodal capabilities."""
        try:
            # Convert frames to base64
            frame_images = []
            for i, frame in enumerate(frames):
                frame_base64 = self._encode_frame_to_base64(frame)
                frame_images.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{frame_base64}",
                        "detail": "high"
                    }
                })

            # Create comprehensive prompt for trading chart analysis
            system_prompt = """You are an expert technical analyst specializing in trading chart analysis. 
            Analyze the provided trading chart frames and extract detailed technical information.
            
            Focus on identifying:
            1. Trading pair (e.g., BTC/USD, EUR/USD, etc.)
            2. Timeframe (1m, 5m, 15m, 1h, 4h, 1d, etc.)
            3. Technical indicators visible (RSI, MACD, Moving Averages, Bollinger Bands, etc.)
            4. Chart patterns (triangles, head and shoulders, flags, pennants, wedges, etc.)
            5. Support and resistance levels
            6. Trend direction and strength
            7. Key price levels and significant zones
            8. Volume information if visible
            
            Provide your analysis in a structured JSON format with high accuracy and confidence scores."""

            user_prompt = f"""Analyze these trading chart frames with focus on: {analysis_focus}
            
            Please provide a comprehensive technical analysis in the following JSON structure:
            {{
                "trading_pair": "string (e.g., BTC/USD)",
                "timeframe": "string (e.g., 1h)",
                "technical_indicators": ["array of visible indicators"],
                "chart_patterns": [
                    {{
                        "pattern": "pattern name",
                        "confidence": 0.0-1.0,
                        "description": "brief description"
                    }}
                ],
                "support_levels": [array of price levels],
                "resistance_levels": [array of price levels],
                "trend_direction": "bullish/bearish/sideways",
                "trend_strength": "strong/moderate/weak",
                "current_price_estimate": float,
                "key_observations": ["array of important notes"],
                "confidence_score": 0.0-1.0,
                "frame_analysis": {{
                    "total_frames_analyzed": int,
                    "consistency_across_frames": "high/medium/low"
                }}
            }}
            
            Be precise and only include information you can clearly observe in the charts."""

            # Prepare messages for API call
            messages = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user", 
                    "content": [
                        {"type": "text", "text": user_prompt}
                    ] + frame_images
                }
            ]

            # Call OpenAI API with vision model
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Use GPT-4 with vision capabilities
                messages=messages,
                max_tokens=2000,
                temperature=0.1  # Low temperature for consistent analysis
            )

            # Parse the response
            analysis_text = response.choices[0].message.content
            
            # Try to extract JSON from the response
            try:
                # Find JSON in the response
                start_idx = analysis_text.find('{')
                end_idx = analysis_text.rfind('}') + 1
                if start_idx != -1 and end_idx != 0:
                    json_str = analysis_text[start_idx:end_idx]
                    analysis_result = json.loads(json_str)
                else:
                    # Fallback: create structured response from text
                    analysis_result = {
                        "trading_pair": "Unknown",
                        "timeframe": "Unknown",
                        "technical_indicators": [],
                        "chart_patterns": [],
                        "support_levels": [],
                        "resistance_levels": [],
                        "trend_direction": "unknown",
                        "trend_strength": "unknown",
                        "key_observations": [analysis_text],
                        "confidence_score": 0.5,
                        "raw_analysis": analysis_text
                    }
            except json.JSONDecodeError:
                # Fallback response if JSON parsing fails
                analysis_result = {
                    "trading_pair": "Unknown",
                    "timeframe": "Unknown",
                    "technical_indicators": [],
                    "chart_patterns": [],
                    "support_levels": [],
                    "resistance_levels": [],
                    "trend_direction": "unknown",
                    "trend_strength": "unknown",
                    "key_observations": ["Analysis completed but JSON parsing failed"],
                    "confidence_score": 0.3,
                    "raw_analysis": analysis_text,
                    "error": "JSON parsing failed"
                }

            return analysis_result

        except Exception as e:
            return {
                "error": f"LLM analysis failed: {str(e)}",
                "trading_pair": "Error",
                "timeframe": "Error",
                "technical_indicators": [],
                "chart_patterns": [],
                "support_levels": [],
                "resistance_levels": [],
                "trend_direction": "error",
                "trend_strength": "error",
                "key_observations": [f"Analysis failed: {str(e)}"],
                "confidence_score": 0.0
            }

    def _run(self, video_path: str, max_frames: int = 10, analysis_focus: str = "comprehensive") -> str:
        """Execute the video analysis tool."""
        try:
            # Check dependencies
            if not CV2_AVAILABLE:
                return json.dumps({
                    "error": "OpenCV (cv2) is not installed. Please install with: pip install opencv-python",
                    "success": False
                })
            
            if not OPENAI_AVAILABLE:
                return json.dumps({
                    "error": "OpenAI library is not installed. Please install with: pip install openai",
                    "success": False
                })
            
            if not self.client:
                return json.dumps({
                    "error": "OpenAI API key not configured. Please set OPENAI_API_KEY environment variable",
                    "success": False
                })

            # Validate video file exists
            if not os.path.exists(video_path):
                return json.dumps({
                    "error": f"Video file not found: {video_path}",
                    "success": False
                })

            # Extract frames from video
            frames = self._extract_frames(video_path, max_frames)
            
            if not frames:
                return json.dumps({
                    "error": "No frames could be extracted from video",
                    "success": False
                })

            # Analyze frames with multimodal LLM
            analysis_result = self._analyze_frames_with_llm(frames, analysis_focus)
            
            # Add metadata
            analysis_result.update({
                "success": True,
                "frames_processed": len(frames),
                "video_path": video_path,
                "analysis_timestamp": "2024-01-01T00:00:00Z"  # You might want to use actual timestamp
            })

            return json.dumps(analysis_result, indent=2)

        except Exception as e:
            error_result = {
                "error": f"Video analysis failed: {str(e)}",
                "success": False,
                "video_path": video_path
            }
            return json.dumps(error_result, indent=2)


# Create tool instance for import
video_analysis_tool = VideoAnalysisTool()