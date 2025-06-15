# Dynamic Persona Generator

A sophisticated tool that creates psychological user profiles based on text analysis and evolves these personas over time with continued interaction.

![Dynamic Persona Generator](https://img.shields.io/badge/Hackathon-Project-blue)

## Overview

Dynamic Persona Generator creates detailed psychological profiles of users based on text analysis and conversation. The system analyzes written content to extract personality traits and generates evolving user personas that become more accurate over time as additional data is processed.

### Key Features

- **Psychological Profiling**: Extracts Big Five personality traits (Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism) from text
- **Dynamic Persona Evolution**: Personas evolve as more data is processed
- **Conversational Interface**: Talk directly with generated personas
- **LLM Integration**: Uses Siemens LiteLLM for advanced analysis and conversation
- **Visualizations**: Charts and detailed displays of personality traits

## Installation

1. **Clone the repository**
   ```
   git clone <repository-url>
   cd hackathon
   ```

2. **Create and activate a virtual environment**
   ```
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

4. **Create a .env file with your API key**
   ```
   LITELLM_API_KEY=your_litellm_api_key_here
   ```

## Usage

1. **Start the application**
   ```
   python app.py
   ```

2. **Access the web interface**
   Open your browser and go to: `http://localhost:5000`

3. **Generate synthetic data**
   Click "Generate Data" on the homepage to create demo data

4. **Create a persona**
   - Click "Analyze Data"
   - Enter a user ID
   - Choose either Text Analysis or Social Media Analysis
   - Submit text or social media username
   - View the generated persona

5. **Talk to a persona**
   - Go to any persona's detail page
   - Click "Talk to This Persona"
   - Start a conversation with the AI-powered persona

## Project Structure

```
hackathon/
├── app.py                  # Main Flask application
├── requirements.txt        # Project dependencies
├── templates/              # HTML templates
├── data/                   # Generated data files
│   ├── raw/                # Raw data (social posts, etc.)
│   ├── processed/          # Processed data files
│   └── personas/           # Stored persona files
└── src/                    # Source code
    ├── data_generator.py   # Synthetic data generation
    ├── api/                # API endpoints
    ├── collectors/         # Data collection modules
    │   └── social_media.py # Social media data collector
    ├── processors/         # Data processing modules
    │   └── text_analysis.py # Text analysis module
    ├── models/             # Core modeling components
    │   ├── persona_evolve.py # Persona generation logic
    │   └── trait_predictor.py # Personality trait prediction
    └── integrations/       # External API integrations
        └── persona_simulator.py # Persona conversation simulator
```

## Technical Details

### Architecture

The Dynamic Persona Generator uses a modular architecture:

1. **Data Collection**: Gathers text data from direct input or social media
2. **Text Analysis**: Processes text to extract linguistic features
3. **Trait Prediction**: Predicts Big Five personality traits from linguistic features
4. **Persona Generation**: Creates detailed personas based on traits
5. **Persona Evolution**: Updates personas over time with new data
6. **Conversation**: Enables interactive dialogue with personas using LLM

### Technologies Used

- **Backend**: Python, Flask
- **AI/ML**: LiteLLM (Siemens API)
- **Data Processing**: Pandas, NumPy
- **Frontend**: HTML, Bootstrap, Chart.js
- **Data Storage**: JSON/CSV files

## Future Enhancements

- Real social media API integrations
- User authentication and multi-user support
- Long-term persona memory and more sophisticated evolution
- Expanded trait models beyond Big Five
- More detailed behavior prediction
- Mobile app integration

## Team

Created for the Siemens Hackathon 2024

## License

This project is licensed for demonstration and educational purposes only.