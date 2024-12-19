from flask import Flask, request, jsonify
import logging
from main_v2 import analyze_media
import os 
import tempfile
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

app=Flask(__name__)


@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Endpoint for media analysis with file uploads.
    """
    if 'video' not in request.files and 'image' not in request.files:
        logging.error("Invalid request structure")
        return jsonify({"error": "Request must contain at least 'video' or 'image' file"}), 400

    video_file = request.files.get('video')  # Optional video file
    image_file = request.files.get('image')  # Optional image file
    text_msg = request.form.get('text_msg', '')  # Additional text input

    primary_analysis = None
    additional_image_analysis = None

    try:
        # Analyze video file if provided
        if video_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
                video_file.save(temp_video.name)
                primary_analysis = analyze_media('video', temp_video.name, text_msg)

        # Analyze image file if provided
        if image_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_image:
                image_file.save(temp_image.name)
                additional_image_analysis = analyze_media('image', temp_image.name, text_msg)

        # Prepare response
        response = {
            "primary_analysis": primary_analysis,
            "additional_image_analysis": additional_image_analysis,
        }
        return jsonify(response)

    except Exception as e:
        logging.error(f"Error processing files: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        # Clean up temporary files
        if video_file:
            os.remove(temp_video.name)
        if image_file:
            os.remove(temp_image.name)
