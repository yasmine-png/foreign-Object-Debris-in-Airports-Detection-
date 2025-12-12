# 🛫 FOD Detection System - Airport Runway Safety

> **Foreign Object Debris (FOD) Detection System** - A comprehensive AI-powered solution for detecting and managing foreign objects on airport runways to enhance aviation safety.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.2-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2-blue.svg)](https://www.typescriptlang.org/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-8.1.0-green.svg)](https://github.com/ultralytics/ultralytics)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A modern, responsive web application for **Foreign Object Debris (FOD) detection** on airport runways. Built with React frontend and Flask backend, using **YOLOv8** for real-time object detection, **Autoencoder** for anomaly detection, **SAM (Segment Anything Model)** for precise segmentation, and **MongoDB** for data persistence.

## ✨ Features

- 🎯 **Real-time Object Detection**: YOLOv8-powered detection with high accuracy
- 🔬 **Anomaly Detection**: Autoencoder-based anomaly detection for identifying unusual patterns
- 🖼️ **Image & Video Processing**: Support for both image uploads and video analysis
- 🎨 **Interactive UI**: Modern, responsive dashboard with real-time visualization
- 📊 **Risk Assessment**: Automatic risk level classification (High/Medium/Low)
- 🔍 **Advanced Segmentation**: SAM (Segment Anything Model) integration for precise object segmentation
- 🗄️ **Data Persistence**: MongoDB integration for storing detection results and metadata
- 📈 **Analytics Dashboard**: Detailed results panel with filtering and sorting capabilities
- 🚀 **Production Ready**: Docker support and deployment configurations included

## Tech Stack

### Frontend
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Vite** for build tooling

### Backend
- **Flask** for RESTful API server
- **YOLOv8 (Ultralytics)** for object detection
- **Autoencoder (PyTorch)** for anomaly detection
- **SAM (Segment Anything Model)** for image segmentation
- **MongoDB** for data storage and retrieval
- **OpenCV** for image/video processing
- **Python 3.8+**

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Python 3.8 or higher
- pip

### Installation

#### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
```

3. Activate the virtual environment:
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

4. Install Python dependencies:
```bash
pip install -r requirements.txt
```

5. Verify the model path in `backend/app.py`:
```python
MODEL_PATH = r"C:\Users\ybouk\OneDrive\Bureau\projet_fod\yolov8n_fod_final_v7\weights\best.pt"
```

6. Start the Flask server:
```bash
python app.py
```

The backend will be available at `http://localhost:5000`

#### Frontend Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open your browser and navigate to `http://localhost:5173`

### Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Project Structure

```
projet_fod/
├── backend/
│   ├── app.py                  # Flask API server with YOLOv8 integration
│   ├── requirements.txt        # Python dependencies
│   └── README.md              # Backend documentation
├── src/
│   ├── components/
│   │   ├── Header.tsx              # Top navigation bar
│   │   ├── DetectionWorkspace.tsx  # Main detection area (left column)
│   │   ├── ResultsPanel.tsx        # Results and metadata (right column)
│   │   ├── AIScanEffect.tsx        # AI scanning visual effects
│   │   └── AIProcessingIndicator.tsx # Processing status indicator
│   ├── services/
│   │   └── api.ts             # API service for backend communication
│   ├── types.ts               # TypeScript type definitions
│   ├── App.tsx                # Main application component
│   ├── main.tsx               # Application entry point
│   └── index.css              # Global styles and Tailwind imports
├── backend/
│   └── autoencoder_fod.pth    # Pre-trained Autoencoder model for anomaly detection
└── yolov8n_fod_final_v7/
    └── weights/
        └── best.pt            # Pre-trained YOLOv8 model
```

## Usage

1. **Start the Backend**: Make sure the Flask server is running on port 5000
2. **Start the Frontend**: Launch the React development server
3. **Upload an Image**: Click "Upload Image" and select an image file
4. **View Detections**: The YOLOv8 model will process the image and display detected objects with bounding boxes
5. **Filter Results**: Use the filters in the Results Panel to sort by risk level or confidence
6. **Review Details**: Each detection shows the object label, confidence score, risk level, and position

## Design Notes

- Clean, modern dashboard-style interface
- Responsive layout that stacks on mobile devices
- Color-coded risk levels (High: Red, Medium: Yellow, Low: Green)
- Smooth transitions and hover effects
- Accessible UI with proper contrast and spacing

## 🔬 Anomaly Detection with Autoencoder

The system includes an **Autoencoder-based anomaly detection** model that complements the YOLOv8 object detection. This dual approach provides:

### How It Works

1. **Training Phase**: The autoencoder is trained on normal runway images to learn the typical patterns and structures
2. **Inference Phase**: 
   - Input images are encoded and then decoded (reconstructed) by the autoencoder
   - The reconstruction error (MSE - Mean Squared Error) is calculated
   - High reconstruction errors indicate anomalies or unusual patterns
3. **Anomaly Score**: A normalized score (0-1) is computed, where higher values indicate greater anomaly likelihood

### Features

- **Unsupervised Learning**: Detects anomalies without requiring labeled anomaly data
- **Complementary Detection**: Works alongside YOLOv8 to catch objects that might be missed
- **Reconstruction Error**: Provides quantitative measure of image abnormality
- **Configurable Threshold**: Adjustable sensitivity for anomaly detection

### Model Details

- **Model File**: `backend/autoencoder_fod.pth`
- **Input Size**: 224x224 pixels
- **Framework**: PyTorch
- **Device Support**: CPU and CUDA (GPU)

The autoencoder model is automatically loaded at server startup if available. Check the server logs to confirm the model status.

## API Endpoints

### GET /api/health
Check if the backend is running and the models are loaded.

**Response**:
```json
{
  "status": "ok",
  "model_loaded": true,
  "autoencoder_available": true
}
```

### POST /api/detect
Upload an image for FOD detection. Returns detected objects with bounding boxes, confidence scores, and risk levels.

**Request**: multipart/form-data with `image` field

**Response**: JSON with array of detections and anomaly information:
```json
{
  "detections": [...],
  "count": 1,
  "anomaly_detection": {
    "is_anomaly": false,
    "reconstruction_error": 0.023,
    "anomaly_score": 0.23
  }
}
```

## Notes

- The YOLOv8 model is loaded once at server startup
- The Autoencoder model is automatically loaded if `autoencoder_fod.pth` is present in the backend directory
- Images are processed with a minimum confidence threshold of 0.25 for YOLOv8
- Anomaly detection threshold is configurable (default: 0.1)
- Bounding box coordinates are returned as percentages of image dimensions
- Risk levels are automatically determined based on confidence scores
- Both models support CPU and GPU (CUDA) inference

## 📚 Additional Documentation

- [Backend Documentation](backend/README.md)
- [MongoDB Setup Guide](MONGODB_SETUP.md)
- [SAM Activation Guide](backend/ACTIVATION_SAM.md)
- [Deployment Instructions](DEPLOY_INSTRUCTIONS.md)
- [Quick Start Guide](DEMARRAGE_INTERFACE.md)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**Yasmine**

- GitHub: [@yasmine-png](https://github.com/yasmine-png)

## 🙏 Acknowledgments

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics) for the detection model
- [Segment Anything Model (SAM)](https://github.com/facebookresearch/segment-anything) for segmentation capabilities
- PyTorch for the autoencoder framework

