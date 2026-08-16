

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

def predict_attendance(class_image_np, threshold=0.52):
    """
    Detects faces in class_image_np, extracts 128D descriptors, and matches each face
    against registered students using Euclidean distance.
    Returns (detected_students_dict, all_student_ids, num_detected_faces).
    """
    encodings = get_face_embeddings(class_image_np)
    detected_students = {}

    student_db = get_all_students()
    if not student_db:
        return detected_students, [], len(encodings)

    valid_students = []
    for s in student_db:
        emb = s.get('face_embedding')
        if emb:
            valid_students.append({
                'student_id': s['student_id'],
                'name': s.get('name', ''),
                'embedding': np.array(emb, dtype=float)
            })

    all_ids = [s['student_id'] for s in valid_students]
    if not valid_students:
        return detected_students, [], len(encodings)

    for encoding in encodings:
        enc_np = np.array(encoding, dtype=float)

        best_sid = None
        min_distance = float('inf')

        for s in valid_students:
            dist = float(np.linalg.norm(s['embedding'] - enc_np))
            if dist < min_distance:
                min_distance = dist
                best_sid = s['student_id']

        # Match only if within strict resemblance threshold (prevents misidentification)
        if best_sid is not None and min_distance <= threshold:
            detected_students[int(best_sid)] = True

    return detected_students, all_ids, len(encodings)


def train_classifier():
    """Invalidates cached resources to ensure fresh student data is loaded."""
    st.cache_resource.clear()
    return True


