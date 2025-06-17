from flask import Flask, request, jsonify, send_file
import os
import cv2
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return "✅ Grill API is running!"

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        filename = f"{uuid.uuid4().hex}_{file.filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Process the image
        processed_path = process_image(filepath)

        return jsonify({
            'message': 'Grill design applied successfully',
            'processed_image_url': f"/processed/{os.path.basename(processed_path)}"
        })

    # GET: show upload form
    return '''
        <h2>Upload Grill Image</h2>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="file" required>
            <input type="submit" value="Upload">
        </form>
    '''

@app.route('/processed/<filename>')
def serve_processed_image(filename):
    path = os.path.join(PROCESSED_FOLDER, filename)
    return send_file(path, mimetype='image/jpeg')

def process_image(filepath):
    image = cv2.imread(filepath)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)

    # Find contours (simulate window/door detection)
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, 0.02*cv2.arcLength(cnt, True), True)
        if len(approx) == 4 and cv2.contourArea(cnt) > 5000:
            x, y, w, h = cv2.boundingRect(cnt)

            # Draw simulated grill (vertical + horizontal lines)
            for i in range(1, 4):
                cv2.line(image, (x + i*w//4, y), (x + i*w//4, y + h), (0, 255, 0), 2)
                cv2.line(image, (x, y + i*h//4), (x + w, y + i*h//4), (0, 255, 0), 2)

    # Save processed image
    processed_path = os.path.join(PROCESSED_FOLDER, f"processed_{os.path.basename(filepath)}")
    cv2.imwrite(processed_path, image)
    return processed_path

if __name__ == '__main__':
    app.run()
