import axios from 'axios';

const axiosInstance = axios.create({
  baseURL: 'http://localhost:5000/', // Replace with your Flask backend URL
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});

export default axiosInstance;
