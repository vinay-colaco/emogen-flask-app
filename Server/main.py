import pickle
import os
import numpy as np
import librosa
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load the saved model
with open('./model/final_full_gender.pkl', 'rb') as file:
    pipeline = pickle.load(file)

# Load the emotion prediction model
with open('./model/fourClass.pkl', 'rb') as file:
    emotion_model = pickle.load(file)

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

        predicted_gender = "male" if predicted_class == 0 else "female"
        confidence_scores = {'Male': float(predictions_proba[0]), 'Female': float(predictions_proba[1])}

        # Return prediction and confidence scores as dictionary
        return {'predictedGender': predicted_gender, 'confidenceScores': confidence_scores}, 200
    except Exception as e:
        return {'error': str(e)}, 500

def emotion_extract_features(file_path):
    try:
        audio, sample_rate = librosa.load(file_path, res_type='kaiser_fast')
        mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40)
        mfccs_processed = np.mean(mfccs.T, axis=0)
    except Exception as e:
        print("Error encountered while parsing file: ", file_path)
        return None
    return mfccs_processed

def predict_emotion(file_path):
    features = emotion_extract_features(file_path)

    if features is not None:
        features = np.reshape(features, (1, 1, -1))
        prediction = emotion_model.predict(features)
        confidence_scores = np.max(prediction, axis=1).astype(float)  # Convert to float
        labels = ['High Valence-High Arousal', 'High Valence-Low Arousal', 'Low Valence-High Arousal', 'Low Valence-Low Arousal']
        predicted_emotion = labels[np.argmax(prediction)]
        return predicted_emotion, confidence_scores[0]
    else:
        return "Error processing the audio file.", 0.0  
        


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
        # Predict gender
        gender_prediction = predict_gender(file_path)

        # Predict emotion
        emotion, confidence = predict_emotion(file_path)
        emotion_prediction = {'predictedEmotion': emotion, 'confidenceScore': confidence}

        # Combine responses
        combined_response = {
            'genderPrediction': gender_prediction,
            'emotionPrediction': emotion_prediction
        }

        return jsonify(combined_response), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


