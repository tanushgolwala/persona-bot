from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os
import json
from datetime import datetime
from dotenv import load_dotenv
 
# Import your core components
from src.data_generator import SyntheticDataGenerator
from src.processors.text_analysis import TextAnalyzer
from src.models.trait_predictor import PersonalityTraitPredictor
from src.models.persona_evolve import DynamicPersonaGenerator
from src.collectors.social_media import SocialMediaCollector
from src.integrations.persona_simulator import PersonaSimulator
 
# Load environment variables
load_dotenv()
 
app = Flask(__name__, static_folder='static', static_url_path='/static')
 
# Initialize components directly in the Flask app
text_analyzer = TextAnalyzer()
trait_predictor = PersonalityTraitPredictor()
persona_generator = DynamicPersonaGenerator()
social_collector = SocialMediaCollector()
persona_simulator = PersonaSimulator()
 
# Try to load any existing persona data
try:
    persona_generator.load_personas()
except Exception as e:
    print(f"Could not load existing personas: {e}")
 
@app.route('/')
def index():
    # Check if API key is set
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
        quirk = request.form.get('quirk', '').strip()

        if not user_id:
            return render_template('error.html', message="User ID is required")

        if analysis_type == 'text':
            text = request.form.get('text')
            if not text:
                return render_template('error.html', message="Text is required")

            # Process text analysis directly here instead of calling API
            features = text_analyzer.extract_linguistic_features([text])
            features_df = pd.DataFrame({k: features[k] for k in features})

            # Predict traits
            traits_df = trait_predictor.predict(features_df)
            avg_traits = traits_df.mean().to_dict()

            # Generate persona (with quirk)
            persona = persona_generator.generate_user_persona(user_id, avg_traits, [text], quirk=quirk)

            return render_template('results.html', persona={"user_id": user_id, "persona": persona})

        elif analysis_type == 'social':
            username = request.form.get('username')
            platform = request.form.get('platform', 'twitter')

            if not username:
                return render_template('error.html', message="Username is required")

            # Add debug output
            print(f"Starting social media analysis for {username} on {platform}")
            
            try:
                # Collect social media posts
                posts = social_collector.collect_user_data(username, platform)
                
                # Debug output
                print(f"Retrieved {len(posts)} posts for {username} on {platform}")
                
                # Check for error messages in posts (if using the error format I suggested earlier)
                if posts and isinstance(posts[0], dict) and "error" in posts[0]:
                    error_message = posts[0]["error"]
                    print(f"Error from social collector: {error_message}")
                    return render_template('error.html', message=error_message)
                
                if not posts:
                    print(f"No posts found for {username} on {platform}")
                    return render_template('error.html', 
                        message=f"No posts found for {username} on {platform}. Try another username or platform.")
                
                # Verify we have text content
                texts = [post.get('text', '') for post in posts if post.get('text', '').strip()]
                
                if not texts:
                    print(f"No text content found in posts for {username}")
                    return render_template('error.html', 
                        message=f"Retrieved posts for {username}, but couldn't extract usable text content.")
                
                print(f"Processing {len(texts)} text samples from social media")
                
                # Save sample texts for debugging
                import os
                os.makedirs("data/debug", exist_ok=True)
                with open(f"data/debug/social_texts_{username}.txt", "w", encoding="utf-8") as f:
                    f.write("\n---\n".join(texts[:5]))  # Save first 5 texts as sample
                
                # Continue with analysis
                features = text_analyzer.extract_linguistic_features(texts)
                features_df = pd.DataFrame({k: features[k] for k in features})
                traits_df = trait_predictor.predict(features_df)
                avg_traits = traits_df.mean().to_dict()

                # Generate persona
                persona = persona_generator.generate_user_persona(user_id, avg_traits, texts, quirk=quirk)

                return render_template('results.html', persona={"user_id": user_id, "persona": persona})
                
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                print(f"Error during social media analysis: {str(e)}")
                print(error_details)
                return render_template('error.html', 
                    message=f"Error analyzing social media data: {str(e)}")

        else:
            return render_template('error.html', message="Invalid analysis type")

    return render_template('analyze.html')

@app.route('/test-social/<platform>/<username>')
def test_social(platform, username):
    # Test the social media collector directly
    print(f"Testing social media collector for {username} on {platform}")
    
    try:
        results = social_collector.collect_user_data(username, platform)
        
        # Create an HTML response showing the results
        html = f"<html><body><h1>Social Media Collection Test</h1>"
        html += f"<p>Platform: {platform}</p>"
        html += f"<p>Username: {username}</p>"
        html += f"<p>Results count: {len(results)}</p>"
        
        # Show any saved file locations
        html += "<h2>Generated Files:</h2>"
        scraped_dir = "data/scraped"
        if os.path.exists(scraped_dir):
            files = [f for f in os.listdir(scraped_dir) if username in f]
            for file in files:
                html += f"<p>{os.path.join(scraped_dir, file)}</p>"
        else:
            html += "<p>Scraped directory does not exist</p>"
        
        # Display the results
        html += "<h2>Results:</h2><pre>"
        import json
        html += json.dumps(results[:5], indent=2, default=str)  # Show first 5 results
        html += "</pre></body></html>"
        
        return html
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"<html><body><h1>Error</h1><p>{str(e)}</p><pre>{error_details}</pre></body></html>"

@app.route('/personas')
def personas():
    # Get all personas directly
    user_ids = list(persona_generator.user_personas.keys())
    result = {
        "total": len(persona_generator.user_personas),
        "personas": {uid: persona_generator.user_personas[uid] for uid in user_ids[:10]}  # Limit to first 10
    }
    return render_template('personas.html', personas=result)
 
@app.route('/persona/<user_id>')
def persona_detail(user_id):
    # Get specific persona directly
    if user_id in persona_generator.user_personas:
        persona = {"user_id": user_id, "persona": persona_generator.user_personas[user_id]}
        return render_template('persona_detail.html', persona=persona)
    else:
        return render_template('error.html', message=f"No persona found for user {user_id}")
 
@app.route('/converse/<user_id>', methods=['GET', 'POST'])
def converse(user_id):
    """Have a conversation with a persona"""
    if user_id not in persona_generator.user_personas:
        return render_template('error.html', message=f"No persona found for user {user_id}")
    persona = persona_generator.user_personas[user_id]
    if request.method == 'POST':
        user_message = request.form.get('message', '')
        if user_message:
            # Get response from persona simulator
            response = persona_simulator.converse_with_persona(user_id, persona, user_message)
            return render_template('conversation.html', 
                                 persona={"user_id": user_id, "persona": persona},
                                 conversation=persona_simulator.conversations.get(user_id, []),
                                 response=response)
    # For GET requests or empty messages
    return render_template('conversation.html', 
                         persona={"user_id": user_id, "persona": persona},
                         conversation=persona_simulator.conversations.get(user_id, []))
 
if __name__ == '__main__':
    # Create directories if they don't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    os.makedirs('data/personas', exist_ok=True)
    app.run(debug=True, port=5000)