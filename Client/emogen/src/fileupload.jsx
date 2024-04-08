import { useState } from 'react';
import axios from './axiosInstance';

function FileUpload() {
  const [file, setFile] = useState(null);
  const [predictions, setPredictions] = useState(null);

  const onFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const onFileUpload = () => {
    const formData = new FormData();
    formData.append("file", file);

    axios.post("/upload", formData)
      .then((response) => {
        setPredictions(response.data);
      })
      .catch((error) => {
        console.error("Error uploading file:", error);
      });
  };

  return (
    <div>
      <input type="file" onChange={onFileChange} />
      <button onClick={onFileUpload}>Upload</button>
      {predictions && (
        <div>
          <div>Predicted Gender: {predictions.genderPrediction[0].predictedGender}</div>
          <div>Confidence Scores:</div>
          <ul>
            <li>Male: {predictions.genderPrediction[0].confidenceScores.Male}</li>
            <li>Female: {predictions.genderPrediction[0].confidenceScores.Female}</li>
            <li>Predicted Emotion: {predictions.emotionPrediction.predictedEmotion}</li>
            <li>Confidence Score: {predictions.emotionPrediction.confidenceScore}</li>
          </ul>
        </div>
      )}
    </div>
  );
  
}

export default FileUpload;
