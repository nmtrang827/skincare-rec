from ultralytics import YOLO
import os

# Load model once when the module is imported
# so it doesn't reload on every request
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model', 'best.pt')
model = YOLO(MODEL_PATH)

def count_lesions(image_path, conf=0.15):
    result = model.predict(
        source=image_path,
        imgsz=640,
        conf=conf,
        save=False,
        verbose=False
    )
    return len(result[0].boxes)

def get_severity(count):
    if count == 0:
        return 0
    score = (count / 30) * 9 + 1
    return min(10, round(score))

def analyze_image(image_path):
    count = count_lesions(image_path)
    score = get_severity(count)
    return {
        'lesion_count': count,
        'acne_severity': score
    }