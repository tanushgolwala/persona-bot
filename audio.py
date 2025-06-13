import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import tensorflow as tf
from tensorflow import keras
import speech_recognition as sr
import queue
import threading
import time
import pickle
import os

class ConversationLearningSystem:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.conversation_buffer = queue.Queue()
        self.conversation_history = []
        self.model = self.create_model()
        self.is_training = False
        self.model_version = 0
        
        # Create directory for saving conversations and models
        os.makedirs('conversation_data', exist_ok=True)
        os.makedirs('models', exist_ok=True)
        
        # Load previous conversations if they exist
        self.load_conversation_history()

    def create_model(self):
        model = keras.Sequential([
            keras.layers.Dense(256, activation='relu', input_shape=(1000,)),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(128, activation='relu'),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dense(1000, activation='softmax')
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        return model

    def save_conversation_history(self):
        with open('conversation_data/conversation_history.pkl', 'wb') as f:
            pickle.dump(self.conversation_history, f)

    def load_conversation_history(self):
        try:
            with open('conversation_data/conversation_history.pkl', 'rb') as f:
                self.conversation_history = pickle.load(f)
            print(f"Loaded {len(self.conversation_history)} previous conversations")
        except FileNotFoundError:
            print("No previous conversation history found")

    def save_model(self):
        self.model.save(f'models/model_v{self.model_version}.h5')
        print(f"Model saved as version {self.model_version}")

    def load_latest_model(self):
        try:
            latest_version = max([int(f.split('_v')[1].split('.')[0]) 
                                for f in os.listdir('models') 
                                if f.startswith('model_v')])
            self.model = keras.models.load_model(f'models/model_v{latest_version}.h5')
            self.model_version = latest_version
            print(f"Loaded model version {latest_version}")
        except ValueError:
            print("No previous model found")

    def detect_speech(self):
        with sr.Microphone() as source:
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)
            
            try:
                text = self.recognizer.recognize_google(audio)
                return text.lower()
            except sr.UnknownValueError:
                print("Could not understand audio")
                return None
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
                return None

    def train_model_incremental(self):
        while True:
            if not self.conversation_buffer.empty() and not self.is_training:
                self.is_training = True
                print("\nTraining model with new conversations...")
                
                # Get all available conversations from buffer
                new_conversations = []
                while not self.conversation_buffer.empty():
                    new_conversations.append(self.conversation_buffer.get())
                
                # Add to conversation history
                self.conversation_history.extend(new_conversations)
                
                # Prepare training data
                questions = [conv[0] for conv in self.conversation_history]
                answers = [conv[1] for conv in self.conversation_history]
                
                # Vectorize the text
                X = self.vectorizer.fit_transform(questions).toarray()
                y = self.vectorizer.transform(answers).toarray()
                
                # Train the model
                self.model.fit(
                    X, y,
                    epochs=5,
                    batch_size=32,
                    verbose=1
                )
                
                # Save updated model and conversations
                self.model_version += 1
                self.save_model()
                self.save_conversation_history()
                
                self.is_training = False
                print("\nModel training completed")
            
            time.sleep(1)  # Prevent CPU overload

    def predict_response(self, question):
        if not self.conversation_history:
            return "I haven't learned any conversations yet."
        
        question_vec = self.vectorizer.transform([question]).toarray()
        prediction = self.model.predict(question_vec)
        predicted_response = self.vectorizer.inverse_transform(prediction)[0]
        return " ".join(predicted_response)

def main():
    system = ConversationLearningSystem()
    
    # Start training thread
    training_thread = threading.Thread(
        target=system.train_model_incremental, 
        daemon=True
    )
    training_thread.start()
    
    print("Starting conversation recording system")
    print("Instructions:")
    print("1. Speak clearly into the microphone")
    print("2. The system will record pairs of conversations")
    print("3. Say 'quit' to exit")
    print("4. Say 'predict' to enter prediction mode")
    
    while True:
        print("\nSpeak the question/statement:")
        question = system.detect_speech()
        
        if question is None:
            continue
            
        if question == 'quit':
            break
            
        if question == 'predict':
            print("Entering prediction mode. Say your question:")
            pred_question = system.detect_speech()
            if pred_question:
                predicted = system.predict_response(pred_question)
                print(f"Predicted response: {predicted}")
            continue
        
        print(f"Question recorded: {question}")
        print("Speak the response:")
        
        response = system.detect_speech()
        if response:
            print(f"Response recorded: {response}")
            # Add to training buffer
            system.conversation_buffer.put((question, response))
            print("Conversation pair added to training buffer")

if __name__ == "__main__":
    main()