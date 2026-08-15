import os
import random
import html
from typing import Dict, List

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from google import genai
from google.genai import types


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="MindMate AI",
    description="A small AI-powered stress buster for students."
)


# ============================================================
# GEMINI
# ============================================================

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable is not set.")

client = genai.Client(api_key=API_KEY)

# Use a current Gemini model.
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")


# ============================================================
# SIMPLE SESSION MEMORY
# ============================================================

sessions: Dict[str, List[str]] = {}


def get_session(session_id: str) -> List[str]:
    if session_id not in sessions:
        sessions[session_id] = []

    return sessions[session_id]


def remember_response(session_id: str, response: str):
    history = get_session(session_id)

    # Store only short summaries of previous responses.
    history.append(response[:500])

    # Prevent memory from growing forever.
    if len(history) > 8:
        sessions[session_id] = history[-8:]


# ============================================================
# REQUEST MODELS
# ============================================================

class StartRequest(BaseModel):
    session_id: str
    mood: str


class ActionRequest(BaseModel):
    session_id: str
    mood: str
    action: str


class NextRequest(BaseModel):
    session_id: str
    mood: str
    action: str
    previous: str


# ============================================================
# MOOD DATA
# ============================================================

MOODS = {
    "Stressed": "😰",
    "Sad": "😔",
    "Tired": "😴",
    "Angry": "😡",
    "Worried": "😟",
    "Overwhelmed": "😵",
    "Okay": "🙂",
    "Excited": "🤩",
}


ACTIONS = {
    "Calm Me": {
        "emoji": "🧘",
        "description": "Slow down and relax"
    },
    "Distract Me": {
        "emoji": "🎮",
        "description": "Give me something fun"
    },
    "Cheer Me Up": {
        "emoji": "🌈",
        "description": "Make me smile"
    },
    "Reset My Mind": {
        "emoji": "🔄",
        "description": "Help me start fresh"
    },
}


# ============================================================
# FALLBACK CONTENT
# ============================================================

FALLBACKS = {

    "Calm Me": [
        "🌿 Let's slow everything down for a moment.\n\n"
        "Take a slow breath in for 4 seconds... 🌬️\n"
        "Hold it for 2 seconds... ⏸️\n"
        "Now breathe out slowly for 6 seconds. 😌\n\n"
        "You don't have to solve everything right now. "
        "Just take this one minute.",

        "🧘 Mini reset:\n\n"
        "Relax your shoulders.\n"
        "Unclench your jaw.\n"
        "Put your phone down for 20 seconds.\n"
        "Take one slow breath. 🌱\n\n"
        "That's enough for now. You are allowed to pause.",

        "🌊 Imagine your thoughts are little waves.\n\n"
        "You don't have to stop the waves.\n"
        "Just watch them come and go.\n\n"
        "For the next 30 seconds, breathe slowly and let your mind be quiet. 💙"
    ],

    "Distract Me": [
        "🎮 Quick challenge!\n\n"
        "Look around you and find:\n"
        "🔴 Something red\n"
        "🟢 Something green\n"
        "🔵 Something blue\n\n"
        "Found them? Nice! 😄\n"
        "Your brain just took a tiny vacation.",

        "🕵️ Tiny detective challenge!\n\n"
        "Find the most unusual object near you.\n"
        "Give it a funny name.\n"
        "Now imagine it has a secret job. 😂\n\n"
        "What is its job?",

        "🎲 10-second game!\n\n"
        "Think of 3 foods that start with the letter 'P'.\n\n"
        "Ready?\n"
        "Go! 🚀\n\n"
        "Your brain deserves a little playful break."
    ],

    "Cheer Me Up": [
        "🌈 Here is your reminder:\n\n"
        "You have survived every difficult day you've faced so far.\n\n"
        "That's a pretty impressive record. 💙\n\n"
        "Today doesn't have to be perfect.\n"
        "It only needs to be a little better than five minutes ago. 😊",

        "🐧 Important announcement:\n\n"
        "A tiny imaginary penguin has officially been assigned to cheer you up. 🐧🎉\n\n"
        "Its first message is:\n\n"
        "\"You are doing better than you think!\"\n\n"
        "Penguin has spoken. 😂💙",

        "✨ Today's tiny win:\n\n"
        "You opened MindMate instead of simply ignoring how you feel.\n\n"
        "That counts.\n"
        "Small steps are still steps. 🌱"
    ],

    "Reset My Mind": [
        "🔄 Let's do a 30-second mental reset.\n\n"
        "1️⃣ Forget the last task for a moment.\n"
        "2️⃣ Take one deep breath.\n"
        "3️⃣ Choose ONE thing you can do next.\n\n"
        "Not ten things.\n"
        "Just one. 🎯\n\n"
        "Small progress beats overwhelming yourself.",

        "🧠 Brain reset:\n\n"
        "Write down the one thing bothering you most.\n"
        "Now ask:\n\n"
        "\"Can I do something about this right now?\"\n\n"
        "If yes → take one tiny step.\n"
        "If no → give yourself permission to pause. 🌱",

        "☀️ Fresh start unlocked!\n\n"
        "You don't need to restart your whole day.\n"
        "You only need to restart this moment.\n\n"
        "Take a breath.\n"
        "Stretch.\n"
        "Drink some water.\n\n"
        "Now begin again. 💙"
    ],
}


# ============================================================
# AI GENERATION
# ============================================================

def generate_ai_response(
    session_id: str,
    mood: str,
    action: str
) -> str:

    history = get_session(session_id)

    previous_text = "\n---\n".join(history[-4:])

    prompt = f"""
You are MindMate AI, a friendly student stress-buster.

The student's current mood is:
{mood}

The student selected:
{action}

Create ONE short interactive response.

IMPORTANT:
- Do NOT repeat previous responses.
- Do NOT give a long lecture.
- Use very simple English.
- Be warm, friendly and encouraging.
- Use emojis naturally.
- Make it feel like a real interactive app.
- Give the student ONE small activity they can do in 30-90 seconds.
- The activity should be easy and safe.
- End with exactly ONE short question or challenge.
- Do not mention therapy, diagnosis, or mental illness.
- Do not say "as an AI".
- Do not repeat the mood or action unnecessarily.

Previous responses:
{previous_text}

Now create a fresh response.
"""

    try:

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.9,
                max_output_tokens=350,
                candidate_count=1,
                automatic_function_calling={
                    "disable": True
                }
            )
        )

        text = response.text.strip()

        if text:
            remember_response(session_id, text)
            return text

    except Exception as e:
        print("Gemini error:", str(e))

    # Fallback if Gemini fails
    options = FALLBACKS.get(action, FALLBACKS["Calm Me"])

    history = get_session(session_id)

    available = [
        item for item in options
        if item[:80] not in [x[:80] for x in history]
    ]

    if not available:
        available = options

    result = random.choice(available)

    remember_response(session_id, result)

    return result


# ============================================================
# START
# ============================================================

@app.post("/api/start")
def start_session(request: StartRequest):

    # New session = fresh experience
    sessions[request.session_id] = []

    mood_emoji = MOODS.get(request.mood, "🙂")

    message = (
        f"{mood_emoji} Thanks for checking in.\n\n"
        f"You chose **{request.mood}**.\n\n"
        "You don't need to fix everything right now. "
        "Let's take a tiny break together. 💙"
    )

    return {
        "success": True,
        "message": message,
        "actions": [
            {
                "name": name,
                "emoji": info["emoji"],
                "description": info["description"]
            }
            for name, info in ACTIONS.items()
        ]
    }


# ============================================================
# ACTION
# ============================================================

@app.post("/api/action")
def action(request: ActionRequest):

    response = generate_ai_response(
        request.session_id,
        request.mood,
        request.action
    )

    return {
        "success": True,
        "action": request.action,
        "response": response,
        "next_options": [
            "🎲 Give me another",
            "🌿 Try a different activity",
            "💙 I'm feeling better"
        ]
    }


# ============================================================
# ANOTHER RESPONSE
# ============================================================

@app.post("/api/next")
def next_response(request: NextRequest):

    response = generate_ai_response(
        request.session_id,
        request.mood,
        request.action
    )

    return {
        "success": True,
        "response": response
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

<html>

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

    font-family:
        Inter,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;

    background:
        linear-gradient(
            135deg,
            #eef7ff,
            #f8f5ff
        );

    min-height: 100vh;

    color: #172554;
}

.container {

    width: 92%;
    max-width: 900px;

    margin: auto;

    padding: 30px 0 60px;
}

.hero {

    text-align: center;

    padding: 25px 10px 30px;
}

.logo {

    font-size: 48px;
}

h1 {

    margin: 8px 0;

    font-size: 42px;

    color: #123c73;
}

.subtitle {

    font-size: 18px;

    color: #64748b;
}

.card {

    background: rgba(255,255,255,.88);

    border-radius: 24px;

    padding: 28px;

    margin-top: 20px;

    box-shadow:
        0 15px 45px rgba(30,64,175,.10);

    border: 1px solid rgba(255,255,255,.8);
}

.section-title {

    font-size: 22px;

    font-weight: 700;

    margin-bottom: 18px;
}

.moods {

    display: grid;

    grid-template-columns:
        repeat(4, 1fr);

    gap: 12px;
}

.mood {

    border: none;

    padding: 16px 8px;

    border-radius: 18px;

    background: #f1f5f9;

    cursor: pointer;

    font-size: 15px;

    transition: .2s;
}

.mood:hover {

    transform: translateY(-3px);

    background: #dbeafe;
}

.mood.selected {

    background: #2563eb;

    color: white;

    box-shadow:
        0 8px 20px rgba(37,99,235,.25);
}

.action-grid {

    display: grid;

    grid-template-columns:
        repeat(2, 1fr);

    gap: 16px;
}

.action {

    border: none;

    border-radius: 22px;

    padding: 24px;

    text-align: left;

    background: white;

    cursor: pointer;

    box-shadow:
        0 8px 25px rgba(0,0,0,.07);

    transition: .25s;

    border: 2px solid transparent;
}

.action:hover {

    transform: translateY(-5px);

    border-color: #93c5fd;

}

.action-icon {

    font-size: 36px;
}

.action-title {

    font-size: 19px;

    font-weight: 700;

    margin-top: 8px;
}

.action-desc {

    color: #64748b;

    margin-top: 5px;
}

.primary {

    width: 100%;

    border: none;

    border-radius: 18px;

    padding: 16px;

    margin-top: 22px;

    background:
        linear-gradient(
            135deg,
            #2563eb,
            #4f46e5
        );

    color: white;

    font-size: 17px;

    font-weight: 700;

    cursor: pointer;

    box-shadow:
        0 10px 25px rgba(37,99,235,.25);
}

.primary:hover {

    transform: translateY(-2px);
}

.result {

    margin-top: 24px;

    background:
        linear-gradient(
            135deg,
            #eff6ff,
            #f5f3ff
        );

    border-radius: 22px;

    padding: 25px;

    line-height: 1.75;

    font-size: 17px;

    white-space: pre-wrap;

    border: 1px solid #dbeafe;

}

.result-title {

    font-size: 21px;

    font-weight: 700;

    margin-bottom: 14px;

    color: #1e3a8a;
}

.next-buttons {

    display: flex;

    flex-wrap: wrap;

    gap: 10px;

    margin-top: 18px;
}

.next-btn {

    border: none;

    border-radius: 14px;

    padding: 12px 17px;

    background: white;

    color: #1e40af;

    border: 1px solid #bfdbfe;

    cursor: pointer;

    font-weight: 600;
}

.next-btn:hover {

    background: #eff6ff;
}

.loading {

    text-align: center;

    padding: 20px;

    color: #64748b;
}

.hidden {

    display: none;
}

.footer {

    text-align: center;

    margin-top: 30px;

    color: #64748b;

    font-size: 14px;
}

@media(max-width:650px) {

    h1 {
        font-size: 32px;
    }

    .moods {

        grid-template-columns:
            repeat(2, 1fr);
    }

    .action-grid {

        grid-template-columns: 1fr;
    }

    .card {

        padding: 20px;
    }
}

</style>

</head>


<body>


<div class="container">


<div class="hero">

<div class="logo">🌱</div>

<h1>MindMate AI</h1>

<div class="subtitle">

Your little AI-powered stress-buster 💙

<br>

Take a tiny break. You deserve it.

</div>

</div>


<div class="card">

<div class="section-title">

😊 How are you feeling right now?

</div>


<div class="moods">

<button class="mood" data-mood="Stressed">
😰<br>Stressed
</button>

<button class="mood" data-mood="Sad">
😔<br>Sad
</button>

<button class="mood" data-mood="Tired">
😴<br>Tired
</button>

<button class="mood" data-mood="Angry">
😡<br>Angry
</button>

<button class="mood" data-mood="Worried">
😟<br>Worried
</button>

<button class="mood" data-mood="Overwhelmed">
😵<br>Overwhelmed
</button>

<button class="mood" data-mood="Okay">
🙂<br>Okay
</button>

<button class="mood" data-mood="Excited">
🤩<br>Excited
</button>

</div>


<button
class="primary"
id="startBtn"
disabled>

💙 Help Me Feel Better

</button>

</div>


<div
class="card hidden"
id="actionsCard">

<div class="section-title">

🤖 What would you like to do?

</div>


<div
class="action-grid"
id="actionGrid">

</div>

</div>


<div
class="card hidden"
id="resultCard">

<div class="result-title">

✨ Your MindMate Moment

</div>

<div
class="result"
id="result">

</div>


<div
class="next-buttons"
id="nextButtons">

<button
class="next-btn"
id="anotherBtn">

🎲 Give me another

</button>

<button
class="next-btn"
id="differentBtn">

🌿 Try a different activity

</button>

<button
class="next-btn"
id="betterBtn">

💙 I'm feeling better

</button>

</div>

</div>


<div class="footer">

🌱 MindMate AI • A small break can make a big difference

</div>


</div>


<script>

let sessionId =
    "session_" +
    Date.now() +
    "_" +
    Math.random()
        .toString(36)
        .substring(2, 8);

let selectedMood = "";

let selectedAction = "";

const moods =
    document.querySelectorAll(".mood");

const startBtn =
    document.getElementById("startBtn");

const actionsCard =
    document.getElementById("actionsCard");

const actionGrid =
    document.getElementById("actionGrid");

const resultCard =
    document.getElementById("resultCard");

const result =
    document.getElementById("result");


// ========================================================
// MOOD SELECTION
// ========================================================

moods.forEach(button => {

    button.addEventListener(
        "click",
        () => {

            moods.forEach(
                b => b.classList.remove("selected")
            );

            button.classList.add("selected");

            selectedMood =
                button.dataset.mood;

            startBtn.disabled = false;

        }
    );

});


// ========================================================
// START
// ========================================================

startBtn.addEventListener(
    "click",
    async () => {

        startBtn.disabled = true;

        startBtn.innerText =
            "💙 Let's take a moment...";

        try {

            const response =
                await fetch("/api/start", {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        session_id:
                            sessionId,

                        mood:
                            selectedMood

                    })

                });

            const data =
                await response.json();

            actionGrid.innerHTML = "";

            data.actions.forEach(
                action => {

                    const button =
                        document.createElement("button");

                    button.className =
                        "action";

                    button.innerHTML = `

                        <div class="action-icon">
                            ${action.emoji}
                        </div>

                        <div class="action-title">
                            ${action.name}
                        </div>

                        <div class="action-desc">
                            ${action.description}
                        </div>
                    `;

                    button.onclick =
                        () => chooseAction(
                            action.name
                        );

                    actionGrid.appendChild(button);

                }
            );

            actionsCard.classList.remove(
                "hidden"
            );

            actionsCard.scrollIntoView({
                behavior: "smooth"
            });

        } catch (error) {

            alert(
                "Something went wrong. Please try again."
            );

        } finally {

            startBtn.disabled = false;

            startBtn.innerText =
                "💙 Help Me Feel Better";

        }

    }
);


// ========================================================
// ACTION
// ========================================================

async function chooseAction(action) {

    selectedAction = action;

    resultCard.classList.remove(
        "hidden"
    );

    result.innerHTML = `
        <div class="loading">
            🌱 MindMate is preparing a tiny break for you...
        </div>
    `;

    resultCard.scrollIntoView({
        behavior: "smooth"
    });

    try {

        const response =
            await fetch("/api/action", {

                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({

                    session_id:
                        sessionId,

                    mood:
                        selectedMood,

                    action:
                        selectedAction

                })

            });

        const data =
            await response.json();

        showResult(data.response);

    } catch (error) {

        result.innerText =
            "💙 I couldn't prepare your activity right now. Try again.";

    }

}


// ========================================================
// SHOW RESULT
// ========================================================

function showResult(text) {

    // Convert basic markdown safely
    let safe =
        escapeHtml(text);

    safe =
        safe.replace(
            /\*\*(.*?)\*\*/g,
            "<strong>$1</strong>"
        );

    safe =
        safe.replace(
            /\n/g,
            "<br>"
        );

    result.innerHTML =
        safe;

}


// ========================================================
// ANOTHER
// ========================================================

document
    .getElementById("anotherBtn")
    .addEventListener(
        "click",
        async () => {

            result.innerHTML = `
                <div class="loading">
                    🎲 Finding something fresh...
                </div>
            `;

            try {

                const response =
                    await fetch("/api/next", {

                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({

                            session_id:
                                sessionId,

                            mood:
                                selectedMood,

                            action:
                                selectedAction,

                            previous:
                                result.innerText

                        })

                    });

                const data =
                    await response.json();

                showResult(
                    data.response
                );

            } catch (error) {

                result.innerText =
                    "💙 Let's try that again.";

            }

        }
    );


// ========================================================
// DIFFERENT ACTIVITY
// ========================================================

document
    .getElementById("differentBtn")
    .addEventListener(
        "click",
        () => {

            actionsCard.scrollIntoView({
                behavior: "smooth"
            });

        }
    );


// ========================================================
// FEELING BETTER
// ========================================================

document
    .getElementById("betterBtn")
    .addEventListener(
        "click",
        () => {

            result.innerHTML = `

                <div style="
                    text-align:center;
                    font-size:20px;
                ">

                    🌟 That's wonderful! 💙

                    <br><br>

                    You just gave yourself
                    a little space to breathe.

                    <br><br>

                    🌱 Remember:
                    <br>
                    You don't always need
                    a big solution.

                    <br>
                    Sometimes you just need
                    a small pause.

                    <br><br>

                    😊 Be kind to yourself today.

                </div>

            `;

        }
    );


// ========================================================
// ESCAPE HTML
// ========================================================

function escapeHtml(text) {

    const div =
        document.createElement("div");

    div.textContent =
        text;

    return div.innerHTML;
}

</script>


</body>

</html>
"""


# ============================================================
# HOME
# ============================================================

@app.get("/", response_class=HTMLResponse)
def home():

    return HTMLResponse(content=HTML)


# ============================================================
# RUN LOCALLY
# ============================================================

if __name__ == "__main__":

    import uvicorn

    port = int(
        os.getenv("PORT", "8000")
    )

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port
    )
