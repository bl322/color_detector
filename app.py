import cv2
import numpy as np
from scipy.io import wavfile
import sounddevice as sd
import soundfile as sf
import playsound
import os
import pygame
from flask import Flask, render_template, Response, request

app = Flask(__name__)
app.debug = False

@app.route('/')
def index():
    """Render the index page."""
    return render_template('index.html')


def detect_color(frame):
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    height, width, _ = frame.shape

    cx = int(width / 2)
    cy = int(height / 2)

    # Pick pixel value
    pixel_center = hsv_frame[cy, cx]
    hue_value = pixel_center[0]

    color = "Undefined"
    sound_file = "./sound/"
    if hue_value < 5:
        color = "RED"
        sound_file = sound_file + "red.wav"
    elif hue_value < 22:
        color = "ORANGE"
        sound_file = sound_file + "orange.wav"
    elif hue_value < 33:
        color = "YELLOW"
        sound_file = sound_file + "yellow.wav"
    elif hue_value < 78:
        color = "GREEN"
        sound_file = sound_file + "green.wav"
    elif hue_value < 131:
        color = "BLUE"
        sound_file = sound_file + "blue.wav"
    elif hue_value < 170:
        color = "VIOLET"
        sound_file = sound_file + "violet.wav"
    else:
        color = "RED"
        sound_file = sound_file + "red.wav"

    playsound.playsound(sound=sound_file)
    return color


def gen_frames():
    """Generate frames from the user's camera."""
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break
        color = detect_color(frame)
        if color is not None:
            (x, y) = (color[0], color[1])
            cv2.putText(
                frame, f"Rainbow color: {color}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.rectangle(frame, (x - 10, y - 10),
                          (x + 10, y + 10), (0, 0, 255), 2)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Stream the camera preview with rainbow color detection."""
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/detect_color', methods=['POST'])
def detect_color_api():
    """Detect the rainbow color in a given image."""
    file = request.files['image']
    img = cv2.imdecode(np.fromstring(file.read(), np.uint8), cv2.IMREAD_COLOR)
    color = detect_color(img)
    if color is not None:
        return f"Rainbow color: {color}", 200
    else:
        return "Rainbow color not found", 404


