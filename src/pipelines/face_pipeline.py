

import dlib
import numpy as np
import face_recognition_models
from sklearn.svm import SVC
import streamlit as st

from src.database.db import get_all_students


@st.cache_resource
def load_dlib_models():
    detector = dlib.get_frontal_face_detector() 


    sp = dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )

    facerec = dlib.face_recognition_model_v1(
        face_recognition_models.face_recognition_model_location()
    )

    return detector, sp, facerec

def compute_ear_from_landmarks(shape):
    """Compute Eye Aspect Ratio (EAR) from dlib 68-point shape."""
    def _eye_ear(indices):
        pts = np.array([[shape.part(i).x, shape.part(i).y] for i in indices], dtype=float)
        # Vertical eye distances
        v1 = np.linalg.norm(pts[1] - pts[5])
        v2 = np.linalg.norm(pts[2] - pts[4])
        # Horizontal eye distance
        h = np.linalg.norm(pts[0] - pts[3])
        if h == 0:
            return 0.0
        return (v1 + v2) / (2.0 * h)

    left_ear = _eye_ear([36, 37, 38, 39, 40, 41])
    right_ear = _eye_ear([42, 43, 44, 45, 46, 47])
    return (left_ear + right_ear) / 2.0


def check_liveness(frames: list) -> bool:
    """
    Evaluates a sequence of captured frames (RGB numpy arrays or PIL Images)
    to confirm liveness by detecting natural eye blink dynamics (Anti-Spoofing).
    Returns True if natural blinking/eye motion is confirmed, False for static photos or spoofs.
    """
    if not frames or len(frames) < 2:
        return False

    detector, sp, _ = load_dlib_models()
    ears = []

    for frame in frames:
        if hasattr(frame, 'convert'):
            frame_np = np.array(frame.convert('RGB'))
        elif isinstance(frame, np.ndarray):
            frame_np = frame
        else:
            continue

        faces = detector(frame_np, 0)
        if not faces:
            faces = detector(frame_np, 1)

        if faces:
            face = faces[0]
            shape = sp(frame_np, face)
            ear_val = compute_ear_from_landmarks(shape)
            ears.append(ear_val)

    if len(ears) < 2:
        return False

    min_ear = min(ears)
    max_ear = max(ears)
    ear_range = max_ear - min_ear

    # Liveness check: requires eye closure/open transition or dynamic EAR range
    is_live = (min_ear <= 0.22 and max_ear >= 0.25) or (ear_range >= 0.065)
    return is_live


def get_face_embeddings(image_np):
    detector, sp, facerec = load_dlib_models()
    faces = detector(image_np, 1)

    encodings = []

    for face in faces:
        shape = sp(image_np, face)
        face_descriptor = facerec.compute_face_descriptor(image_np, shape, 1)  # 128 embedding

        encodings.append(np.array(face_descriptor))
    return encodings

@st.cache_resource
def get_trained_model():
    X = []
    y = []


    student_db = get_all_students()

    if not student_db:
        return None
    
    for student in student_db:
        embedding = student.get('face_embedding')
        if embedding:
            X.append(np.array(embedding))
            y.append(student.get('student_id'))

    if len(X) ==0:
        return 0
    
    clf = SVC(kernel='linear', probability=True, class_weight='balanced')

    try:
        clf.fit(X, y)
    except ValueError:
        pass

    return {'clf': clf, 'X':X, "y":y}


def train_classifier():
    st.cache_resource.clear()
    model_data = get_trained_model()
    return bool(model_data)

def predict_attendance(class_image_np):
    encodings = get_face_embeddings(class_image_np)

    detected_student = {}


    model_data = get_trained_model()

    if not model_data:
        return detected_student, [], len(encodings)
    
    clf = model_data['clf']
    X_train = model_data['X']
    y_train = model_data['y']

    all_students = sorted(list(set(y_train)))

    for encoding in encodings:
        if len(all_students)>= 2:
            predicted_id= int(clf.predict([encoding])[0])
        else:
            predicted_id = int(all_students[0])

        student_embedding = X_train[y_train.index(predicted_id)]

        best_match_score = np.linalg.norm(student_embedding - encoding)

        resemblance_threshold = 0.6

        if best_match_score <= resemblance_threshold:
            detected_student[predicted_id] = True
    return detected_student, all_students, len(encodings)

