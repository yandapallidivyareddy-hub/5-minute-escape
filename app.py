import os
import random
import html
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from google import genai


# ============================================================
# CONFIGURATION
# ============================================================

app = FastAPI(title="MindMate AI")

API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY or GOOGLE_API_KEY is not configured."
    )

client = genai.Client(api_key=API_KEY)

# Use a currently supported Gemini model.
MODEL_NAME = "gemini-2.5-flash"


# ============================================================
# SESSION DATA
# ============================================================

# Used activities are stored per browser session.
# The frontend sends the IDs already used.
#
# This prevents immediate repetition without needing a database.


# ============================================================
# ACTIVITY LIBRARY
# ============================================================

ACTIVITIES = {

    "calm": [

        {
            "id": "breathing_4",
            "title": "🌬️ 60-Second Breathing",
            "description": "Let's slow everything down for one minute.",
            "type": "breathing",
            "steps": [
                "🌬️ Breathe in slowly",
                "⏸️ Hold for a moment",
                "🍃 Breathe out slowly",
                "💙 Repeat 4 times"
            ],
            "button": "Start Breathing"
        },

        {
            "id": "grounding_54321",
            "title": "🌎 5-4-3-2-1 Grounding",
            "description": "Let's bring your attention back to the present.",
            "type": "grounding",
            "steps": [
                "👀 Notice 5 things you can see",
                "👂 Notice 4 things you can hear",
                "✋ Notice 3 things you can touch",
                "👃 Notice 2 things you can smell",
                "💭 Notice 1 thing you feel"
            ],
            "button": "Start Grounding"
        },

        {
            "id": "body_reset",
            "title": "🧘 Tiny Body Reset",
            "description": "Give your body a quick break.",
            "type": "steps",
            "steps": [
                "🙆 Stretch your arms",
                "🤲 Relax your hands",
                "😌 Drop your shoulders",
                "🙂 Unclench your jaw",
                "🌬️ Take one slow breath"
            ],
            "button": "Begin Reset"
        },

        {
            "id": "mind_cloud",
            "title": "☁️ Let the Thought Float Away",
            "description": "Imagine placing your stressful thought on a cloud.",
            "type": "steps",
            "steps": [
                "💭 Think of one thing bothering you",
                "☁️ Imagine putting that thought on a cloud",
                "🌬️ Watch the cloud slowly move away",
                "💙 Remind yourself: this moment will pass"
            ],
            "button": "Try It"
        },

        {
            "id": "five_breaths",
            "title": "🌿 Five Peaceful Breaths",
            "description": "Nothing to solve. Just five slow breaths.",
            "type": "counter",
            "count": 5,
            "button": "Take Breath"
        },

        {
            "id": "safe_place",
            "title": "🏡 Your Happy Place",
            "description": "Imagine a place where you feel completely comfortable.",
            "type": "steps",
            "steps": [
                "🌅 Picture the place",
                "👀 Notice its colors",
                "👂 Imagine its sounds",
                "🌸 Imagine its smell",
                "💙 Stay there for a few seconds"
            ],
            "button": "Enter My Happy Place"
        }
    ],


    "distract": [

        {
            "id": "emoji_guess",
            "title": "🎬 Guess the Movie",
            "description": "Can you guess the movie from the emojis?",
            "type": "quiz",
            "question": "🦁👑",
            "answers": [
                "The Lion King",
                "Frozen",
                "Toy Story",
                "Aladdin"
            ],
            "correct": 0,
            "button": "Choose Answer"
        },

        {
            "id": "emoji_story",
            "title": "🪄 Make a Tiny Story",
            "description": "Create a funny story using these three emojis.",
            "type": "creative",
            "question": "🐸 🚀 🍕",
            "prompt": "Imagine what happens when a frog, a rocket and a pizza meet!",
            "button": "Create Story"
        },

        {
            "id": "would_you_rather",
            "title": "🤔 Would You Rather?",
            "description": "Pick one. There is no wrong answer!",
            "type": "quiz",
            "question": "Would you rather 🦅 fly or 🐬 breathe underwater?",
            "answers": [
                "🦅 Fly",
                "🐬 Breathe underwater"
            ],
            "correct": -1,
            "button": "Pick One"
        },

        {
            "id": "quick_memory",
            "title": "🧠 Memory Challenge",
            "description": "Look at the emojis and remember them!",
            "type": "memory",
            "items": [
                "🍎",
                "🚀",
                "🐱",
                "🌈",
                "🎸"
            ],
            "button": "Start Memory Game"
        },

        {
            "id": "silly_question",
            "title": "😂 Silly Question",
            "description": "Time for a completely unnecessary question.",
            "type": "creative",
            "question": "If your backpack could talk, what would it complain about?",
            "prompt": "Give your backpack a funny answer.",
            "button": "Make Me Laugh"
        },

        {
            "id": "word_chain",
            "title": "🔤 Word Challenge",
            "description": "Think quickly!",
            "type": "creative",
            "question": "Name 5 things that are yellow in 10 seconds! 💛",
            "prompt": "Try to think of five different yellow things.",
            "button": "Start Challenge"
        }
    ],


    "cheer": [

        {
            "id": "compliment",
            "title": "💙 A Little Reminder",
            "description": "You don't have to have everything figured out today.",
            "type": "message",
            "message": "🌱 You're learning.\n🌱 You're growing.\n🌱 You're doing better than you think.",
            "button": "I Needed That"
        },

        {
            "id": "smile_challenge",
            "title": "😄 Smile Challenge",
            "description": "Let's make your brain think of something happy.",
            "type": "steps",
            "steps": [
                "😊 Think of someone who makes you laugh",
                "😂 Remember something funny they did",
                "💭 Replay the moment in your head",
                "😁 Give yourself a tiny smile"
            ],
            "button": "Start Challenge"
        },

        {
            "id": "gratitude",
            "title": "🌷 Tiny Gratitude Moment",
            "description": "Think of three small things that were nice today.",
            "type": "steps",
            "steps": [
                "🌷 One person you're thankful for",
                "☀️ One small thing you enjoyed",
                "💙 One thing you're looking forward to"
            ],
            "button": "Begin"
        },

        {
            "id": "positive_future",
            "title": "✨ Future You",
            "description": "Imagine yourself one month from now.",
            "type": "steps",
            "steps": [
                "🌱 Imagine yourself one month from now",
                "📚 Imagine one thing you've improved",
                "😊 Imagine how proud you'll feel",
                "💪 Tell yourself: I can get there"
            ],
            "button": "Imagine"
        },

        {
            "id": "funny_fact",
            "title": "🐧 Random Smile",
            "description": "Here's a tiny fact to brighten your break.",
            "type": "message",
            "message": "🐧 Penguins propose to their partners by giving them a pebble! 💙\n\nSomewhere out there, a penguin is probably having a better love life than all of us. 😂",
            "button": "That Made Me Smile"
        },

        {
            "id": "mini_adventure",
            "title": "🚀 30-Second Adventure",
            "description": "Close your eyes and imagine this.",
            "type": "steps",
            "steps": [
                "🚀 You are sitting inside a tiny spaceship",
                "🌌 Stars are moving past your window",
                "🪐 You discover a new planet",
                "🌈 Everything on it is your favorite color",
                "😄 You have just discovered your secret escape planet"
            ],
            "button": "Start Adventure"
        }
    ]
}


# ============================================================
# REQUEST MODELS
# ============================================================

class StartRequest(BaseModel):
    mood: str


class ActivityRequest(BaseModel):
    mood: str
    mode: str
    used: list[str] = []


class AIRequest(BaseModel):
    mood: str
    mode: str
    activity: str


# ============================================================
# HELPERS
# ============================================================

def choose_activity(mode: str, used: list[str]):
    activities = ACTIVITIES.get(mode, ACTIVITIES["calm"])

    available = [
        activity
        for activity in activities
        if activity["id"] not in used
    ]

    # If every activity has been used, start a new cycle.
    if not available:
        available = activities

    return random.choice(available)


def clean_text(text: str) -> str:
    return html.escape(text).replace("\n", "<br>")


# ============================================================
# GEMINI PERSONALIZATION
# ============================================================

def generate_personal_message(
    mood: str,
    mode: str,
    activity: str
) -> str:

    prompt = f"""
You are MindMate, a friendly student stress-break assistant.

Student mood: {mood}
Activity: {activity}
Mode: {mode}

Create ONE very short supportive message.

Rules:
- Use simple English.
- Maximum 40 words.
- Use 2-4 friendly emojis.
- Do not give medical advice.
- Do not repeat common motivational phrases.
- Do not mention being an AI.
- Do not create a long paragraph.
- Make it feel natural and warm.

Return only the message.
"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        if response and response.text:
            return response.text.strip()

    except Exception:
        pass

    # Safe fallback if Gemini is unavailable.
    return "💙 Take this tiny break for yourself. You don't need to solve everything right now. 🌱"


# ============================================================
# START API
# ============================================================

@app.post("/api/start")
def start_session(request: StartRequest):

    mood = request.mood.strip()

    return {
        "success": True,
        "mood": mood,
        "message": f"Thanks for telling me. 💙 Let's make the next two minutes a little easier.",
        "options": [
            {
                "id": "calm",
                "icon": "🧘",
                "title": "Calm Me",
                "description": "Relax your mind"
            },
            {
                "id": "distract",
                "icon": "🎮",
                "title": "Distract Me",
                "description": "Give me something fun"
            },
            {
                "id": "cheer",
                "icon": "📖",
                "title": "Cheer Me Up",
                "description": "Make me smile"
            }
        ]
    }


# ============================================================
# ACTIVITY API
# ============================================================

@app.post("/api/activity")
def get_activity(request: ActivityRequest):

    activity = choose_activity(
        request.mode,
        request.used
    )

    return {
        "success": True,
        "activity": activity,
        "used_count": len(request.used) + 1
    }


# ============================================================
# AI PERSONAL MESSAGE
# ============================================================

@app.post("/api/message")
def get_message(request: AIRequest):

    message = generate_personal_message(
        request.mood,
        request.mode,
        request.activity
    )

    return {
        "success": True,
        "message": message
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "app": "MindMate AI"
    }


# ============================================================
# FRONTEND
# ============================================================

HTML = r"""
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>MindMate AI</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family:
        Inter,
        system-ui,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;

    background:
        radial-gradient(
            circle at top left,
            #dff8f0,
            transparent 35%
        ),
        linear-gradient(
            135deg,
            #f4fbff,
            #eef9f5
        );

    color: #17324d;
    min-height: 100vh;
}

.container {
    width: min(900px, 92%);
    margin: auto;
    padding: 30px 0 50px;
}

.header {
    text-align: center;
    margin-bottom: 28px;
}

.logo {
    font-size: 46px;
}

h1 {
    margin: 5px 0;
    font-size: 38px;
    color: #123d5a;
}

.subtitle {
    color: #658096;
    font-size: 17px;
}

.card {
    background: rgba(255,255,255,.88);
    border-radius: 24px;
    padding: 28px;
    margin-top: 20px;

    box-shadow:
        0 15px 45px rgba(41, 92, 112, .10);

    border: 1px solid rgba(255,255,255,.8);
}

.section-title {
    font-size: 21px;
    font-weight: 700;
    margin-bottom: 18px;
}

.mood-grid {
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(120px, 1fr));

    gap: 12px;
}

.mood {
    border: none;
    padding: 17px 10px;
    border-radius: 18px;

    background: #f3f8fb;

    cursor: pointer;

    font-size: 15px;
    font-weight: 600;

    transition: .2s;
}

.mood:hover {
    transform: translateY(-3px);
    background: #e5f5f3;
}

.mood.selected {
    background: #c9eee7;
    box-shadow: 0 0 0 3px #6ac9bb;
}

.mode-grid {
    display: grid;

    grid-template-columns:
        repeat(auto-fit, minmax(220px, 1fr));

    gap: 16px;
}

.mode {
    padding: 25px;

    border: 2px solid transparent;
    border-radius: 20px;

    background: #f8fbfd;

    cursor: pointer;
    text-align: left;

    transition: .2s;
}

.mode:hover {
    transform: translateY(-4px);
    border-color: #8bd4ca;
}

.mode-icon {
    font-size: 36px;
}

.mode-title {
    font-size: 19px;
    font-weight: 700;
    margin-top: 8px;
}

.mode-description {
    color: #72869a;
    margin-top: 5px;
}

.primary {
    width: 100%;
    border: none;

    padding: 17px;

    border-radius: 16px;

    background: #174d6d;
    color: white;

    font-size: 17px;
    font-weight: 700;

    cursor: pointer;

    transition: .2s;
}

.primary:hover {
    transform: translateY(-2px);
    background: #123f59;
}

.primary:disabled {
    opacity: .45;
    cursor: not-allowed;
}

.activity {
    display: none;
}

.activity-card {
    text-align: center;
    padding: 30px 20px;
}

.activity-icon {
    font-size: 55px;
}

.activity-title {
    font-size: 28px;
    margin: 10px 0;
    color: #174d6d;
}

.activity-description {
    color: #71859a;
    font-size: 16px;
}

.step {
    display: none;

    background: #edf9f6;

    border-radius: 18px;

    padding: 25px;

    margin: 20px 0;

    font-size: 21px;
    font-weight: 600;
}

.step.active {
    display: block;
    animation: fade .35s ease;
}

@keyframes fade {
    from {
        opacity: 0;
        transform: translateY(8px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.counter {
    font-size: 14px;
    color: #7990a0;
    margin: 15px;
}

.progress {
    width: 100%;
    height: 8px;

    background: #e5eeee;

    border-radius: 20px;

    overflow: hidden;
}

.progress-bar {
    height: 100%;
    width: 0%;

    background: #63bfae;

    transition: .3s;
}

.actions {
    display: flex;
    gap: 10px;
    margin-top: 18px;
}

.secondary {
    flex: 1;

    padding: 14px;

    border-radius: 14px;

    border: 1px solid #d6e4e8;

    background: white;

    cursor: pointer;

    font-weight: 600;
}

.success {
    display: none;

    text-align: center;

    padding: 30px;
}

.success-icon {
    font-size: 60px;
}

.score {
    display: inline-block;

    margin-top: 15px;

    padding: 10px 18px;

    border-radius: 20px;

    background: #e2f5ef;

    color: #23685d;

    font-weight: 700;
}

.ai-message {
    margin-top: 18px;

    padding: 17px;

    border-radius: 16px;

    background: #f1f7fc;

    color: #456174;

    line-height: 1.6;
}

.footer {
    text-align: center;
    margin-top: 25px;
    color: #8194a2;
    font-size: 14px;
}

.hidden {
    display: none !important;
}

@media(max-width:600px) {

    h1 {
        font-size: 30px;
    }

    .card {
        padding: 20px;
    }

    .activity-title {
        font-size: 24px;
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
            Take a tiny break. You deserve it.
        </div>

    </div>


    <!-- MOOD -->

    <div class="card" id="moodCard">

        <div class="section-title">
            😊 How are you feeling right now?
        </div>

        <div class="mood-grid">

            <button class="mood" onclick="selectMood(this,'Stressed')">
                😰 Stressed
            </button>

            <button class="mood" onclick="selectMood(this,'Sad')">
                😔 Sad
            </button>

            <button class="mood" onclick="selectMood(this,'Tired')">
                😴 Tired
            </button>

            <button class="mood" onclick="selectMood(this,'Angry')">
                😡 Angry
            </button>

            <button class="mood" onclick="selectMood(this,'Worried')">
                😟 Worried
            </button>

            <button class="mood" onclick="selectMood(this,'Overwhelmed')">
                😵 Overwhelmed
            </button>

            <button class="mood" onclick="selectMood(this,'Okay')">
                🙂 Okay
            </button>

            <button class="mood" onclick="selectMood(this,'Excited')">
                🤩 Excited
            </button>

        </div>

    </div>


    <!-- MODES -->

    <div class="card hidden" id="modeCard">

        <div class="section-title">
            💙 What would you like right now?
        </div>

        <div class="mode-grid">

            <button
                class="mode"
                onclick="chooseMode('calm')"
            >

                <div class="mode-icon">🧘</div>

                <div class="mode-title">
                    Calm Me
                </div>

                <div class="mode-description">
                    Relax your mind and body
                </div>

            </button>


            <button
                class="mode"
                onclick="chooseMode('distract')"
            >

                <div class="mode-icon">🎮</div>

                <div class="mode-title">
                    Distract Me
                </div>

                <div class="mode-description">
                    Give me something fun
                </div>

            </button>


            <button
                class="mode"
                onclick="chooseMode('cheer')"
            >

                <div class="mode-icon">📖</div>

                <div class="mode-title">
                    Cheer Me Up
                </div>

                <div class="mode-description">
                    Make me smile
                </div>

            </button>

        </div>

    </div>


    <!-- ACTIVITY -->

    <div class="card activity" id="activityCard">

        <div class="activity-card">

            <div class="activity-icon" id="activityIcon">
                🧘
            </div>

            <div class="activity-title" id="activityTitle">
                Your Activity
            </div>

            <div
                class="activity-description"
                id="activityDescription">
            </div>

            <div id="activityContent"></div>

            <div class="ai-message" id="aiMessage">
            </div>

            <div class="actions">

                <button
                    class="secondary"
                    onclick="newActivity()">
                    🔄 Try Another
                </button>

                <button
                    class="primary"
                    onclick="finishActivity()">
                    💙 I'm Done
                </button>

            </div>

        </div>

    </div>


    <!-- SUCCESS -->

    <div class="card success" id="successCard">

        <div class="success-icon">
            🌟
        </div>

        <h2>
            Nice work!
        </h2>

        <p>
            You just gave yourself a little breathing space.
        </p>

        <div class="score" id="score">
            🌱 Breaks completed: 1
        </div>

        <br><br>

        <button
            class="primary"
            onclick="newActivity()">
            ✨ Give Me Another Break
        </button>

    </div>


    <div class="footer">
        🌱 MindMate AI • Small breaks can make a big difference 💙
    </div>

</div>


<script>

let mood = "";
let mode = "";

let usedActivities = [];

let currentActivity = null;

let completed = 0;


// ============================================================
// MOOD
// ============================================================

function selectMood(button, selectedMood) {

    document
        .querySelectorAll(".mood")
        .forEach(btn => btn.classList.remove("selected"));

    button.classList.add("selected");

    mood = selectedMood;

    document
        .getElementById("modeCard")
        .classList.remove("hidden");
}


// ============================================================
// MODE
// ============================================================

async function chooseMode(selectedMode) {

    mode = selectedMode;

    document
        .getElementById("activityCard")
        .style.display = "block";

    document
        .getElementById("successCard")
        .style.display = "none";

    await loadActivity();
}


// ============================================================
// LOAD ACTIVITY
// ============================================================

async function loadActivity() {

    const response = await fetch(
        "/api/activity",
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                mood: mood,
                mode: mode,
                used: usedActivities
            })
        }
    );

    const data = await response.json();

    currentActivity = data.activity;

    usedActivities.push(
        currentActivity.id
    );

    renderActivity(
        currentActivity
    );

    getAIMessage(
        currentActivity.title
    );
}


// ============================================================
// RENDER
// ============================================================

function renderActivity(activity) {

    const icon =
        activity.title.match(
            /^[^\w\s]+/
        );

    document.getElementById(
        "activityIcon"
    ).textContent =
        icon ? icon[0] : "💙";

    document.getElementById(
        "activityTitle"
    ).textContent =
        activity.title;

    document.getElementById(
        "activityDescription"
    ).textContent =
        activity.description;

    const content =
        document.getElementById(
            "activityContent"
        );

    content.innerHTML = "";

    if (activity.type === "steps") {

        const progress =
            document.createElement(
                "div"
            );

        progress.className =
            "progress";

        progress.innerHTML =
            '<div class="progress-bar"></div>';

        content.appendChild(progress);

        activity.steps.forEach(
            (step, index) => {

                const div =
                    document.createElement(
                        "div"
                    );

                div.className =
                    "step";

                if (index === 0) {
                    div.classList.add(
                        "active"
                    );
                }

                div.textContent = step;

                content.appendChild(div);
            }
        );

        const button =
            document.createElement(
                "button"
            );

        button.className =
            "primary";

        button.style.marginTop =
            "15px";

        button.textContent =
            activity.button;

        button.onclick =
            () => nextStep(
                activity.steps.length
            );

        content.appendChild(button);

    }

    else if (
        activity.type === "breathing"
    ) {

        const box =
            document.createElement(
                "div"
            );

        box.className = "step active";

        box.innerHTML =
            "🌬️ Get comfortable.<br><br>" +
            "Press the button and follow the breathing rhythm.";

        content.appendChild(box);

        const button =
            document.createElement(
                "button"
            );

        button.className =
            "primary";

        button.textContent =
            "🌬️ Start";

        button.onclick =
            () => breathingExercise(
                box,
                button
            );

        content.appendChild(button);
    }

    else if (
        activity.type === "counter"
    ) {

        const box =
            document.createElement(
                "div"
            );

        box.className =
            "step active";

        box.id =
            "breathCounter";

        box.textContent =
            "🌬️ Ready for a slow breath?";

        content.appendChild(box);

        const button =
            document.createElement(
                "button"
            );

        button.className =
            "primary";

        button.textContent =
            activity.button;

        let count = 0;

        button.onclick = () => {

            count++;

            box.textContent =
                `🌬️ Breath ${count} of ${activity.count}`;

            if (
                count >= activity.count
            ) {

                button.textContent =
                    "✨ Beautiful!";

                button.disabled =
                    true;
            }
        };

        content.appendChild(button);
    }

    else if (
        activity.type === "quiz"
    ) {

        const question =
            document.createElement(
                "div"
            );

        question.className =
            "step active";

        question.textContent =
            activity.question;

        content.appendChild(question);

        activity.answers.forEach(
            (answer, index) => {

                const button =
                    document.createElement(
                        "button"
                    );

                button.className =
                    "secondary";

                button.style.margin =
                    "5px";

                button.textContent =
                    answer;

                button.onclick = () => {

                    if (
                        activity.correct >= 0
                    ) {

                        if (
                            index ===
                            activity.correct
                        ) {

                            question.innerHTML =
                                "🎉 Correct! You got it!";

                        } else {

                            question.innerHTML =
                                "😄 Nice try! The answer was " +
                                activity.answers[
                                    activity.correct
                                ];
                        }

                    } else {

                        question.innerHTML =
                            "✨ Great choice! There is no wrong answer.";
                    }

                };

                content.appendChild(
                    button
                );
            }
        );
    }

    else if (
        activity.type === "memory"
    ) {

        const box =
            document.createElement(
                "div"
            );

        box.className =
            "step active";

        box.style.fontSize =
            "38px";

        box.textContent =
            activity.items.join(" ");

        content.appendChild(box);

        const button =
            document.createElement(
                "button"
            );

        button.className =
            "primary";

        button.textContent =
            "🙈 Hide & Test Me";

        button.onclick = () => {

            box.textContent =
                "❓ What emojis did you see?";

            button.textContent =
                "✨ I Remembered!";
        };

        content.appendChild(button);
    }

    else {

        const box =
            document.createElement(
                "div"
            );

        box.className =
            "step active";

        box.innerHTML =
            activity.message ||
            activity.question ||
            activity.prompt ||
            "";

        content.appendChild(box);
    }
}


// ============================================================
// STEP ACTIVITY
// ============================================================

function nextStep(total) {

    const steps =
        document.querySelectorAll(
            ".step"
        );

    let current = -1;

    steps.forEach(
        (step, index) => {

            if (
                step.classList.contains(
                    "active"
                )
            ) {
                current = index;
            }

            step.classList.remove(
                "active"
            );
        }
    );

    const next =
        current + 1;

    if (next < total) {

        steps[next].classList.add(
            "active"
        );

        const percentage =
            ((next + 1) / total) * 100;

        const bar =
            document.querySelector(
                ".progress-bar"
            );

        if (bar) {
            bar.style.width =
                percentage + "%";
        }

    } else {

        steps[total - 1]
            .classList.add(
                "active"
            );
    }
}


// ============================================================
// BREATHING
// ============================================================

function breathingExercise(
    box,
    button
) {

    let count = 0;

    button.disabled = true;

    function cycle() {

        if (count >= 4) {

            box.innerHTML =
                "🌟 Done!<br><br>" +
                "Notice how your body feels now.";

            button.disabled =
                false;

            button.textContent =
                "🌬️ Again";

            return;
        }

        box.innerHTML =
            "🌬️ Breathe IN<br>" +
            "<strong>1... 2... 3... 4...</strong>";

        setTimeout(
            () => {

                box.innerHTML =
                    "⏸️ Hold<br>" +
                    "<strong>1... 2...</strong>";

                setTimeout(
                    () => {

                        box.innerHTML =
                            "🍃 Breathe OUT<br>" +
                            "<strong>1... 2... 3... 4... 5... 6...</strong>";

                        setTimeout(
                            () => {

                                count++;

                                cycle();

                            },
                            3000
                        );

                    },
                    1500
                );

            },
            2500
        );
    }

    cycle();
}


// ============================================================
// AI MESSAGE
// ============================================================

async function getAIMessage(
    activityName
) {

    const element =
        document.getElementById(
            "aiMessage"
        );

    element.textContent =
        "💭 Preparing a little message for you...";

    try {

        const response =
            await fetch(
                "/api/message",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        mood: mood,
                        mode: mode,
                        activity: activityName
                    })
                }
            );

        const data =
            await response.json();

        element.innerHTML =
            data.message;

    } catch {

        element.textContent =
            "💙 This little moment is just for you.";
    }
}


// ============================================================
// NEW ACTIVITY
// ============================================================

async function newActivity() {

    document
        .getElementById(
            "successCard"
        )
        .style.display = "none";

    document
        .getElementById(
            "activityCard"
        )
        .style.display = "block";

    await loadActivity();
}


// ============================================================
// FINISH
// ============================================================

function finishActivity() {

    completed++;

    document
        .getElementById(
            "activityCard"
        )
        .style.display = "none";

    document
        .getElementById(
            "successCard"
        )
        .style.display = "block";

    document
        .getElementById(
            "score"
        )
        .textContent =
        `🌱 Breaks completed: ${completed}`;
}

</script>

</body>

</html>
"""


# ============================================================
# HOME PAGE
# ============================================================

@app.get("/", response_class=HTMLResponse)
def home():

    return HTMLResponse(
        content=HTML
    )

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port
    )
