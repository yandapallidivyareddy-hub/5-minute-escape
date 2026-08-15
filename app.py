import os
import random
import re

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="5-Minute Escape AI",
    description="An interactive AI escape adventure for students",
    version="1.0.0"
)


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GOOGLE_API_KEY or GEMINI_API_KEY is not configured in Render."
    )


MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-3-flash-preview"
)


llm = ChatGoogleGenerativeAI(
    model=MODEL_NAME,
    google_api_key=API_KEY,
    temperature=0.9,
    max_output_tokens=1200
)


# ============================================================
# REQUEST MODEL
# ============================================================

class EscapeRequest(BaseModel):
    mood: str
    world: str


class ContinueRequest(BaseModel):
    mood: str
    world: str
    story: str
    choice: str
    turn: int


# ============================================================
# HELPERS
# ============================================================

def clean_text(text):

    if not text:
        return "✨ The magical world is quiet for a moment. Try again."

    # Handle Gemini content blocks
    if isinstance(text, list):

        parts = []

        for item in text:

            if isinstance(item, dict):

                if item.get("type") == "text":
                    parts.append(item.get("text", ""))

            elif isinstance(item, str):
                parts.append(item)

        text = "\n".join(parts)

    text = str(text)

    # Remove accidental code blocks
    text = re.sub(
        r"```.*?```",
        "",
        text,
        flags=re.DOTALL
    )

    # Remove unnecessary labels
    text = re.sub(
        r"^(story|response|answer)\s*:\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    # Clean excessive blank lines
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()


# ============================================================
# INITIAL ADVENTURE
# ============================================================

def create_escape(mood, world):

    prompt = f"""
You are the narrator of a short, peaceful, magical interactive
adventure called "5-Minute Escape AI".

The student currently feels:
{mood}

The student has entered:
{world}

Create the opening scene of the adventure.

IMPORTANT:

- Use simple, friendly English.
- Make it imaginative and comforting.
- Make it feel like a small escape from everyday student life.
- Do not mention therapy, diagnosis, mental illness, or treatment.
- Do not give medical advice.
- Do not mention AI.
- Do not generate images.
- Use emojis naturally.
- Do not make the story frightening.
- Avoid violence.
- Keep the atmosphere warm, magical and relaxing.
- Write approximately 250-350 words.
- End with EXACTLY three choices.
- Each choice must be clearly labelled A, B and C.
- The choices should lead to different story directions.

Format:

🌌 [Adventure Title]

[Opening scene]

✨ What will you do?

🅰️ [Choice A]
🅱️ [Choice B]
🅲️ [Choice C]
"""

    response = llm.invoke(prompt)

    return clean_text(response.content)


# ============================================================
# CONTINUE ADVENTURE
# ============================================================

def continue_escape(mood, world, story, choice, turn):

    prompt = f"""
You are continuing an interactive magical adventure.

Adventure world:
{world}

Student mood at the beginning:
{mood}

The adventure so far:
{story}

The student chose:
{choice}

This is adventure turn:
{turn}

Continue the story based on the student's choice.

IMPORTANT:

- Use simple English.
- Be creative and surprising.
- Keep the story peaceful, positive and playful.
- Make the student feel like they are inside the adventure.
- Use emojis naturally.
- No images.
- No image prompts.
- No AI references.
- No therapy or medical advice.
- No violence.
- Keep the story suitable for students.
- Write approximately 180-280 words.

If this is turn 4 or later:

END the adventure naturally.

Give the student a peaceful conclusion and include:

🌅 Your escape is complete.

Take a small breath.
Look around you.
You are back in the real world.

✨ Welcome back!

Otherwise, end with EXACTLY three new choices:

✨ What will you do next?

🅰️ [Choice A]
🅱️ [Choice B]
🅲️ [Choice C]
"""

    response = llm.invoke(prompt)

    return clean_text(response.content)


# ============================================================
# API ROUTES
# ============================================================

@app.get("/", response_class=HTMLResponse)
def home():

    return HTML_PAGE


@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "5-Minute Escape AI",
        "model": MODEL_NAME
    }


@app.post("/start")
def start_escape(request: EscapeRequest):

    try:

        story = create_escape(
            request.mood,
            request.world
        )

        return {
            "success": True,
            "story": story,
            "turn": 1
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


@app.post("/continue")
def continue_adventure(request: ContinueRequest):

    try:

        new_story = continue_escape(
            request.mood,
            request.world,
            request.story,
            request.choice,
            request.turn
        )

        return {
            "success": True,
            "story": new_story,
            "turn": request.turn + 1
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


# ============================================================
# FRONTEND
# ============================================================

HTML_PAGE = r"""
<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width, initial-scale=1.0">

<title>5-Minute Escape AI</title>


<style>

* {
    box-sizing: border-box;
}


body {

    margin: 0;

    min-height: 100vh;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    background:
        radial-gradient(
            circle at top,
            #17366b,
            #07152f 55%,
            #030b1c
        );

    color: white;

    padding: 25px 15px;

}


.container {

    width: 100%;

    max-width: 900px;

    margin: auto;

}


.header {

    text-align: center;

    padding: 20px 0 30px;

}


.logo {

    font-size: 52px;

}


h1 {

    margin: 8px 0;

    font-size: 42px;

    color: #ffd43b;

}


.subtitle {

    color: #c9d8f2;

    font-size: 17px;

    line-height: 1.6;

}


.card {

    background:
        rgba(255,255,255,0.08);

    border:
        1px solid rgba(255,255,255,0.15);

    border-radius: 24px;

    padding: 30px;

    margin-bottom: 25px;

    backdrop-filter: blur(15px);

    box-shadow:
        0 20px 50px rgba(0,0,0,0.3);

}


.section-title {

    font-size: 20px;

    font-weight: bold;

    color: #ffd43b;

    margin-bottom: 15px;

}


.options {

    display: grid;

    grid-template-columns:
        repeat(2, 1fr);

    gap: 12px;

    margin-bottom: 25px;

}


.option {

    padding: 16px;

    border-radius: 14px;

    border:
        1px solid rgba(255,255,255,0.15);

    background:
        rgba(255,255,255,0.06);

    color: white;

    cursor: pointer;

    font-size: 16px;

    transition: 0.2s;

}


.option:hover {

    transform: translateY(-2px);

    background:
        rgba(255,212,59,0.15);

}


.option.selected {

    background: #ffd43b;

    color: #07152f;

    border-color: #ffd43b;

    font-weight: bold;

}


.start-btn {

    width: 100%;

    padding: 17px;

    border: none;

    border-radius: 14px;

    background: #ffd43b;

    color: #07152f;

    font-size: 18px;

    font-weight: bold;

    cursor: pointer;

    transition: 0.2s;

}


.start-btn:hover {

    transform: translateY(-2px);

    box-shadow:
        0 8px 25px rgba(255,212,59,0.3);

}


.start-btn:disabled {

    opacity: 0.6;

    cursor: wait;

}


.adventure {

    display: none;

    background: #fffdf6;

    color: #263238;

    border-radius: 24px;

    padding: 35px;

    box-shadow:
        0 20px 60px rgba(0,0,0,0.4);

}


.adventure-title {

    text-align: center;

    color: #102d5c;

    font-size: 26px;

    margin-bottom: 20px;

}


.story {

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 18px;

    line-height: 1.9;

    white-space: pre-wrap;

}


.choice-area {

    margin-top: 25px;

    display: grid;

    gap: 12px;

}


.choice {

    padding: 15px;

    border-radius: 13px;

    border: 2px solid #d9c55a;

    background: #fff9d8;

    color: #102d5c;

    font-size: 16px;

    font-weight: bold;

    cursor: pointer;

    text-align: left;

    transition: 0.2s;

}


.choice:hover {

    background: #ffe979;

    transform: translateX(3px);

}


.loading {

    display: none;

    text-align: center;

    color: #ffd43b;

    margin-top: 15px;

    font-weight: bold;

}


.error {

    display: none;

    margin-top: 15px;

    background: #641f2a;

    padding: 12px;

    border-radius: 10px;

    color: #ffd8dd;

}


.restart {

    display: none;

    margin-top: 25px;

    width: 100%;

    padding: 14px;

    border: none;

    border-radius: 12px;

    background: #102d5c;

    color: white;

    cursor: pointer;

    font-weight: bold;

}


.footer {

    text-align: center;

    color: #91a8cc;

    padding: 15px;

    font-size: 14px;

}


@media(max-width:600px) {

    h1 {
        font-size: 32px;
    }

    .options {
        grid-template-columns: 1fr;
    }

    .card {
        padding: 20px;
    }

    .adventure {
        padding: 22px;
    }

    .story {
        font-size: 17px;
    }

}

</style>

</head>


<body>


<div class="container">


    <div class="header">

        <div class="logo">
            🌌✨
        </div>

        <h1>
            5-Minute Escape
        </h1>

        <div class="subtitle">
            Take a tiny break from your busy day.
            <br>
            Choose a world. Make a choice. Escape for a few minutes. 🌿
        </div>

    </div>


    <!-- SETUP -->

    <div
        class="card"
        id="setup"
    >

        <div class="section-title">
            🌈 How are you feeling?
        </div>


        <div class="options">

            <button
                class="option mood"
                onclick="selectMood(this,'Stressed')"
            >
                😫 Stressed
            </button>

            <button
                class="option mood"
                onclick="selectMood(this,'Tired')"
            >
                😴 Tired
            </button>

            <button
                class="option mood"
                onclick="selectMood(this,'Sad')"
            >
                😔 Sad
            </button>

            <button
                class="option mood"
                onclick="selectMood(this,'Bored')"
            >
                😐 Bored
            </button>

            <button
                class="option mood"
                onclick="selectMood(this,'Overwhelmed')"
            >
                😵 Overwhelmed
            </button>

            <button
                class="option mood"
                onclick="selectMood(this,'Happy')"
            >
                😄 Happy
            </button>

        </div>


        <div class="section-title">
            🌌 Where would you like to escape?
        </div>


        <div class="options">

            <button
                class="option world"
                onclick="selectWorld(this,'Enchanted Forest')"
            >
                🌲 Enchanted Forest
            </button>

            <button
                class="option world"
                onclick="selectWorld(this,'Secret Island')"
            >
                🏝️ Secret Island
            </button>

            <button
                class="option world"
                onclick="selectWorld(this,'Space Station')"
            >
                🚀 Space Station
            </button>

            <button
                class="option world"
                onclick="selectWorld(this,'Magical Kingdom')"
            >
                🏰 Magical Kingdom
            </button>

            <button
                class="option world"
                onclick="selectWorld(this,'Dragon Valley')"
            >
                🐉 Dragon Valley
            </button>

            <button
                class="option world"
                onclick="selectWorld(this,'Underwater City')"
            >
                🌊 Underwater City
            </button>

        </div>


        <button
            class="start-btn"
            id="startBtn"
            onclick="startEscape()"
        >
            ✨ Start My Escape
        </button>


        <div
            class="loading"
            id="loading"
        >
            🌌 Opening a magical world...
        </div>


        <div
            class="error"
            id="error"
        ></div>

    </div>


    <!-- ADVENTURE -->

    <div
        class="adventure"
        id="adventure"
    >

        <div class="adventure-title">
            🌌 Your 5-Minute Escape
        </div>


        <div
            class="story"
            id="story"
        ></div>


        <div
            class="choice-area"
            id="choices"
        ></div>


        <button
            class="restart"
            id="restart"
            onclick="restartEscape()"
        >
            🔄 Start Another Escape
        </button>

    </div>


    <div class="footer">
        🌿 5-Minute Escape AI • A tiny break for a busy mind ✨
    </div>


</div>


<script>

let selectedMood = "";

let selectedWorld = "";

let currentStory = "";

let currentTurn = 1;


function selectMood(button, mood) {

    document
        .querySelectorAll(".mood")
        .forEach(btn => {
            btn.classList.remove("selected");
        });

    button.classList.add("selected");

    selectedMood = mood;
}


function selectWorld(button, world) {

    document
        .querySelectorAll(".world")
        .forEach(btn => {
            btn.classList.remove("selected");
        });

    button.classList.add("selected");

    selectedWorld = world;
}


async function startEscape() {

    const error =
        document.getElementById("error");

    const loading =
        document.getElementById("loading");

    const button =
        document.getElementById("startBtn");


    error.style.display = "none";


    if (!selectedMood) {

        error.style.display = "block";

        error.textContent =
            "🌈 Please choose how you are feeling.";

        return;
    }


    if (!selectedWorld) {

        error.style.display = "block";

        error.textContent =
            "🌌 Please choose an escape world.";

        return;
    }


    button.disabled = true;

    loading.style.display = "block";


    try {

        const response =
            await fetch("/start", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    mood: selectedMood,

                    world: selectedWorld

                })

            });


        const data =
            await response.json();


        if (!data.success) {

            throw new Error(
                data.error ||
                "Could not start the escape."
            );

        }


        currentStory =
            data.story;

        currentTurn =
            data.turn;


        showAdventure(
            currentStory
        );

    }

    catch (err) {

        error.style.display = "block";

        error.textContent =
            "❌ " + err.message;

    }

    finally {

        button.disabled = false;

        loading.style.display = "none";

    }

}


function showAdventure(text) {

    document.getElementById(
        "setup"
    ).style.display = "none";


    document.getElementById(
        "adventure"
    ).style.display = "block";


    document.getElementById(
        "story"
    ).textContent = text;


    createChoices(text);


    document
        .getElementById("adventure")
        .scrollIntoView({
            behavior: "smooth"
        });

}


function createChoices(text) {

    const choiceArea =
        document.getElementById("choices");


    choiceArea.innerHTML = "";


    const hasA =
        /🅰️/u.test(text);

    const hasB =
        /🅱️/u.test(text);

    const hasC =
        /🅲️/u.test(text);


    if (!hasA || !hasB || !hasC) {

        document.getElementById(
            "restart"
        ).style.display = "block";

        return;

    }


    const choices = extractChoices(text);


    choices.forEach(choice => {

        const button =
            document.createElement("button");

        button.className = "choice";

        button.textContent =
            choice.label + " " + choice.text;

        button.onclick =
            () => chooseOption(
                choice.text
            );

        choiceArea.appendChild(button);

    });

}


function extractChoices(text) {

    const choices = [];


    const patterns = [

        /🅰️\s*(.+)/u,

        /🅱️\s*(.+)/u,

        /🅲️\s*(.+)/u

    ];


    const labels = [
        "🅰️",
        "🅱️",
        "🅲️"
    ];


    patterns.forEach(
        (pattern, index) => {

            const match =
                text.match(pattern);

            if (match) {

                choices.push({

                    label: labels[index],

                    text:
                        match[1]
                            .trim()
                            .split("\n")[0]

                });

            }

        }
    );


    return choices;

}


async function chooseOption(choice) {

    const choiceArea =
        document.getElementById("choices");


    choiceArea.innerHTML =
        '<div class="loading" style="display:block;">✨ Your choice is opening a new path...</div>';


    try {

        const response =
            await fetch("/continue", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    mood: selectedMood,

                    world: selectedWorld,

                    story: currentStory,

                    choice: choice,

                    turn: currentTurn

                })

            });


        const data =
            await response.json();


        if (!data.success) {

            throw new Error(
                data.error ||
                "Could not continue the adventure."
            );

        }


        currentStory +=
            "\n\n" + data.story;

        currentTurn =
            data.turn;


        document.getElementById(
            "story"
        ).textContent =
            currentStory;


        createChoices(
            data.story
        );


        document
            .getElementById("story")
            .scrollIntoView({
                behavior: "smooth"
            });

    }

    catch (err) {

        choiceArea.innerHTML =
            '<div class="error" style="display:block;">❌ '
            + err.message +
            '</div>';

    }

}


function restartEscape() {

    selectedMood = "";

    selectedWorld = "";

    currentStory = "";

    currentTurn = 1;


    document.getElementById(
        "adventure"
    ).style.display = "none";


    document.getElementById(
        "setup"
    ).style.display = "block";


    document.querySelectorAll(
        ".option"
    ).forEach(btn => {

        btn.classList.remove(
            "selected"
        );

    });


    document.getElementById(
        "restart"
    ).style.display = "none";


    window.scrollTo({

        top: 0,

        behavior: "smooth"

    });

}

</script>

</body>

</html>
"""
