from flask import Flask, render_template, request, jsonify
import sqlite3
import random
from datetime import datetime

app = Flask(__name__)

DATABASE = "quiz_performance.db"

QUESTIONS = [
    {
        "id": 0,
        "q": "What does 'IoT' stand for?",
        "a": "Internet of Things"
    },
    {
        "id": 1,
        "q": "Which component is known as the 'brain' of the computer?",
        "a": "CPU"
    },
    {
        "id": 2,
        "q": "Is a Social Robot a type of hardware?",
        "a": "Yes"
    },
    {
        "id": 3,
        "q": "What is the acronym for Acoustic Emotion Recognition?",
        "a": "AER"
    },
    {
        "id": 4,
        "q": "Does multimodal feedback use more than one sense?",
        "a": "Yes"
    }
]


# ---------------------------------------------------------
# DATABASE
# ---------------------------------------------------------

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS quiz_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT,
            score INTEGER DEFAULT 0,
            total_questions INTEGER DEFAULT 5,
            modality TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS answer_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            student_answer TEXT NOT NULL,
            is_correct INTEGER NOT NULL,
            modality TEXT NOT NULL,
            emotion TEXT,
            timestamp TEXT NOT NULL,
            FOREIGN KEY(session_id) REFERENCES quiz_sessions(id)
        )
    """)

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# MAIN PAGE
# ---------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')


# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


# ---------------------------------------------------------
# START QUIZ SESSION
# ---------------------------------------------------------

@app.route('/start_session', methods=['POST'])
def start_session():

    data = request.json

    student_name = data.get('student_name', '').strip()

    if not student_name:
        return jsonify({
            "error": "Student name is required"
        }), 400

    modality = data.get('modality', 'multimodal')

    conn = get_db_connection()

    cursor = conn.execute("""
        INSERT INTO quiz_sessions
        (student_name, start_time, total_questions, modality)
        VALUES (?, ?, ?, ?)
    """, (
        student_name,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        len(QUESTIONS),
        modality
    ))

    session_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return jsonify({
        "session_id": session_id,
        "student_name": student_name
    })


# ---------------------------------------------------------
# GET QUESTION
# ---------------------------------------------------------

@app.route('/get_question/<int:q_id>')
def get_question(q_id):

    if q_id < len(QUESTIONS):
        return jsonify(QUESTIONS[q_id])

    return jsonify({
        "end": True
    })


# ---------------------------------------------------------
# VERIFY ANSWER
# ---------------------------------------------------------

@app.route('/verify_voice_answer', methods=['POST'])
def verify_voice_answer():

    data = request.json

    q_id = data.get('q_id')
    user_ans = data.get('answer', '').strip().lower()

    session_id = data.get('session_id')
    modality = data.get('modality', 'multimodal')

    if q_id is None or q_id >= len(QUESTIONS):
        return jsonify({
            "error": "Invalid question ID"
        }), 400

    if not session_id:
        return jsonify({
            "error": "Session ID is missing"
        }), 400

    # Clean answer
    user_ans = (
        user_ans
        .replace('.', '')
        .replace('?', '')
        .strip()
    )

    correct_ans = QUESTIONS[q_id]['a'].lower()

    # Simple answer checking
    is_correct = correct_ans in user_ans

    emotion = random.choice([
        "confident",
        "hesitant"
    ])

    # -----------------------------------------------------
    # ROBOT RESPONSE
    # -----------------------------------------------------

    if modality == "multimodal":

        if is_correct:

            msg = (
                f"Exactly! I heard you say '{user_ans}'. "
                f"You sound {emotion}."
            )

            color = "#2ecc71"

        else:

            msg = (
                f"I think I heard '{user_ans}', but the "
                f"correct answer is {QUESTIONS[q_id]['a']}."
            )

            color = "#e74c3c"

    else:

        if is_correct:

            msg = "Correct."

        else:

            msg = (
                f"Incorrect. The answer is "
                f"{QUESTIONS[q_id]['a']}."
            )

        color = "#3498db"

    # -----------------------------------------------------
    # STORE ANSWER
    # -----------------------------------------------------

    conn = get_db_connection()

    conn.execute("""
        INSERT INTO answer_records
        (
            session_id,
            question_id,
            question,
            correct_answer,
            student_answer,
            is_correct,
            modality,
            emotion,
            timestamp
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session_id,
        q_id,
        QUESTIONS[q_id]['q'],
        QUESTIONS[q_id]['a'],
        user_ans,
        int(is_correct),
        modality,
        emotion,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "correct": is_correct,
        "speech": msg,
        "color": color,
        "emotion_detected": emotion,
        "detected_text": user_ans
    })


# ---------------------------------------------------------
# COMPLETE SESSION
# ---------------------------------------------------------

@app.route('/complete_session', methods=['POST'])
def complete_session():

    data = request.json

    session_id = data.get('session_id')

    if not session_id:
        return jsonify({
            "error": "Session ID missing"
        }), 400

    conn = get_db_connection()

    cursor = conn.execute("""
        SELECT COUNT(*) AS score
        FROM answer_records
        WHERE session_id = ?
        AND is_correct = 1
    """, (session_id,))

    score = cursor.fetchone()['score']

    conn.execute("""
        UPDATE quiz_sessions
        SET score = ?,
            end_time = ?
        WHERE id = ?
    """, (
        score,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        session_id
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "score": score,
        "total": len(QUESTIONS)
    })


# ---------------------------------------------------------
# DASHBOARD DATA
# ---------------------------------------------------------

@app.route('/api/dashboard')
def dashboard_data():

    conn = get_db_connection()

    # Overall statistics
    overall = conn.execute("""
        SELECT
            COUNT(*) AS total_answers,
            SUM(is_correct) AS correct_answers,
            COUNT(DISTINCT session_id) AS total_sessions
        FROM answer_records
    """).fetchone()

    # Recent sessions
    sessions = conn.execute("""
        SELECT
            id,
            student_name,
            start_time,
            end_time,
            score,
            total_questions,
            modality
        FROM quiz_sessions
        ORDER BY id DESC
        LIMIT 20
    """).fetchall()

    # Question-wise performance
    question_stats = conn.execute("""
        SELECT
            question_id,
            question,
            COUNT(*) AS attempts,
            SUM(is_correct) AS correct
        FROM answer_records
        GROUP BY question_id
        ORDER BY question_id
    """).fetchall()

    # Modality statistics
    modality_stats = conn.execute("""
        SELECT
            modality,
            COUNT(*) AS attempts,
            SUM(is_correct) AS correct
        FROM answer_records
        GROUP BY modality
    """).fetchall()

    # Emotion statistics
    emotion_stats = conn.execute("""
        SELECT
            emotion,
            COUNT(*) AS count
        FROM answer_records
        GROUP BY emotion
    """).fetchall()

    conn.close()

    total_answers = overall['total_answers'] or 0
    correct_answers = overall['correct_answers'] or 0

    accuracy = 0

    if total_answers > 0:
        accuracy = round(
            (correct_answers / total_answers) * 100,
            2
        )

    return jsonify({

        "overall": {
            "total_answers": total_answers,
            "correct_answers": correct_answers,
            "incorrect_answers": total_answers - correct_answers,
            "accuracy": accuracy,
            "total_sessions": overall['total_sessions'] or 0
        },

        "sessions": [
            dict(row)
            for row in sessions
        ],

        "question_stats": [
            dict(row)
            for row in question_stats
        ],

        "modality_stats": [
            dict(row)
            for row in modality_stats
        ],

        "emotion_stats": [
            dict(row)
            for row in emotion_stats
        ]
    })


# ---------------------------------------------------------
# RUN
# ---------------------------------------------------------

if __name__ == '__main__':

    init_db()

    app.run(
        debug=True,
        threaded=True
    )