import os
import html
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from google import genai
from google.genai import types


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="MindMate AI",
    description="A small AI-powered stress-buster for students",
    version="1.0.0"
)


# ============================================================
# GEMINI CLIENT
# ============================================================

API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY or GOOGLE_API_KEY is not configured in Render."
    )

client = genai.Client(api_key=API_KEY)


# ============================================================
# REQUEST MODEL
# ============================================================

class MindMateRequest(BaseModel):
    mood: str
    activity: str


# ============================================================
# GEMINI FUNCTION
# ============================================================

def generate_activity(mood: str, activity: str) -> str:

    prompts = {

        "Calm Me": f"""
You are MindMate AI, a friendly student stress-buster.

The student currently feels: {mood}

Create a short calming activity that takes about 2 minutes.

Rules:
- Use very simple English.
- Be warm and encouraging.
- Give exactly 3 to 5 small steps.
- Include breathing, grounding, relaxation, or a peaceful visualization.
- Do NOT give medical advice.
- Do NOT mention therapy or diagnosis.
- Use a few appropriate emojis.
- End with one short encouraging sentence.
- Make the activity easy to do anywhere.

Format:

🧘 CALM MOMENT

Short encouraging introduction.

1️⃣ ...
2️⃣ ...
3️⃣ ...
4️⃣ ...

💙 Final encouraging sentence.
""",

        "Distract Me": f"""
You are MindMate AI, a playful and friendly student stress-buster.

The student currently feels: {mood}

Create a fun activity that takes about 2 to 5 minutes.

Choose something such as:
- a tiny quiz
- a fun guessing game
- a silly challenge
- a riddle
- a word game
- a quick imagination game
- a mini creativity challenge

Rules:
- Use simple English.
- Make it genuinely fun.
- Give the student something to DO, not just something to read.
- Use emojis.
- Avoid anything requiring special equipment.
- Keep it suitable for students.

Format:

🎮 QUICK FUN BREAK

Short playful introduction.

🎯 CHALLENGE
...

💡 YOUR TURN
...

✨ BONUS
...

End with a cheerful sentence.
""",

        "Cheer Me Up": f"""
You are MindMate AI, a kind and cheerful friend.

The student currently feels: {mood}

Create a short mood-lifting experience that takes about 2 to 5 minutes.

Include:
- one positive thought
- one tiny fun activity
- one playful question or challenge
- one encouraging message

Rules:
- Use very simple English.
- Do not sound like a lecture.
- Do not give medical advice.
- Do not mention diagnosis or therapy.
- Use friendly emojis.
- Make it feel personal and uplifting.

Format:

🌈 LITTLE MOOD BOOST

A warm opening.

💭 THINK ABOUT THIS
...

🎯 TRY THIS
...

😄 FUN QUESTION
...

💙 REMEMBER
...

End with a hopeful sentence.
"""
    }

    prompt = prompts.get(
        activity,
        f"""
You are MindMate AI.

The student feels {mood}.

Give them a simple 2-minute stress-busting activity.
Use simple English, friendly emojis and 3-5 steps.
End with encouragement.
"""
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.8,
                max_output_tokens=700
            )
        )

        if response.text:
            return response.text.strip()

        return "💙 Take a slow breath. You are doing better than you think."

    except Exception as e:
        print(f"Gemini error: {type(e).__name__}: {e}")

        return fallback_activity(mood, activity)


# ============================================================
# FALLBACK
# ============================================================

def fallback_activity(mood: str, activity: str) -> str:

    if activity == "Calm Me":

        return f"""
🧘 **CALM MOMENT**

You are feeling **{mood}**, and that's okay. Let's take a tiny break. 💙

1️⃣ Sit comfortably and relax your shoulders.

2️⃣ Breathe in slowly for 4 seconds. 🌬️

3️⃣ Hold for 2 seconds.

4️⃣ Breathe out slowly for 6 seconds. 😌

5️⃣ Look around and notice 3 things you can see.

💙 You don't have to solve everything right now. Just take this moment for yourself.
"""

    if activity == "Distract Me":

        return """
🎮 **QUICK FUN BREAK**

Let's give your brain a tiny adventure! 😄

🎯 **Guess the word!**

I am thinking of something that:

🔹 Is yellow  
🔹 Is curved  
🔹 Monkeys love it 🍌

What am I?

...

🍌 **Answer: A BANANA!**

😄 Now make up your own silly riddle.

✨ A little fun can give your brain a fresh start!
"""

    return f"""
🌈 **LITTLE MOOD BOOST**

You're feeling **{mood}** right now. That's completely okay. 💙

💭 **THINK ABOUT THIS**

You don't have to have everything figured out today.

🎯 **TRY THIS**

Smile for 5 seconds, stretch your arms, and take one deep breath. 😊

😄 **FUN QUESTION**

If you could instantly teleport anywhere for 10 minutes, where would you go?

💙 **REMEMBER**

A difficult moment is only one moment. Better moments can come next. 🌱
"""


# ============================================================
# API
# ============================================================

@app.post("/api/start")
def start_mindmate(request: MindMateRequest):

    mood = request.mood.strip()
    activity = request.activity.strip()

    if not mood:
        return {
            "success": False,
            "message": "Please choose how you are feeling."
        }

    if not activity:
        return {
            "success": False,
            "message": "Please choose an activity."
        }

    result = generate_activity(mood, activity)

    return {
        "success": True,
        "mood": mood,
        "activity": activity,
        "response": result
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

@app.get("/", response_class=HTMLResponse)
def home():

    return """
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
    min-height: 100vh;
    font-family: Arial, sans-serif;

    background:
        radial-gradient(
            circle at top left,
            #dff7ec,
            transparent 35%
        ),
        linear-gradient(
            135deg,
            #eefbf6,
            #eaf4ff
        );

    color: #183b56;
}

.container {
    width: min(900px, 92%);
    margin: auto;
    padding: 35px 0 50px;
}

.header {
    text-align: center;
    margin-bottom: 30px;
}

.logo {
    font-size: 55px;
}

h1 {
    margin: 5px 0;
    font-size: 42px;
    color: #123c55;
}

.subtitle {
    font-size: 18px;
    color: #557080;
}

.card {
    background: rgba(255,255,255,0.88);
    border-radius: 24px;
    padding: 28px;
    margin-top: 20px;

    box-shadow:
        0 12px 35px rgba(30,80,100,0.10);
}

.section-title {
    font-size: 21px;
    font-weight: bold;
    margin-bottom: 18px;
}

.mood-grid {
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(130px, 1fr));

    gap: 12px;
}

.mood {
    border: 2px solid #d8e9ef;
    background: white;
    padding: 15px 10px;
    border-radius: 16px;

    cursor: pointer;
    font-size: 16px;

    transition: 0.2s;
}

.mood:hover {
    transform: translateY(-2px);
    border-color: #63b99b;
}

.mood.selected {
    background: #dff7ec;
    border-color: #35a875;
    font-weight: bold;
}

.activities {
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(180px, 1fr));

    gap: 15px;
}

.activity {
    border: none;
    border-radius: 18px;
    padding: 20px;

    background: #f4f9ff;
    color: #183b56;

    cursor: pointer;

    transition: 0.2s;
}

.activity:hover {
    transform: translateY(-3px);
}

.activity.selected {
    background: #dff0ff;
    outline: 3px solid #65a9d6;
}

.activity-icon {
    font-size: 35px;
}

.activity-name {
    font-size: 18px;
    font-weight: bold;
    margin-top: 8px;
}

.activity-desc {
    color: #617582;
    margin-top: 5px;
}

button.generate {
    width: 100%;
    border: none;

    margin-top: 25px;
    padding: 17px;

    border-radius: 16px;

    background: #247ba0;
    color: white;

    font-size: 18px;
    font-weight: bold;

    cursor: pointer;
}

button.generate:hover {
    background: #1b6381;
}

button.generate:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.result {
    display: none;

    margin-top: 25px;

    background: white;

    border-radius: 22px;
    padding: 30px;

    line-height: 1.7;

    box-shadow:
        0 10px 30px rgba(30,80,100,0.08);

    white-space: pre-wrap;
}

.loading {
    display: none;
    text-align: center;
    padding: 20px;
    font-size: 18px;
}

.footer {
    text-align: center;
    margin-top: 30px;
    color: #708895;
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

        <p>
            Take a 2-minute break. You deserve it.
        </p>

    </div>


    <div class="card">

        <div class="section-title">
            😊 How are you feeling right now?
        </div>

        <div class="mood-grid">

            <button class="mood"
                    onclick="selectMood(this, 'Stressed')">
                😰 Stressed
            </button>

            <button class="mood"
                    onclick="selectMood(this, 'Sad')">
                😔 Sad
            </button>

            <button class="mood"
                    onclick="selectMood(this, 'Tired')">
                😴 Tired
            </button>

            <button class="mood"
                    onclick="selectMood(this, 'Angry')">
                😡 Angry
            </button>

            <button class="mood"
                    onclick="selectMood(this, 'Worried')">
                😟 Worried
            </button>

            <button class="mood"
                    onclick="selectMood(this, 'Overwhelmed')">
                😵 Overwhelmed
            </button>

            <button class="mood"
                    onclick="selectMood(this, 'Okay')">
                🙂 Okay
            </button>

            <button class="mood"
                    onclick="selectMood(this, 'Excited')">
                🤩 Excited
            </button>

        </div>

    </div>


    <div class="card">

        <div class="section-title">
            🤖 What would you like to do?
        </div>

        <div class="activities">

            <button class="activity"
                    onclick="selectActivity(this, 'Calm Me')">

                <div class="activity-icon">
                    🧘
                </div>

                <div class="activity-name">
                    Calm Me
                </div>

                <div class="activity-desc">
                    Relax your mind
                </div>

            </button>


            <button class="activity"
                    onclick="selectActivity(this, 'Distract Me')">

                <div class="activity-icon">
                    🎮
                </div>

                <div class="activity-name">
                    Distract Me
                </div>

                <div class="activity-desc">
                    Give me something fun
                </div>

            </button>


            <button class="activity"
                    onclick="selectActivity(this, 'Cheer Me Up')">

                <div class="activity-icon">
                    📖
                </div>

                <div class="activity-name">
                    Cheer Me Up
                </div>

                <div class="activity-desc">
                    Make me smile
                </div>

            </button>

        </div>


        <button class="generate"
                id="generateButton"
                onclick="generateActivity()"
                disabled>

            💙 Help Me Feel Better

        </button>

        <div class="loading" id="loading">
            🌱 MindMate is preparing your little break...
        </div>

    </div>


    <div class="result"
         id="result">
    </div>


    <div class="footer">
        🌱 MindMate AI • A small break can make a big difference 💙
    </div>

</div>


<script>

let selectedMood = "";
let selectedActivity = "";


function selectMood(button, mood) {

    document
        .querySelectorAll(".mood")
        .forEach(item => {
            item.classList.remove("selected");
        });

    button.classList.add("selected");

    selectedMood = mood;

    updateButton();

}


function selectActivity(button, activity) {

    document
        .querySelectorAll(".activity")
        .forEach(item => {
            item.classList.remove("selected");
        });

    button.classList.add("selected");

    selectedActivity = activity;

    updateButton();

}


function updateButton() {

    const button =
        document.getElementById("generateButton");

    button.disabled =
        !(selectedMood && selectedActivity);

}


async function generateActivity() {

    const result =
        document.getElementById("result");

    const loading =
        document.getElementById("loading");

    const button =
        document.getElementById("generateButton");


    result.style.display = "none";

    loading.style.display = "block";

    button.disabled = true;


    try {

        const response =
            await fetch("/api/start", {

                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({

                    mood: selectedMood,

                    activity: selectedActivity

                })

            });


        const data =
            await response.json();


        if (!data.success) {

            throw new Error(
                data.message ||
                "Something went wrong."
            );

        }


        result.textContent =
            data.response;

        result.style.display =
            "block";


        result.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });


    } catch (error) {

        result.textContent =
            "💙 Something went wrong. Please try again.";

        result.style.display =
            "block";

        console.error(error);

    } finally {

        loading.style.display =
            "none";

        updateButton();

    }

}

</script>

</body>

</html>
"""


# ============================================================
# LOCAL DEVELOPMENT
# ============================================================

if __name__ == "__main__":

    import uvicorn

    port = int(os.getenv("PORT", "8000"))

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port
    )
