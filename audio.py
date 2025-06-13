import speech_recognition as sr
import threading
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from queue import Queue
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import warnings
import os
import certifi
warnings.filterwarnings("ignore")

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

class SpeechPredictionSystem:
    def __init__(self):
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300  # Adjust based on environment noise
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8   # Shorter pauses between phrases

        # Initialize language model for prediction
        self.model_name = "distilgpt2"  # Smaller version of GPT-2 for faster inference
        self.tokenizer = GPT2Tokenizer.from_pretrained(self.model_name)
        self.model = GPT2LMHeadModel.from_pretrained(self.model_name)
        
        # Speech history
        self.conversation_history = []
        self.max_history = 5
        
        # For storing transcriptions and predictions
        self.last_transcription = ""
        self.current_prediction = ""
        self.transcription_queue = Queue()
        self.similarity_scores = []
        
        # For visualization
        self.fig, self.axs = None, None
        self.active = False
        self.plot_data = {
            'timestamps': [],
            'actual_texts': [],
            'predicted_texts': [],
            'similarity_scores': []
        }
        self.max_display_points = 10  # Number of points to display in plots
        
    def start(self):
        """Start the speech detection and prediction system"""
        self.active = True
        
        # Start speech recognition thread
        self.recognition_thread = threading.Thread(target=self._recognition_loop)
        self.recognition_thread.daemon = True
        self.recognition_thread.start()
        
        # Setup visualization
        self._setup_visualization()
        
    def stop(self):
        """Stop the system"""
        self.active = False
        plt.close()
        
    def _recognition_loop(self):
        """Main loop for speech recognition"""
        with sr.Microphone() as source:
            print("Adjusting for ambient noise... Please wait.")
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
            print("Speech detection active. Start speaking...")
            
            while self.active:
                try:
                    # Listen for speech
                    print("Listening...")
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=15)
                    
                    # Try to recognize the speech
                    print("Processing speech...")
                    text = self.recognizer.recognize_google(audio)
                    print(f"Detected: {text}")
                    
                    # Generate a prediction before updating history
                    prediction = self._generate_prediction()
                    print(f"Prediction: {prediction}")
                    
                    # Calculate similarity between actual and predicted
                    similarity = self._calculate_similarity(text, prediction)
                    print(f"Similarity score: {similarity:.2f}")
                    
                    # Update conversation history
                    self._update_history(text)
                    
                    # Add to queue for visualization
                    timestamp = time.time()
                    self.transcription_queue.put((timestamp, text, prediction, similarity))
                    
                except sr.WaitTimeoutError:
                    print("No speech detected...")
                    continue
                except sr.UnknownValueError:
                    print("Could not understand audio...")
                    continue
                except sr.RequestError as e:
                    print(f"Could not request results; {e}")
                    continue
                except Exception as e:
                    print(f"Error: {e}")
                    continue
                    
    def _update_history(self, text):
        """Update the conversation history"""
        self.conversation_history.append(text)
        if len(self.conversation_history) > self.max_history:
            self.conversation_history.pop(0)
        self.last_transcription = text
                
    def _generate_prediction(self):
        """Generate a prediction of what might be said next"""
        if not self.conversation_history:
            return "Hello there."  # Default prediction if no history
            
        # Combine history for context
        context = " ".join(self.conversation_history[-3:]) if len(self.conversation_history) >= 3 else " ".join(self.conversation_history)
        
        try:
            # Tokenize input
            inputs = self.tokenizer.encode(context, return_tensors="pt")
            
            # Generate prediction
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=50,
                    num_return_sequences=1,
                    temperature=0.7,
                    top_k=50,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode prediction
            predicted_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the new part (not the input context)
            new_prediction = predicted_text[len(context):].strip()
            if not new_prediction:
                new_prediction = "I'm not sure what comes next."
                
            self.current_prediction = new_prediction
            return new_prediction
        except Exception as e:
            print(f"Prediction error: {e}")
            return "I'm not sure what comes next."
            
    def _calculate_similarity(self, actual, predicted):
        """Calculate a similarity score between actual and predicted text"""
        # Convert to lowercase and split into words
        actual_words = set(actual.lower().split())
        predicted_words = set(predicted.lower().split())
        
        # Calculate Jaccard similarity (intersection over union)
        if not actual_words or not predicted_words:
            return 0.0
            
        intersection = len(actual_words.intersection(predicted_words))
        union = len(actual_words.union(predicted_words))
        
        similarity = intersection / union if union > 0 else 0.0
        self.similarity_scores.append(similarity)
        
        return similarity
        
    def _setup_visualization(self):
        """Set up visualization for comparing predicted vs actual speech"""
        plt.ion()  # Interactive mode
        self.fig, self.axs = plt.subplots(2, 1, figsize=(12, 10))
        plt.tight_layout(pad=4.0)
        
        # Text display area (top subplot)
        self.axs[0].axis('off')  # No axes for text display
        self.axs[0].set_title('Speech Comparison')
        self.text_display = self.axs[0].text(
            0.5, 0.5, 
            "Waiting for speech...\n\nActual: \nPredicted: ", 
            ha='center', va='center',
            fontsize=12, wrap=True
        )
        
        # Similarity score plot (bottom subplot)
        self.axs[1].set_title('Prediction Accuracy')
        self.axs[1].set_xlabel('Time')
        self.axs[1].set_ylabel('Similarity Score (0-1)')
        self.axs[1].set_ylim(0, 1)
        self.similarity_line, = self.axs[1].plot([], [], 'b-o', label='Similarity Score')
        self.axs[1].legend()
        
        # Create animation
        self.ani = FuncAnimation(
            self.fig, 
            self._update_plots, 
            interval=100,
            blit=False
        )
        
        plt.show()
        
    def _update_plots(self, frame):
        """Update the visualization with new data"""
        # Process any new transcriptions in the queue
        while not self.transcription_queue.empty():
            timestamp, actual, predicted, similarity = self.transcription_queue.get()
            
            # Add to plot data
            self.plot_data['timestamps'].append(timestamp)
            self.plot_data['actual_texts'].append(actual)
            self.plot_data['predicted_texts'].append(predicted)
            self.plot_data['similarity_scores'].append(similarity)
            
            # Keep data within display limit
            if len(self.plot_data['timestamps']) > self.max_display_points:
                self.plot_data['timestamps'] = self.plot_data['timestamps'][-self.max_display_points:]
                self.plot_data['actual_texts'] = self.plot_data['actual_texts'][-self.max_display_points:]
                self.plot_data['predicted_texts'] = self.plot_data['predicted_texts'][-self.max_display_points:]
                self.plot_data['similarity_scores'] = self.plot_data['similarity_scores'][-self.max_display_points:]
        
        # Update text display if we have data
        if self.plot_data['actual_texts']:
            latest_actual = self.plot_data['actual_texts'][-1]
            latest_pred = self.plot_data['predicted_texts'][-1]
            
            display_text = f"EXPECTED (ACTUAL):\n{latest_actual}\n\nPREDICTED:\n{latest_pred}"
            
            # Add the 3 most recent pairs for context
            if len(self.plot_data['actual_texts']) > 1:
                display_text += "\n\n--- RECENT HISTORY ---"
                for i in range(min(3, len(self.plot_data['actual_texts'])-1)):
                    idx = -2-i
                    if idx >= -len(self.plot_data['actual_texts']):
                        display_text += f"\n\nActual: {self.plot_data['actual_texts'][idx]}\nPredicted: {self.plot_data['predicted_texts'][idx]}"
                    
            self.text_display.set_text(display_text)
        
        # Update similarity plot
        if self.plot_data['timestamps']:
            # Convert timestamps to relative seconds for display
            relative_times = [t - self.plot_data['timestamps'][0] for t in self.plot_data['timestamps']]
            
            self.similarity_line.set_data(relative_times, self.plot_data['similarity_scores'])
            self.axs[1].set_xlim(0, max(relative_times) + 1 if relative_times else 1)
            
        return self.text_display, self.similarity_line

def print_comparison_table(system):
    """Print a formatted table of predictions vs actual speech"""
    if not system.plot_data['actual_texts']:
        print("No speech data collected yet.")
        return
        
    print("\n" + "="*80)
    print(f"{'TIMESTAMP':<12} | {'EXPECTED (ACTUAL)':<30} | {'PREDICTED':<30}")
    print("-"*80)
    
    for i in range(len(system.plot_data['timestamps'])):
        timestamp = system.plot_data['timestamps'][i]
        actual = system.plot_data['actual_texts'][i]
        predicted = system.plot_data['predicted_texts'][i]
        
        # Truncate long strings for display
        if len(actual) > 27:
            actual = actual[:27] + "..."
        if len(predicted) > 27:
            predicted = predicted[:27] + "..."
            
        print(f"{timestamp:<12.1f} | {actual:<30} | {predicted:<30}")
    
    print("="*80)
    print(f"Average Prediction Similarity: {np.mean(system.plot_data['similarity_scores']):.2f}")
    print("="*80 + "\n")

def main():
    print("Starting Speech Prediction System...")
    print("This system will detect your speech, predict what might come next,")
    print("and compare the prediction with what you actually say.")
    
    system = SpeechPredictionSystem()
    
    try:
        system.start()
        
        # Main loop
        while True:
            time.sleep(5)  # Update comparison table periodically
            print_comparison_table(system)
            
    except KeyboardInterrupt:
        print("\nStopping system...")
    finally:
        system.stop()
        print("System stopped.")

if __name__ == "__main__":
    main()