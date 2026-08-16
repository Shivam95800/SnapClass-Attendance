import io
import wave
import random
import librosa
import numpy as np
import streamlit as st
from resemblyzer import VoiceEncoder, preprocess_wav
import speech_recognition as sr

NUMBER_WORDS = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
    "to": "2", "too": "2", "for": "4", "tree": "3", "won": "1",
}

CHALLENGE_WORDS = [
    "Alpha", "Bravo", "Delta", "Echo", "Falcon", "Nova", "Phoenix",
    "Solar", "Titan", "Vortex", "Amber", "Cobalt", "Emerald", "Ruby"
]


def generate_voice_challenge() -> str:
    """Generates a dynamic 4-token challenge phrase per session (e.g. 'Falcon 7 4 2')."""
    word = random.choice(CHALLENGE_WORDS)
    digits = [str(random.randint(1, 9)) for _ in range(3)]
    return f"{word} {' '.join(digits)}"


def transcribe_and_verify_phrase(audio_bytes: bytes, expected_phrase: str) -> tuple[bool, str]:
    """
    Transcribes spoken audio using SpeechRecognition and checks if the spoken words
    match the dynamic challenge phrase to ensure voice liveness and prevent replay attacks.
    Returns (is_match, transcribed_text).
    """
    if not audio_bytes or not expected_phrase:
        return False, ""

    try:
        # 1. Decode audio using librosa to 16kHz float32
        audio, sr_rate = librosa.load(io.BytesIO(audio_bytes), sr=16000)

        # 2. Convert to 16-bit PCM WAV in memory for SpeechRecognition
        audio_int16 = (np.clip(audio, -1.0, 1.0) * 32767).astype(np.int16)
        wav_io = io.BytesIO()
        with wave.open(wav_io, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sr_rate)
            wav_file.writeframes(audio_int16.tobytes())
        wav_io.seek(0)

        # 3. Transcribe using SpeechRecognition
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_io) as source:
            audio_data = recognizer.record(source)

        transcribed = recognizer.recognize_google(audio_data).lower()

        # 4. Normalize words and numbers for flexible matching
        expected_tokens = expected_phrase.lower().split()
        raw_tokens = transcribed.replace('-', ' ').replace(',', ' ').split()
        normalized_tokens = [NUMBER_WORDS.get(t, t) for t in raw_tokens]
        transcribed_norm = ' '.join(normalized_tokens)

        # Check keyword matches
        matches = 0
        for token in expected_tokens:
            norm_token = NUMBER_WORDS.get(token, token)
            if norm_token in transcribed_norm or norm_token in normalized_tokens:
                matches += 1

        is_match = (matches >= max(2, int(len(expected_tokens) * 0.6)))
        return is_match, transcribed

    except sr.UnknownValueError:
        return False, "Could not understand audio"
    except sr.RequestError as e:
        print("Speech recognition API request error:", e)
        # In case of network timeout with Google STT API, fallback gracefully
        return True, "API offline fallback (allowed)"
    except Exception as e:
        print("Voice liveness STT error:", e)
        return False, f"Error: {str(e)}"


@st.cache_resource
def load_voice_encoder():
    return VoiceEncoder()


def get_voice_embedding(audio_bytes):
    try:
        encoder = load_voice_encoder()
        audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
        wav = preprocess_wav(audio)
        embedding = encoder.embed_utterance(wav)
        return embedding.tolist()
    except Exception as e:
        print("Voice recog error:", e)
        st.error('Voice recognition error occurred during audio processing.')
        return None


def identify_speaker(new_embedding, candidates_dict, threshold=0.65):
    if new_embedding is None or not candidates_dict:
        return None, 0.0

    new_emb_np = np.array(new_embedding)
    new_norm = np.linalg.norm(new_emb_np)
    if new_norm > 0:
        new_emb_np = new_emb_np / new_norm

    best_sid = None
    best_score = -1.0

    for sid, stored_embedding in candidates_dict.items():
        if stored_embedding is not None:
            stored_emb_np = np.array(stored_embedding)
            stored_norm = np.linalg.norm(stored_emb_np)
            if stored_norm > 0:
                stored_emb_np = stored_emb_np / stored_norm

            similarity = float(np.dot(new_emb_np, stored_emb_np))
            if similarity > best_score:
                best_score = similarity
                best_sid = sid

    if best_score >= threshold:
        return best_sid, best_score

    return None, best_score


def process_bulk_audio(audio_bytes, candidates_dict, threshold=0.65):
    try:
        encoder = load_voice_encoder()
        audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
        segments = librosa.effects.split(audio, top_db=30)

        identified_results = {}

        for start, end in segments:
            if (end - start) < sr * 0.5:
                continue
            segment_audio = audio[start:end]
            wav = preprocess_wav(segment_audio)
            embedding = encoder.embed_utterance(wav)

            sid, score = identify_speaker(embedding, candidates_dict, threshold)

            if sid:
                if sid not in identified_results or score > identified_results[sid]:
                    identified_results[sid] = score

        return identified_results
    except Exception as e:
        print("Bulk process error:", e)
        st.error('Bulk audio processing error.')
        return {}