# 🤖 Robot Quiz Moderator

## Technology Acceptance in University Robot-Supported Quiz-Based Learning

A web-based robot quiz moderator designed to support university quiz-based learning through **voice input, robot-generated feedback, performance tracking, and analytics**.

The system allows students to answer quiz questions verbally using their microphone. The robot asks questions using text-to-speech, processes the student's spoken answer using browser-based speech recognition, evaluates the answer, and provides either **Verbal Only** or **Multimodal Feedback**.

The system also stores student performance data using SQLite and provides an interactive dashboard for analyzing quiz performance.

---

## 📌 Project Overview

The project focuses on studying technology acceptance and learning interaction with a robot-supported quiz environment.

The application provides two feedback modes:

- **Verbal Only Feedback**
- **Multimodal Feedback**

Students interact with the robot by listening to questions and answering them using their voice.

After each answer:

1. The spoken answer is converted into text.
2. The answer is evaluated against the correct answer.
3. The response is stored in the database.
4. The robot provides feedback.
5. The student can take as much time as needed before moving to the next question.
6. After completing the quiz, the overall performance is stored.
7. The collected data can be viewed through the performance dashboard.

---

## ✨ Features

### 🎙️ Voice-Based Quiz Interaction

Students can answer questions using their microphone instead of typing.

The application uses the browser's Speech Recognition API to convert spoken responses into text.

### 🔊 Robot Text-to-Speech

The robot reads quiz questions aloud using the browser's Text-to-Speech functionality.

It also speaks the feedback provided after each answer.

### 🤖 Robot Feedback

The robot provides feedback depending on the student's answer.

For example:

- Correct answer
- Incorrect answer
- Detected response
- Confidence-related feedback

The robot's visual indicator also changes according to the result.

### 🔄 Verbal and Multimodal Feedback

The student can select between:

**Verbal Only**

The robot provides simple verbal feedback.

**Multimodal**

The robot provides verbal feedback along with additional visual feedback such as changes in the robot indicator and response information.

### ⏭️ Student-Controlled Question Navigation

The previous version automatically moved to the next question after a fixed amount of time.

The new version does **not automatically skip questions**.

After the robot provides feedback, the student sees:

```text
Next Question →
