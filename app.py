from flask import Flask, request, jsonify, send_file
from ultralytics import YOLO
import os
import cv2
import numpy as np
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

model = YOLO("yolov8n.pt")  # Pretrained YOLOv8 model

@app.route('/')
def home():
    return "✅ Grill AI API is live!"

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        filename = f"{uuid.uuid4().hex}_{file.filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Detect and apply grill
        processed_path = process_image(filepath)

        return jsonify({
            'message': 'Grill design applied',
            'processed_image_url': f"/processed/{os.path.basename(processed_path)}"
        })

    # GET form for manual upload
    return '''
        <h2>Upload House Image</h2>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="file" required>
            <input type="submit" value="Upload">
        </form>
    '''

@app.route('/processed/<filename>')
def serve_processed_image(filename):
    path = os.path.join(PROCESSED_FOLDER, filename)
    return send_file(path, mimetype='image/jpeg')

def process_image(image_path):
    image = cv2.imread(image_path)
    results = model(image)[0]

    for box in results.boxes:
        cls = int(box.cls[0])
        name = model.names[cls]
        if name.lower() in ['window', 'door', 'building']:  # Optional: 'balcony' if trained
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            region = image[y1:y2, x1:x2]

            # Apply grill lines (simple crossbars)
            for i in range(1, 4):
                cv2.line(image, (x1 + i*(x2 - x1)//4, y1), (x1 + i*(x2 - x1)//4, y2), (0, 255, 0), 2)
                cv2.line(image, (x1, y1 + i*(y2 - y1)//4), (x2, y1 + i*(y2 - y1)//4), (0, 255, 0), 2)

    processed_path = os.path.join(PROCESSED_FOLDER, f"processed_{os.path.basename(image_path)}")
    cv2.imwrite(processed_path, image)
    return processed_path

if __name__ == '__main__':
    app.run(debug=True)
