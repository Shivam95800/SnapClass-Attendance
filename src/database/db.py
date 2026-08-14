import streamlit as st
import bcrypt
from firebase_admin import firestore as fs

from src.database.config import db, _init_error


# ─────────────────────────────────────────────
# Guard: stop app if Firebase not initialized
# ─────────────────────────────────────────────
def _check_db():
    if db is None:
        msg = _init_error or "Firebase not initialized. Check your credentials."
        st.error(f"🔴 Database error: {msg}")
        st.stop()


# ─────────────────────────────────────────────
# Auto-increment ID helper
# ─────────────────────────────────────────────
def _next_id(collection_name: str) -> int:
    """Atomically increment and return the next integer ID for a collection."""
    _check_db()
    counter_ref = db.collection("_meta").document("counters")
    field = f"{collection_name}_next"

    @fs.transactional
    def _txn(transaction):
        snapshot = counter_ref.get(transaction=transaction)
        current = 0
        if snapshot.exists:
            current = snapshot.to_dict().get(field, 0)
        next_val = current + 1
        transaction.set(counter_ref, {field: next_val}, merge=True)
        return next_val

    return _txn(db.transaction())


# ─────────────────────────────────────────────
# Password helpers
# ─────────────────────────────────────────────
def hash_pass(pwd: str) -> str:
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()


def check_pass(pwd: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(pwd.encode(), hashed.encode())
    except Exception:
        return False


# ─────────────────────────────────────────────
# Teachers
# ─────────────────────────────────────────────
def check_teacher_exists(username: str) -> bool:
    try:
        _check_db()
        docs = db.collection("teachers").where("username", "==", username).limit(1).stream()
        return any(True for _ in docs)
    except Exception as e:
        print("check_teacher_exists error:", e)
        return False


def create_teacher(username: str, password: str, name: str):
    _check_db()
    tid = _next_id("teachers")
    data = {
        "teacher_id": tid,
        "username": username,
        "password": hash_pass(password),
        "name": name,
        "created_at": fs.SERVER_TIMESTAMP,
    }
    db.collection("teachers").document(str(tid)).set(data)
    return [data]


def teacher_login(username: str, password: str):
    try:
        _check_db()
        docs = db.collection("teachers").where("username", "==", username).limit(1).stream()
        for doc in docs:
            teacher = doc.to_dict()
            if check_pass(password, teacher["password"]):
                return teacher
        return None
    except Exception as e:
        print("teacher_login error:", e)
        return None


# ─────────────────────────────────────────────
# Students
# ─────────────────────────────────────────────
def get_all_students():
    try:
        _check_db()
        docs = db.collection("students").stream()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        print("get_all_students error:", e)
        return []


def create_student(new_name: str, face_embedding=None, voice_embedding=None):
    try:
        _check_db()
        sid = _next_id("students")
        data = {
            "student_id": sid,
            "name": new_name,
            "face_embedding": face_embedding,
            "voice_embedding": voice_embedding,
            "created_at": fs.SERVER_TIMESTAMP,
        }
        db.collection("students").document(str(sid)).set(data)
        return [data]
    except Exception as e:
        print("create_student error:", e)
        return []


# ─────────────────────────────────────────────
# Subjects
# ─────────────────────────────────────────────
def create_subject(subject_code: str, name: str, section: str, teacher_id: int):
    _check_db()
    sub_id = _next_id("subjects")
    data = {
        "subject_id": sub_id,
        "subject_code": subject_code,
        "name": name,
        "section": section,
        "teacher_id": teacher_id,
        "created_at": fs.SERVER_TIMESTAMP,
    }
    db.collection("subjects").document(str(sub_id)).set(data)
    return [data]


def get_teacher_subjects(teacher_id: int):
    try:
        _check_db()
        docs = db.collection("subjects").where("teacher_id", "==", teacher_id).stream()
        subjects = []
        for doc in docs:
            sub = doc.to_dict()
            sub_id = sub["subject_id"]

            # Count enrolled students
            student_docs = db.collection("subject_students").where("subject_id", "==", sub_id).stream()
            sub["total_students"] = sum(1 for _ in student_docs)

            # Count unique class sessions
            log_docs = db.collection("attendance_logs").where("subject_id", "==", sub_id).stream()
            unique_sessions = set(lg.to_dict().get("timestamp", "") for lg in log_docs)
            sub["total_classes"] = len(unique_sessions)

            subjects.append(sub)
        return subjects
    except Exception as e:
        print("get_teacher_subjects error:", e)
        return []


def get_subject_by_code(subject_code: str):
    try:
        _check_db()
        docs = db.collection("subjects").where("subject_code", "==", subject_code).limit(1).stream()
        for doc in docs:
            return doc.to_dict()
        return None
    except Exception as e:
        print("get_subject_by_code error:", e)
        return None


# ─────────────────────────────────────────────
# Enrollment
# ─────────────────────────────────────────────
def check_student_enrolled(student_id: int, subject_id: int) -> bool:
    try:
        _check_db()
        existing = (
            db.collection("subject_students")
            .where("student_id", "==", student_id)
            .where("subject_id", "==", subject_id)
            .limit(1)
            .stream()
        )
        return any(True for _ in existing)
    except Exception as e:
        print("check_student_enrolled error:", e)
        return False


def enroll_student_to_subject(student_id: int, subject_id: int):
    try:
        _check_db()
        # Prevent duplicate enrollment
        existing = (
            db.collection("subject_students")
            .where("student_id", "==", student_id)
            .where("subject_id", "==", subject_id)
            .limit(1)
            .stream()
        )
        if any(True for _ in existing):
            return None

        enroll_id = _next_id("subject_students")
        data = {
            "id": enroll_id,
            "student_id": student_id,
            "subject_id": subject_id,
            "created_at": fs.SERVER_TIMESTAMP,
        }
        db.collection("subject_students").document(str(enroll_id)).set(data)
        return [data]
    except Exception as e:
        print("enroll_student_to_subject error:", e)
        return None


def unenroll_student_to_subject(student_id: int, subject_id: int):
    try:
        _check_db()
        docs = (
            db.collection("subject_students")
            .where("student_id", "==", student_id)
            .where("subject_id", "==", subject_id)
            .stream()
        )
        for doc in docs:
            doc.reference.delete()
        return True
    except Exception as e:
        print("unenroll_student_to_subject error:", e)
        return None


def get_student_subjects(student_id: int):
    try:
        _check_db()
        enrollments = db.collection("subject_students").where("student_id", "==", student_id).stream()
        result = []
        for enrollment in enrollments:
            enroll_data = enrollment.to_dict()
            sub_doc = db.collection("subjects").document(str(enroll_data["subject_id"])).get()
            if sub_doc.exists:
                result.append({"subjects": sub_doc.to_dict()})
        return result
    except Exception as e:
        print("get_student_subjects error:", e)
        return []


def get_enrolled_students_for_subject(subject_id: int):
    """Returns list of student dicts enrolled in a given subject."""
    try:
        _check_db()
        enrollments = db.collection("subject_students").where("subject_id", "==", subject_id).stream()
        result = []
        for enrollment in enrollments:
            sid = enrollment.to_dict().get("student_id")
            student_doc = db.collection("students").document(str(sid)).get()
            if student_doc.exists:
                result.append({"students": student_doc.to_dict()})
        return result
    except Exception as e:
        print("get_enrolled_students_for_subject error:", e)
        return []


# ─────────────────────────────────────────────
# Attendance
# ─────────────────────────────────────────────
def get_student_attendance(student_id: int):
    try:
        _check_db()
        logs = db.collection("attendance_logs").where("student_id", "==", student_id).stream()
        result = []
        for log in logs:
            log_data = log.to_dict()
            sub_doc = db.collection("subjects").document(str(log_data["subject_id"])).get()
            if sub_doc.exists:
                log_data["subjects"] = sub_doc.to_dict()
            result.append(log_data)
        return result
    except Exception as e:
        print("get_student_attendance error:", e)
        return []


def create_attendance(logs: list):
    try:
        _check_db()
        batch = db.batch()
        for log in logs:
            log_id = _next_id("attendance_logs")
            log["id"] = log_id
            log["created_at"] = fs.SERVER_TIMESTAMP
            ref = db.collection("attendance_logs").document(str(log_id))
            batch.set(ref, log)
        batch.commit()
        return logs
    except Exception as e:
        print("create_attendance error:", e)
        raise e


def get_attendance_for_teacher(teacher_id: int):
    try:
        _check_db()
        # Fetch all subjects for this teacher
        subject_docs = db.collection("subjects").where("teacher_id", "==", teacher_id).stream()
        subjects_map = {}
        for doc in subject_docs:
            sub = doc.to_dict()
            subjects_map[sub["subject_id"]] = sub

        if not subjects_map:
            return []

        # Fetch attendance logs for each subject
        result = []
        for sub_id, sub_data in subjects_map.items():
            logs = db.collection("attendance_logs").where("subject_id", "==", sub_id).stream()
            for log in logs:
                log_data = log.to_dict()
                log_data["subjects"] = sub_data
                result.append(log_data)
        return result
    except Exception as e:
        print("get_attendance_for_teacher error:", e)
        return []
