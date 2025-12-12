# FOD Detection - Airport Runway UI

A modern, responsive web application for Foreign Object Debris (FOD) detection on airport runways. Built with React frontend and Flask backend, using YOLOv8 for object detection.

## Features

- **Detection Workspace**: Large, interactive area for viewing images with detection overlays
- **Image Upload**: Upload images for FOD detection
- **Real-time Detection Display**: Bounding boxes with risk level indicators from YOLOv8 model
- **Results Panel**: Detailed list of detected objects with filtering and sorting
- **Model Information**: Display of selected AI models and deployment tags
- **YOLOv8 Integration**: Pre-trained YOLOv8 model for accurate FOD detection

## Tech Stack

### Frontend
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Vite** for build tooling

### Backend
- **Flask** for API server
- **YOLOv8 (Ultralytics)** for object detection
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

## API Endpoints

### GET /api/health
Check if the backend is running and the model is loaded.

### POST /api/detect
Upload an image for FOD detection. Returns detected objects with bounding boxes, confidence scores, and risk levels.

**Request**: multipart/form-data with `image` field
**Response**: JSON with array of detections

## Notes

- The YOLOv8 model is loaded once at server startup
- Images are processed with a minimum confidence threshold of 0.25
- Bounding box coordinates are returned as percentages of image dimensions
- Risk levels are automatically determined based on confidence scores

## License

MIT

