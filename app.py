import os
import random
import html
from typing import Optional

import requests
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="MindMate AI",
    description="A fun AI-powered stress-buster for students",
    version="2.0"
)


# ============================================================
# CONFIGURATION
# ============================================================

WATCHMODE_API_KEY = os.getenv("WATCHMODE_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


# ============================================================
# SESSION MEMORY
# Keeps results from repeating during a session.
# ============================================================

session_history = {
    "jokes": set(),
    "movies": set(),
    "activities": set(),
    "facts": set(),
}


# ============================================================
# REQUEST MODEL
# ============================================================

class ActionRequest(BaseModel):
    action: str
    mood: Optional[str] = "Okay"


# ============================================================
# BUILT-IN CONTENT
# ============================================================

ACTIVITIES = [

    {
        "type": "would_you_rather",
        "title": "🤔 Would You Rather?",
        "text": "Would you rather have unlimited snacks 🍕 or unlimited sleep 😴?",
        "buttons": ["🍕 Snacks", "😴 Sleep"]
    },

    {
        "type": "would_you_rather",
        "title": "🤔 Quick Choice",
        "text": "Would you rather explore space 🚀 or explore the deep ocean 🌊?",
        "buttons": ["🚀 Space", "🌊 Ocean"]
    },

    {
        "type": "challenge",
        "title": "🎯 30-Second Challenge",
        "text": "Look around you and find 3 things that are blue. 🔵",
        "buttons": ["✅ Done!"]
    },

    {
        "type": "challenge",
        "title": "😄 Smile Challenge",
        "text": "Smile for 10 seconds. Yes, seriously! 😄",
        "buttons": ["😄 I did it!"]
    },

    {
        "type": "challenge",
        "title": "🧘 Mini Reset",
        "text": "Put your phone down for 30 seconds and take 3 slow breaths. 🌿",
        "buttons": ["🌿 Done"]
    },

    {
        "type": "challenge",
        "title": "🎵 Tiny Dance Break",
        "text": "Play your favorite song and move for 30 seconds. Nobody is judging! 💃🕺",
        "buttons": ["🎶 Let's go!"]
    },

    {
        "type": "riddle",
        "title": "🧩 Quick Riddle",
        "text": "What has many keys but cannot open a single door?",
        "answer": "🎹 A piano",
        "buttons": ["💡 Show Answer"]
    },

    {
        "type": "riddle",
        "title": "🧩 Another Riddle",
        "text": "What gets wetter the more it dries?",
        "answer": "🧻 A towel",
        "buttons": ["💡 Show Answer"]
    },

    {
        "type": "compliment",
        "title": "💙 A Little Reminder",
        "text": "You don't have to have everything figured out today. You're doing better than you think. 🌱",
        "buttons": ["💙 Thank you"]
    },

    {
        "type": "compliment",
        "title": "✨ Just For You",
        "text": "Progress does not have to be huge. Even a tiny step counts. 🌟",
        "buttons": ["🌟 Keep Going"]
    },

    {
        "type": "fun",
        "title": "😂 Imagine This",
        "text": "Imagine your professor accidentally says 'Alexa, next slide' during class. 😂",
        "buttons": ["😂 That would be funny"]
    },

    {
        "type": "fun",
        "title": "🤣 Student Life",
        "text": "POV: You open your laptop to study and somehow end up watching 17 random videos. 😭😂",
        "buttons": ["😂 Too real"]
    },

]


FACTS = [
    "🐙 Octopuses have three hearts.",
    "🍌 Bananas are technically berries!",
    "🦋 Butterflies taste with their feet.",
    "🌈 Rainbows are actually full circles, but we usually see only part of them.",
    "🐧 Penguins can recognize individual voices.",
    "🌙 A day on Venus is longer than its year.",
    "🧠 Your brain is constantly working, even while you sleep.",
    "🐝 Bees can recognize human faces.",
    "🦒 Giraffes have the same number of neck bones as humans: seven.",
    "🌊 The ocean covers more than 70% of Earth's surface.",
]


# ============================================================
# HELPERS
# ============================================================

def get_new_item(items, used_set, key_func=lambda x: x):

    available = [
        item for item in items
        if key_func(item) not in used_set
    ]

    if not available:
        used_set.clear()
        available = items

    item = random.choice(available)
    used_set.add(key_func(item))

    return item


def clean_text(text: str) -> str:
    return html.escape(str(text or ""))


# ============================================================
# JOKE API
# ============================================================

def get_joke():

    try:

        url = (
            "https://v2.jokeapi.dev/joke/"
            "Misc,Pun,Programming"
            "?safe-mode"
            "&type=single,twopart"
            "&blacklistFlags=nsfw,religious,political,racist,sexist,explicit"
        )

        response = requests.get(
            url,
            timeout=8
        )

        response.raise_for_status()

        data = response.json()

        if data.get("error"):
            raise Exception("Joke API returned an error")

        joke_id = data.get("id")

        # Prevent duplicate jokes
        if joke_id in session_history["jokes"]:

            for _ in range(3):

                response = requests.get(
                    url,
                    timeout=8
                )

                data = response.json()

                joke_id = data.get("id")

                if joke_id not in session_history["jokes"]:
                    break

        session_history["jokes"].add(joke_id)

        if data.get("type") == "single":

            return {
                "title": "😂 Here's something funny!",
                "content": data.get("joke", "Why did the computer go to the doctor? It had a virus! 😂"),
                "emoji": "😂"
            }

        return {
            "title": "😂 Wait for it...",
            "content": (
                data.get("setup", "")
                + "\n\n"
                + data.get("delivery", "")
            ),
            "emoji": "🤣"
        }

    except Exception:

        # Fallback jokes
        fallback = [
            "Why did the student eat his homework? Because the teacher said it was a piece of cake! 🍰😂",
            "My laptop and I have a relationship. It gives me problems, and I keep coming back. 💻😂",
            "Why was the math book sad? It had too many problems. 📚😂",
            "I told my computer I needed a break... now it won't stop sending me vacation ads. 😂",
        ]

        joke = get_new_item(
            fallback,
            session_history["jokes"]
        )

        return {
            "title": "😂 Quick Laugh",
            "content": joke,
            "emoji": "😂"
        }


# ============================================================
# WATCHMODE MOVIES
# ============================================================

def get_movies():

    if not WATCHMODE_API_KEY:
        return {
            "title": "🎬 Movie Break",
            "content": (
                "Movie recommendations are not configured yet. "
                "Please add WATCHMODE_API_KEY in Render Environment Variables. 🍿"
            ),
            "movies": []
        }

    try:

        response = requests.get(
            "https://api.watchmode.com/v1/list-titles/",
            params={
                "apiKey": WATCHMODE_API_KEY,
                "types": "movie",
                "source_ids": "203",     # Netflix
                "regions": "IN",
                "sort_by": "popularity_desc",
                "limit": 20
            },
            timeout=10
        )

        response.raise_for_status()
        data = response.json()

        movies = []

        for movie in data.get("titles", []):

            movie_id = movie.get("id")

            if not movie_id:
                continue

            if movie_id in session_history["movies"]:
                continue

            session_history["movies"].add(movie_id)

            movies.append({
                "id": movie_id,
                "title": movie.get("title", "Unknown Movie"),
                "overview": movie.get(
                    "plot_overview",
                    "A movie worth checking out! 🍿"
                ),
                "rating": movie.get("user_rating", "N/A"),
                "release_date": movie.get("release_date", ""),
                "poster": movie.get("poster", "")
            })

            if len(movies) >= 4:
                break

        return {
            "title": "🎬 Movie Break",
            "content": "Here are some trending Netflix movies for your break! 🍿✨",
            "movies": movies
        }

    except requests.exceptions.Timeout:
        return {
            "title": "🎬 Movie Break",
            "content": "The movie service took too long to respond. Try again! ⏳",
            "movies": []
        }

    except requests.exceptions.RequestException:
        return {
            "title": "🎬 Movie Break",
            "content": "Couldn't connect to Watchmode right now. 🎬",
            "movies": []
        }

    except Exception as e:
        return {
            "title": "🎬 Movie Break",
            "content": f"Error: {str(e)}",
            "movies": []
        }
# ============================================================
# FUN FACT
# ============================================================

def get_fact():

    fact = get_new_item(
        FACTS,
        session_history["facts"]
    )

    return {
        "title": "🧠 Did You Know?",
        "content": fact,
        "emoji": "🧠"
    }


# ============================================================
# RANDOM ACTIVITY
# ============================================================

def get_activity():

    activity = get_new_item(
        ACTIVITIES,
        session_history["activities"],
        key_func=lambda x: x["text"]
    )

    return activity


# ============================================================
# GEMINI (MindMate)
# ============================================================

def ask_gemini(mood: str):

    if not GOOGLE_API_KEY:
        return {
            "title": "💙 MindMate",
            "content": "Please configure GOOGLE_API_KEY in Render."
        }

    try:
        from google import genai

        client = genai.Client(api_key=GOOGLE_API_KEY)

        prompt = f"""
You are MindMate, a friendly AI companion for students.

The student's mood is: {mood}

Respond in under 80 words.
- Be warm and positive
- Use simple English
- Give one small practical suggestion
- Use 2–4 emojis
- Do not sound like a therapist
"""

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        return {
            "title": "💙 MindMate Says",
            "content": response.text.strip()
        }

    except Exception as e:
        return {
            "title": "💙 MindMate",
            "content": f"Gemini error: {str(e)}"
        }

# ============================================================
# API
# ============================================================

@app.get("/")
def home():

    return HTMLResponse(HTML_PAGE)


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "watchmode_configured": bool(WATCHMODE_API_KEY),
        "google_configured": bool(GOOGLE_API_KEY)
    }


@app.post("/api/action")
def action(request: ActionRequest):

    action_name = request.action.lower().strip()

    if action_name == "joke":

        return JSONResponse(
            get_joke()
        )

    if action_name == "movie":

        return JSONResponse(
            get_movies()
        )

    if action_name == "activity":

        return JSONResponse(
            get_activity()
        )

    if action_name == "fact":

        return JSONResponse(
            get_fact()
        )

    if action_name == "talk":

        return JSONResponse(
            ask_gemini(request.mood)
        )

    if action_name == "surprise":

        choices = [
            "joke",
            "movie",
            "activity",
            "fact"
        ]

        selected = random.choice(choices)

        if selected == "joke":
            return JSONResponse(get_joke())

        if selected == "movie":
            return JSONResponse(get_movies())

        if selected == "fact":
            return JSONResponse(get_fact())

        return JSONResponse(get_activity())

    return JSONResponse(
        {
            "title": "🌱 MindMate",
            "content": "Let's take a tiny break together. 💙"
        }
    )


# ============================================================
# FRONTEND
# ============================================================

HTML_PAGE = """
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
        Arial,
        sans-serif;

    background:
        linear-gradient(
            135deg,
            #eef8ff,
            #f8f5ff
        );

    color: #17233c;

    min-height: 100vh;
}

.container {

    width: min(1050px, 94%);

    margin: auto;

    padding: 35px 0 50px;
}

.hero {

    text-align: center;

    margin-bottom: 30px;
}

.logo {

    font-size: 54px;
}

h1 {

    margin: 5px 0;

    font-size: 42px;

    color: #123b73;
}

.subtitle {

    font-size: 18px;

    color: #63708a;
}

.mood-section {

    background: white;

    padding: 25px;

    border-radius: 24px;

    box-shadow:
        0 10px 35px rgba(30, 60, 100, 0.08);

    margin-bottom: 25px;
}

.mood-title {

    text-align: center;

    font-size: 20px;

    font-weight: 700;

    margin-bottom: 18px;
}

.moods {

    display: flex;

    flex-wrap: wrap;

    justify-content: center;

    gap: 10px;
}

.mood {

    border: 2px solid #e4eaf5;

    background: #fff;

    border-radius: 30px;

    padding: 11px 17px;

    cursor: pointer;

    font-size: 14px;

    transition: 0.2s;
}

.mood:hover {

    transform: translateY(-2px);

    border-color: #5d8fe8;

    background: #f3f7ff;
}

.mood.selected {

    background: #123b73;

    color: white;

    border-color: #123b73;
}

.actions {

    display: grid;

    grid-template-columns:
        repeat(
            auto-fit,
            minmax(190px, 1fr)
        );

    gap: 15px;

    margin-top: 25px;
}

.action {

    border: none;

    border-radius: 20px;

    padding: 22px 15px;

    cursor: pointer;

    background: white;

    box-shadow:
        0 8px 25px rgba(30, 60, 100, 0.08);

    transition: 0.2s;

    color: #17233c;
}

.action:hover {

    transform: translateY(-5px);

    box-shadow:
        0 14px 35px rgba(30, 60, 100, 0.14);
}

.action .icon {

    font-size: 34px;

    display: block;

    margin-bottom: 8px;
}

.action strong {

    display: block;

    font-size: 17px;
}

.action span {

    display: block;

    color: #7a8497;

    margin-top: 5px;
}

.result-area {

    margin-top: 28px;
}

.empty {

    text-align: center;

    padding: 40px;

    color: #7c879a;
}

.card {

    background: white;

    border-radius: 25px;

    padding: 30px;

    box-shadow:
        0 15px 45px rgba(30, 60, 100, 0.10);

    animation:
        appear 0.35s ease;
}

@keyframes appear {

    from {
        opacity: 0;
        transform: translateY(12px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.card-title {

    font-size: 26px;

    font-weight: 800;

    color: #123b73;

    margin-bottom: 15px;
}

.card-content {

    white-space: pre-line;

    line-height: 1.7;

    font-size: 17px;

    color: #455168;
}

.next {

    margin-top: 22px;

    display: flex;

    flex-wrap: wrap;

    gap: 10px;
}

.next button {

    border: none;

    padding: 12px 18px;

    border-radius: 14px;

    background: #123b73;

    color: white;

    cursor: pointer;

    font-weight: 600;
}

.next button:hover {

    background: #0c2d5a;
}

.movies {

    display: grid;

    grid-template-columns:
        repeat(
            auto-fit,
            minmax(190px, 1fr)
        );

    gap: 18px;

    margin-top: 20px;
}

.movie {

    border: 1px solid #e8edf5;

    border-radius: 18px;

    overflow: hidden;

    background: #fafcff;
}

.movie img {

    width: 100%;

    height: 270px;

    object-fit: cover;

    background: #edf1f7;
}

.movie-body {

    padding: 15px;
}

.movie-title {

    font-weight: 800;

    font-size: 17px;

    margin-bottom: 6px;
}

.rating {

    color: #d18a00;

    font-weight: 700;

    margin-bottom: 8px;
}

.movie-overview {

    font-size: 13px;

    line-height: 1.5;

    color: #667085;
}

.loading {

    text-align: center;

    padding: 35px;

    font-size: 18px;

    color: #64748b;
}

.footer {

    text-align: center;

    margin-top: 40px;

    color: #8290a5;

    font-size: 14px;
}

@media(max-width:600px) {

    h1 {
        font-size: 32px;
    }

    .container {
        padding-top: 20px;
    }

    .card {
        padding: 22px;
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
        </div>

        <div class="subtitle">
            Take a tiny break. You deserve it.
        </div>

    </div>


    <div class="mood-section">

        <div class="mood-title">
            😊 How are you feeling right now?
        </div>

        <div class="moods">

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


    <div class="actions">

        <button class="action"
                onclick="runAction('joke')">

            <span class="icon">😂</span>

            <strong>Make Me Laugh</strong>

            <span>Give me a fresh joke</span>

        </button>


        <button class="action"
                onclick="runAction('movie')">

            <span class="icon">🎬</span>

            <strong>Movie Break</strong>

            <span>Show me something to watch</span>

        </button>


        <button class="action"
                onclick="runAction('activity')">

            <span class="icon">🎮</span>

            <strong>Play Something</strong>

            <span>Try a tiny fun activity</span>

        </button>


        <button class="action"
                onclick="runAction('fact')">

            <span class="icon">🧠</span>

            <strong>Surprise Fact</strong>

            <span>Teach me something cool</span>

        </button>


        <button class="action"
                onclick="runAction('talk')">

            <span class="icon">💙</span>

            <strong>Talk to MindMate</strong>

            <span>I just need a little support</span>

        </button>


        <button class="action"
                onclick="runAction('surprise')">

            <span class="icon">✨</span>

            <strong>Surprise Me</strong>

            <span>I don't know what I want!</span>

        </button>

    </div>


    <div id="result"
         class="result-area">

        <div class="card empty">

            🌱

            <h3>
                Your break starts here.
            </h3>

            <p>
                Choose anything above and let's make
                the next few minutes a little better. 💙
            </p>

        </div>

    </div>


    <div class="footer">

        🌱 MindMate AI • A small break can make a big difference 💙

    </div>

</div>


<script>

let selectedMood = "Okay";


function selectMood(button, mood) {

    document
        .querySelectorAll(".mood")
        .forEach(
            item => item.classList.remove("selected")
        );

    button.classList.add("selected");

    selectedMood = mood;
}


async function runAction(action) {

    const result =
        document.getElementById("result");

    result.innerHTML = `
        <div class="card loading">
            ✨ Finding something nice for you...
        </div>
    `;

    try {

        const response = await fetch(
            "/api/action",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    action: action,
                    mood: selectedMood
                })
            }
        );

        const data = await response.json();

        renderResult(data, action);

    }

    catch (error) {

        result.innerHTML = `
            <div class="card">
                <div class="card-title">
                    😅 Oops!
                </div>

                <div class="card-content">
                    Something went wrong.
                    Please try again. 💙
                </div>

                <div class="next">

                    <button onclick="runAction('${action}')">
                        🔄 Try Again
                    </button>

                </div>
            </div>
        `;
    }
}


function renderResult(data, action) {

    const result =
        document.getElementById("result");


    let movieHTML = "";


    if (data.movies && data.movies.length) {

        movieHTML = `
            <div class="movies">

                ${data.movies.map(movie => `

                    <div class="movie">

                        ${
                            movie.poster
                            ?
                            `<img
                                src="${movie.poster}"
                                alt="${escapeHtml(movie.title)}"
                              >`
                            :
                            `<div
                                style="
                                height:270px;
                                display:flex;
                                align-items:center;
                                justify-content:center;
                                font-size:50px;
                                "
                            >
                                🎬
                            </div>`
                        }

                        <div class="movie-body">

                            <div class="movie-title">
                                ${escapeHtml(movie.title)}
                            </div>

                            <div class="rating">
                                ⭐ ${movie.rating}
                            </div>

                            <div class="movie-overview">
                                ${escapeHtml(movie.overview)}
                            </div>

                        </div>

                    </div>

                `).join("")}

            </div>
        `;
    }


    let activityButtons = "";

    if (data.buttons) {

        activityButtons = `
            <div class="next">

                ${data.buttons.map(
                    button => `
                        <button
                            onclick="alert('🎉 Nice! Keep going!')">
                            ${escapeHtml(button)}
                        </button>
                    `
                ).join("")}

            </div>
        `;
    }


    result.innerHTML = `

        <div class="card">

            <div class="card-title">

                ${data.title || "🌱 MindMate"}

            </div>

            <div class="card-content">

                ${escapeHtml(
                    data.content || data.text || ""
                )}

            </div>

            ${movieHTML}

            ${data.answer ? `
                <div
                    id="answer"
                    style="
                    display:none;
                    margin-top:15px;
                    font-weight:700;
                    font-size:18px;
                    color:#123b73;
                    "
                >
                    ${escapeHtml(data.answer)}
                </div>
            ` : ""}

            ${activityButtons}

            <div class="next">

                ${
                    data.answer
                    ?
                    `<button
                        onclick="showAnswer()">
                        💡 Show Answer
                    </button>`
                    :
                    ""
                }

                <button
                    onclick="runAction('${action}')">
                    🔄 Give Me Another
                </button>

                <button
                    onclick="runAction('surprise')">
                    ✨ Surprise Me
                </button>

            </div>

        </div>

    `;
}


function showAnswer() {

    const answer =
        document.getElementById("answer");

    if (answer) {

        answer.style.display = "block";

    }
}


function escapeHtml(text) {

    const div =
        document.createElement("div");

    div.textContent =
        text || "";

    return div.innerHTML;
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

    port = int(
        os.getenv("PORT", "8000")
    )

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port
    )
