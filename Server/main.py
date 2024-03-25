import pickle
import numpy as np
import librosa
from flask import Flask, request, jsonify
from flask_cors import CORS
from io import BytesIO

app = Flask(__name__)
CORS(app)

# Load the saved model
with open('./model/final_full_gender.pkl', 'rb') as file:
    pipeline = pickle.load(file)


def extract_features(audio_data):
    y, sr = librosa.load(audio_data, sr=None)
    # Extract dynamic number of MFCC coefficients
    mfccs = librosa.feature.mfcc(y=y, sr=sr)
    # Extract additional features
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
    # Concatenate all features
    features = np.concatenate([np.mean(mfccs, axis=1), np.mean(chroma, axis=1), np.mean(spectral_contrast, axis=1)])
    return features


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

    # Extract features and make prediction
    try:
        audio_data = BytesIO(file.read())
        new_features = extract_features(audio_data)
        new_features = np.array(new_features).reshape(1, -1)
        # Predict and get confidence scores
        predictions_proba = pipeline.predict_proba(new_features)[0]
        predicted_class = pipeline.predict(new_features)[0]

        predicted_gender = "male" if predicted_class == 0 else "female"
        confidence_scores = {'Male': predictions_proba[0], 'Female': predictions_proba[1]}

        # Return prediction and confidence scores
        return jsonify({'predictedGender': predicted_gender, 'confidenceScores': confidence_scores}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)






















