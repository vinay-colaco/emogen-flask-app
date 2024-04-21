import os
import time
import click
import pickle
import logging
import librosa
import numpy as np
import emailServer
from threading import Thread
from flask_cors import CORS
from datetime import datetime
from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model


app = Flask(__name__)
CORS(app)


# Load the saved model
with open('./model/final_full_gender.pkl', 'rb') as file:
    pipeline = pickle.load(file)

# Load the emotion prediction model
# emotion_model = load_model('./model/fourclass.h5')
# with open('./model/fourClass.pkl', 'rb') as file:
#     emotion_model = pickle.load(file)
emotion_model = load_model('./model/threeclass1.h5')

UPLOAD_FOLDER = './uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def gender_extract_features(file_path):
    y, sr = librosa.load(file_path, sr=None)
    # Extract dynamic number of MFCC coefficients
    mfccs = librosa.feature.mfcc(y=y, sr=sr)
    # Extract additional features
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
    # Concatenate all features
    features = np.concatenate([np.mean(mfccs, axis=1), np.mean(chroma, axis=1), np.mean(spectral_contrast, axis=1)])
    return features

def predict_gender(file_path):
    try:
        new_features = gender_extract_features(file_path)
        new_features = np.array(new_features).reshape(1, -1)

        # Predict and get confidence scores
        predictions_proba = pipeline.predict_proba(new_features)[0]
        predicted_class = pipeline.predict(new_features)[0]

        predicted_gender = "Male" if predicted_class == 0 else "Female"
        confidence_scores = {'Male': float(predictions_proba[0]), 'Female': float(predictions_proba[1])}

        # Return prediction and confidence scores as dictionary
        return {'predictedGender': predicted_gender, 'confidenceScores': confidence_scores}, 200
    except Exception as e:
        return {'error': str(e)}, 500
    
# For using fourclass.pkl/.h5 model
# def emotion_extract_features(file_path):
#     try:
#         audio, sample_rate = librosa.load(file_path, res_type='kaiser_fast')
#         mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40)
#         mfccs_processed = np.mean(mfccs.T, axis=0)
#     except Exception as e:
#         print("Error encountered while parsing file: ", file_path)
#         return None
#     return mfccs_processed

# def predict_emotion(file_path):
#     features = emotion_extract_features(file_path)
#     if features is not None:
#         features = np.reshape(features, (1, 1, -1))
#         prediction = emotion_model.predict(features)
#         confidence_scores = np.max(prediction, axis=1).astype(float)  # Convert to float
#         labels = ['High Valence-High Arousal', 'High Valence-Low Arousal', 'Low Valence-High Arousal', 'Low Valence-Low Arousal']
#         predicted_emotion = labels[np.argmax(prediction)]
#         return predicted_emotion, confidence_scores[0]
#     else:
#         return "Error processing the audio files.", 500  

# For ThreeClass emotion mdoel
def emotion_extract_features(file_path):
    try:
        audio, sample_rate = librosa.load(file_path, res_type='kaiser_fast')
        mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40)
        chroma = librosa.feature.chroma_stft(y=audio, sr=sample_rate)
        mel = librosa.feature.melspectrogram(y=audio, sr=sample_rate)
        contrast = librosa.feature.spectral_contrast(y=audio, sr=sample_rate)
        features = np.hstack((np.mean(mfccs, axis=1), np.mean(chroma, axis=1), 
                              np.mean(mel, axis=1), np.mean(contrast, axis=1)))
        # Pad features if necessary to match expected input shape (187 dimensions)
        if len(features) < 187:
            features = np.pad(features, ((0, 187 - len(features))), mode='constant')
    except Exception as e:
        print("Error encountered while parsing file: ", file_path)
        return None 
    return features

def predict_emotion(file_path):
    # Extract features
    features =emotion_extract_features(file_path)
    if features is not None:
        features = np.expand_dims(features, axis=0)  
        features = np.expand_dims(features, axis=0)  
        prediction = emotion_model.predict(features)
        confidence_scores = np.max(prediction, axis=1).astype(float)
        labels = ['Happy', 'Neutral', 'Sad']
        predicted_emotion = labels[np.argmax(prediction)]
        
        return predicted_emotion, confidence_scores[0]
    else:
        return "Error processing the audio file.", 500

        

@app.route('/')
def ping():
    return "Server is Fine"


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Save the uploaded file
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    try:


        request_time = time.time()
        request_arrival_time = datetime.now().strftime("%m/%d/%Y %I:%M %p")

        request_time = time.time()

        # Predict gender
        gender_prediction = predict_gender(file_path)
        gender_response_time = time.time()
        # Predict emotion
        emotion_request_time = time.time()
        emotion, confidence = predict_emotion(file_path)
        emotion_response_time = time.time()
        emotion_prediction = {'predictedEmotion': emotion, 'confidenceScore': confidence}

        # Combine responses
        combined_response = {
            'genderPrediction': gender_prediction,
            'emotionPrediction': emotion_prediction
        }
        
        response_time = time.time()


        total_time = response_time - request_time
        gender_total_response_time = gender_response_time - request_time
        emotion_total_response_time = emotion_response_time - emotion_request_time

        app.logger.info(f"Time taken to process the request and send the response: {total_time:.2f} seconds")
        app.logger.info(f"Time taken to process the request and send the response: {gender_total_response_time:.2f} seconds")
        app.logger.info(f"Time taken to process the request and send the response: {emotion_total_response_time:.2f} seconds")
        
        # mail part
        file_name = file.filename
        gender = gender_prediction[0]['predictedGender']
        response_sent_time = datetime.now().strftime("%m/%d/%Y %I:%M %p")

        email_thread = Thread(target=emailServer.email_service, args=(file_name, emotion, gender, request_arrival_time, response_sent_time, emotion_total_response_time, gender_total_response_time))
        email_thread.start()


        total_time = response_time - request_time
        app.logger.info(f"Time taken to process the request and send the response: {total_time:.2f} seconds")

        return jsonify(combined_response), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


