import os
import json
import random
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from google import genai
from google.genai import types


# ============================================================
# CONFIGURATION
# ============================================================

API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GOOGLE_API_KEY is not configured. "
        "Add it in Render → Environment Variables."
    )

client = genai.Client(api_key=API_KEY)

# Current stable Gemini model
MODEL = "gemini-3.5-flash"


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="MindMate AI",
    description="AI-powered Student Stress-Buster",
    version="1.0.0"
)


# ============================================================
# REQUEST MODELS
# ============================================================

class StartRequest(BaseModel):
    mood: str


class ActivityRequest(BaseModel):
    mood: str
    activity: str


class CheckinRequest(BaseModel):
    mood: str
    activity: str
    feeling: str


# ============================================================
# BASIC SAFETY CHECK
# ============================================================

RISK_WORDS = [
    "suicide",
    "kill myself",
    "end my life",
    "hurt myself",
    "self harm",
    "self-harm",
    "die",
    "want to die"
]


def contains_risk_language(text: str) -> bool:
    text = text.lower()

    return any(
        phrase in text
        for phrase in RISK_WORDS
    )


def safety_response():
    return {
        "title": "💙 You don't have to handle this alone",
        "message": (
            "I'm really sorry you're going through something this heavy. "
            "An AI cannot provide the kind of help you may need right now. "
            "Please reach out to someone you trust, such as a parent, "
            "friend, teacher, counselor, or another trusted person, "
            "and stay with someone if you can."
        ),
        "activities": [
            "💙 Talk to someone you trust",
            "📞 Contact a local emergency or crisis service",
            "🏫 Reach out to a teacher or college counselor",
            "🌿 Stay with someone rather than being alone"
        ]
    }


# ============================================================
# GEMINI HELPER
# ============================================================

def ask_gemini(prompt: str) -> str:

    try:

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=800
            )
        )

        if not response.text:
            raise ValueError("Gemini returned an empty response.")

        return response.text.strip()

    except Exception as e:

        print("Gemini error:", repr(e))

        raise HTTPException(
            status_code=500,
            detail="Unable to generate the activity right now. Please try again."
        )


# ============================================================
# HOME PAGE
# ============================================================

@app.get("/", response_class=HTMLResponse)
def home():

    return HTMLResponse("""
<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>MindMate AI</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: linear-gradient(
        135deg,
        #081b3a,
        #102f5c,
        #173f73
    );
    color: white;
    min-height: 100vh;
}

.container {
    max-width: 900px;
    margin: auto;
    padding: 30px 20px 60px;
}

.header {
    text-align: center;
    margin-bottom: 35px;
}

.logo {
    font-size: 55px;
}

h1 {
    margin: 5px 0;
    font-size: 38px;
}

.subtitle {
    color: #dce8ff;
    font-size: 17px;
}

.card {
    background: rgba(255,255,255,0.09);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 24px;
    padding: 30px;
    margin-bottom: 22px;
    backdrop-filter: blur(12px);
    box-shadow: 0 15px 40px rgba(0,0,0,0.25);
}

.section-title {
    font-size: 24px;
    margin-bottom: 20px;
}

.moods {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
}

.mood-btn {
    background: #ffffff;
    color: #10284d;
    border: none;
    padding: 18px 10px;
    border-radius: 16px;
    font-size: 16px;
    cursor: pointer;
    transition: 0.2s;
}

.mood-btn:hover {
    transform: translateY(-3px);
    background: #ffd84d;
}

.mood-btn.selected {
    background: #ffd84d;
    box-shadow: 0 0 0 3px rgba(255,216,77,0.3);
}

.primary-btn {
    width: 100%;
    padding: 17px;
    margin-top: 22px;
    border: none;
    border-radius: 14px;
    background: #ffd84d;
    color: #10284d;
    font-weight: bold;
    font-size: 18px;
    cursor: pointer;
}

.primary-btn:hover {
    background: #ffe37a;
}

.activities {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
}

.activity-btn {
    padding: 22px 12px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.2);
    background: rgba(255,255,255,0.1);
    color: white;
    cursor: pointer;
    font-size: 17px;
}

.activity-btn:hover {
    background: rgba(255,216,77,0.2);
    transform: translateY(-3px);
}

.output {
    background: white;
    color: #172b4d;
    border-radius: 18px;
    padding: 25px;
    line-height: 1.7;
    white-space: pre-wrap;
}

.checkins {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
}

.checkin-btn {
    padding: 18px;
    border: none;
    border-radius: 15px;
    cursor: pointer;
    font-size: 16px;
    background: #fff;
    color: #10284d;
}

.checkin-btn:hover {
    background: #ffd84d;
}

.hidden {
    display: none;
}

.loading {
    text-align: center;
    padding: 20px;
    font-size: 18px;
}

.footer {
    text-align: center;
    color: #b9c8df;
    margin-top: 30px;
    font-size: 14px;
}

@media(max-width:700px) {

    .moods {
        grid-template-columns: repeat(2, 1fr);
    }

    .activities {
        grid-template-columns: 1fr;
    }

    .checkins {
        grid-template-columns: 1fr;
    }

    h1 {
        font-size: 30px;
    }

}

</style>

</head>


<body>

<div class="container">

    <div class="header">

        <div class="logo">🌱</div>

        <h1>MindMate AI</h1>

        <div class="subtitle">
            Your little AI-powered stress-buster 💙
        </div>

        <div class="subtitle">
            Take a 2-minute break. You deserve it.
        </div>

    </div>


    <!-- STEP 1 -->

    <div class="card" id="moodCard">

        <div class="section-title">
            😊 How are you feeling right now?
        </div>

        <div class="moods">

            <button class="mood-btn" onclick="selectMood('Stressed', this)">
                😰 Stressed
            </button>

            <button class="mood-btn" onclick="selectMood('Sad', this)">
                😔 Sad
            </button>

            <button class="mood-btn" onclick="selectMood('Tired', this)">
                😴 Tired
            </button>

            <button class="mood-btn" onclick="selectMood('Angry', this)">
                😡 Angry
            </button>

            <button class="mood-btn" onclick="selectMood('Worried', this)">
                😟 Worried
            </button>

            <button class="mood-btn" onclick="selectMood('Overwhelmed', this)">
                😵 Overwhelmed
            </button>

            <button class="mood-btn" onclick="selectMood('Okay', this)">
                🙂 Okay
            </button>

            <button class="mood-btn" onclick="selectMood('Excited', this)">
                🤩 Excited
            </button>

        </div>

        <button
            class="primary-btn"
            onclick="understandMood()">

            💙 Help Me Feel Better

        </button>

    </div>


    <!-- STEP 2 -->

    <div class="card hidden" id="activityCard">

        <div class="section-title">
            🤖 What would you like to do?
        </div>

        <div id="moodMessage" class="output"></div>

        <br>

        <div class="activities">

            <button
                class="activity-btn"
                onclick="startActivity('Calm Me')">

                🧘<br>
                <b>Calm Me</b>
                <br>
                <small>Relax your mind</small>

            </button>


            <button
                class="activity-btn"
                onclick="startActivity('Distract Me')">

                🎮<br>
                <b>Distract Me</b>
                <br>
                <small>Give me something fun</small>

            </button>


            <button
                class="activity-btn"
                onclick="startActivity('Cheer Me Up')">

                📖<br>
                <b>Cheer Me Up</b>
                <br>
                <small>Make me smile</small>

            </button>

        </div>

    </div>


    <!-- STEP 3 -->

    <div class="card hidden" id="activityResultCard">

        <div class="section-title" id="activityTitle">
            ✨ Your activity
        </div>

        <div id="activityResult" class="output"></div>

        <button
            class="primary-btn"
            onclick="showCheckin()">

            🌱 I'm Done — Check In

        </button>

    </div>


    <!-- STEP 4 -->

    <div class="card hidden" id="checkinCard">

        <div class="section-title">

            💙 How do you feel now?

        </div>

        <div class="checkins">

            <button
                class="checkin-btn"
                onclick="checkin('Better')">

                😊 Much Better

            </button>

            <button
                class="checkin-btn"
                onclick="checkin('A Little Better')">

                🙂 A Little Better

            </button>

            <button
                class="checkin-btn"
                onclick="checkin('Same')">

                😐 Same

            </button>

        </div>

    </div>


    <!-- STEP 5 -->

    <div class="card hidden" id="finalCard">

        <div class="section-title">
            🌈 Your MindMate Moment
        </div>

        <div id="finalResult" class="output"></div>

        <button
            class="primary-btn"
            onclick="restart()">

            🔄 Start Another Break

        </button>

    </div>


    <div class="footer">

        🌱 MindMate AI • A small break can make a big difference.

    </div>

</div>


<script>

let selectedMood = "";
let selectedActivity = "";
let lastActivity = "";


function selectMood(mood, button) {

    selectedMood = mood;

    document
        .querySelectorAll(".mood-btn")
        .forEach(btn => btn.classList.remove("selected"));

    button.classList.add("selected");
}


async function understandMood() {

    if (!selectedMood) {

        alert("Please choose how you are feeling first 💙");

        return;
    }

    document.getElementById("activityCard")
        .classList.remove("hidden");

    document.getElementById("moodMessage")
        .innerText = "🤖 MindMate is thinking...";

    try {

        const response = await fetch("/api/start", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                mood: selectedMood
            })

        });

        const data = await response.json();

        if (!response.ok) {

            throw new Error(data.detail || "Something went wrong");

        }

        document.getElementById("moodMessage")
            .innerText =
                data.message;

    } catch(error) {

        document.getElementById("moodMessage")
            .innerText =
                "💙 Let's take a small break together.";

    }

    document
        .getElementById("activityCard")
        .scrollIntoView({
            behavior: "smooth"
        });
}


async function startActivity(activity) {

    selectedActivity = activity;

    document
        .getElementById("activityResultCard")
        .classList.remove("hidden");

    document
        .getElementById("activityResult")
        .innerText = "✨ Creating your activity...";

    document
        .getElementById("activityTitle")
        .innerText =
            activity + " ✨";

    try {

        const response = await fetch("/api/activity", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                mood: selectedMood,
                activity: activity

            })

        });

        const data = await response.json();

        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Unable to create activity"
            );

        }

        lastActivity = data.activity;

        document
            .getElementById("activityResult")
            .innerText =
                data.activity;

    } catch(error) {

        document
            .getElementById("activityResult")
            .innerText =
                "💙 Something went wrong. Please try again.";

    }

    document
        .getElementById("activityResultCard")
        .scrollIntoView({
            behavior: "smooth"
        });
}


function showCheckin() {

    document
        .getElementById("checkinCard")
        .classList.remove("hidden");

    document
        .getElementById("checkinCard")
        .scrollIntoView({
            behavior: "smooth"
        });
}


async function checkin(feeling) {

    document
        .getElementById("finalCard")
        .classList.remove("hidden");

    document
        .getElementById("finalResult")
        .innerText =
            "💙 MindMate is preparing your next step...";

    try {

        const response = await fetch("/api/checkin", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                mood: selectedMood,
                activity: selectedActivity,
                feeling: feeling

            })

        });

        const data = await response.json();

        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Something went wrong"
            );

        }

        document
            .getElementById("finalResult")
            .innerText =
                data.message;

    } catch(error) {

        document
            .getElementById("finalResult")
            .innerText =
                "🌱 You did something good for yourself today. Keep going! 💙";

    }

    document
        .getElementById("finalCard")
        .scrollIntoView({
            behavior: "smooth"
        });
}


function restart() {

    selectedMood = "";
    selectedActivity = "";
    lastActivity = "";

    document
        .querySelectorAll(".mood-btn")
        .forEach(btn =>
            btn.classList.remove("selected")
        );

    document
        .getElementById("activityCard")
        .classList.add("hidden");

    document
        .getElementById("activityResultCard")
        .classList.add("hidden");

    document
        .getElementById("checkinCard")
        .classList.add("hidden");

    document
        .getElementById("finalCard")
        .classList.add("hidden");

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}

</script>

</body>

</html>
""")


# ============================================================
# STEP 1 → UNDERSTAND MOOD
# ============================================================

@app.post("/api/start")
def start(request: StartRequest):

    mood = request.mood.strip()

    if contains_risk_language(mood):
        return safety_response()

    prompt = f"""
You are MindMate AI, a friendly student stress-buster.

A student says they feel: {mood}

Respond in a warm and friendly way.

Rules:
- Use simple English.
- Use emojis.
- Do not diagnose the student.
- Do not give medical advice.
- Keep the response under 70 words.
- Acknowledge their feeling.
- Tell them they don't need to solve everything immediately.
- Encourage a short break.
- Do not ask many questions.

Return only the response.
"""

    message = ask_gemini(prompt)

    return {
        "mood": mood,
        "message": message
    }


# ============================================================
# STEP 2 → CREATE ACTIVITY
# ============================================================

@app.post("/api/activity")
def create_activity(request: ActivityRequest):

    mood = request.mood.strip()
    activity = request.activity.strip()

    if contains_risk_language(mood):
        return safety_response()

    prompts = {

        "Calm Me": """
Create a very short calming activity for a college student.

Include:
🌬️ breathing or grounding
⏱️ approximately 1–2 minutes
🌱 simple instructions
💙 one encouraging sentence

Do not make it complicated.
""",

        "Distract Me": """
Create a tiny fun activity for a college student.

Choose ONE:
- funny challenge
- simple puzzle
- imagination game
- silly question
- mini guessing game

Make it playful.
Use emojis.
Keep it under 150 words.
Do not make it academic.
""",

        "Cheer Me Up": """
Create a short cheerful mini-story for a college student.

The story should:
- be funny, magical or heartwarming
- use simple English
- have a happy ending
- use emojis
- be around 150 words
- make the student smile

Do not make it about studying.
"""
    }

    selected_prompt = prompts.get(
        activity,
        prompts["Distract Me"]
    )

    prompt = f"""
You are MindMate AI.

Student mood:
{mood}

Chosen activity:
{activity}

{selected_prompt}

The purpose is to provide a small positive break,
not to solve the student's life problems.

Return only the activity.
"""

    result = ask_gemini(prompt)

    return {
        "activity": result
    }


# ============================================================
# STEP 3 → CHECK-IN
# ============================================================

@app.post("/api/checkin")
def checkin(request: CheckinRequest):

    mood = request.mood.strip()
    activity = request.activity.strip()
    feeling = request.feeling.strip()

    prompt = f"""
You are MindMate AI, a supportive student stress-buster.

Initial mood:
{mood}

Activity:
{activity}

Student says they now feel:
{feeling}

Create the next response.

If the student feels "Better" or "A Little Better":
- celebrate gently
- give a positive message
- remind them that small breaks matter
- end warmly

If the student feels "Same":
- do NOT say they failed
- acknowledge that one activity may not be enough
- suggest another tiny activity
- give 2 or 3 choices

Use simple English.
Use emojis.
Keep it under 120 words.

Do not diagnose.
Do not give medical advice.

Return only the response.
"""

    result = ask_gemini(prompt)

    return {
        "message": result
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "application": "MindMate AI",
        "model": MODEL
    }
