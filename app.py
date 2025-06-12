# app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import os
import json
from src.data_generator import SyntheticDataGenerator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# API endpoint (FastAPI running on another port)
API_BASE_URL = "http://localhost:8000"

@app.route('/')
def index():
    # Check if OpenAI API key is set
    has_api_key = bool(os.getenv("LITELLM_API_KEY"))
    return render_template('index.html', has_api_key=has_api_key)

@app.route('/generate-data', methods=['GET'])
def generate_data():
    """Generate synthetic data for demo"""
    generator = SyntheticDataGenerator()
    generator.generate_all_data()
    return redirect(url_for('index'))

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    if request.method == 'POST':
        analysis_type = request.form.get('analysis_type')
        user_id = request.form.get('user_id')
        
        if not user_id:
            return render_template('error.html', message="User ID is required")
        
        if analysis_type == 'text':
            text = request.form.get('text')
            if not text:
                return render_template('error.html', message="Text is required")
                
            # Call API to analyze text
            response = requests.post(
                f"{API_BASE_URL}/analyze-text",
                json={"user_id": user_id, "texts": [text]}
            )
            
        elif analysis_type == 'social':
            username = request.form.get('username')
            platform = request.form.get('platform', 'twitter')
            
            if not username:
                return render_template('error.html', message="Username is required")
                
            # Call API to analyze social media
            response = requests.post(
                f"{API_BASE_URL}/analyze-social",
                json={"user_id": user_id, "username": username, "platform": platform}
            )
        else:
            return render_template('error.html', message="Invalid analysis type")
            
        if response.status_code == 200:
            persona = response.json()
            return render_template('results.html', persona=persona)
        else:
            return render_template('error.html', message=f"API Error: {response.text}")
    
    return render_template('analyze.html')

@app.route('/personas')
def personas():
    # Get all personas from API
    response = requests.get(f"{API_BASE_URL}/personas")
    
    if response.status_code == 200:
        personas = response.json()
        return render_template('personas.html', personas=personas)
    else:
        return render_template('error.html', message=f"API Error: {response.text}")

@app.route('/persona/<user_id>')
def persona_detail(user_id):
    # Get specific persona from API
    response = requests.get(f"{API_BASE_URL}/persona/{user_id}")
    
    if response.status_code == 200:
        data = response.json()
        return render_template('persona_detail.html', persona=data)
    else:
        return render_template('error.html', message=f"API Error: {response.text}")

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    app.run(debug=True, port=5000)