import os
import re
from pathlib import Path

from flask import (
    Flask,
    render_template,
    request,
    session,
    redirect,
    url_for
)

from PIL import Image, ImageEnhance, ImageFilter


# ============================================================
# FLASK SETUP
# ============================================================

app = Flask(__name__)

app.secret_key = "chatlens-local-development-key"

app.config["MAX_CONTENT_LENGTH"] = 30 * 1024 * 1024









# ============================================================
# CLEAN MESSAGES
# ============================================================

def clean_messages(messages):

    cleaned = []

    seen = set()


    for message in messages:

        sender = str(
            message.get(
                "sender",
                "Unknown"
            )
        ).strip()


        text = str(
            message.get(
                "text",
                ""
            )
        ).strip()


        timestamp = str(
            message.get(
                "timestamp",
                ""
            )
        ).strip()


        if not text:

            continue


        key = (

            sender.casefold(),

            text.casefold(),

            timestamp

        )


        if key in seen:

            continue


        seen.add(key)


        cleaned.append({

            "sender": sender,

            "text": text,

            "timestamp": timestamp

        })


    return cleaned


# ============================================================
# TEXT CHAT PARSER
# ============================================================

WHATSAPP_PATTERN = re.compile(
    r"^\s*\[([^\]]+)\]\s*([^:]+):\s*(.*)$"
)


COMMON_PATTERN = re.compile(
    r"^\s*(?:\[([^\]]+)\]\s*)?([^:]+):\s*(.*)$"
)


def parse_text_chat(chat):

    messages = []

    current = None


    for raw_line in chat.splitlines():

        line = raw_line.strip()


        if not line:

            continue


        match = (
            WHATSAPP_PATTERN.match(line)
            or
            COMMON_PATTERN.match(line)
        )


        if match:

            timestamp = (
                match.group(1)
                or
                ""
            )


            sender = (
                match.group(2)
                .strip()
            )


            text = (
                match.group(3)
                .strip()
            )


            # Avoid treating huge text blocks
            # as sender names.

            if len(sender) > 80:

                if current:

                    current["text"] += (
                        "\n"
                        +
                        line
                    )

                continue


            if current:

                messages.append(
                    current
                )


            current = {

                "sender": sender,

                "text": text,

                "timestamp": timestamp

            }


        else:

            if current:

                current["text"] += (
                    "\n"
                    +
                    line
                )

            else:

                messages.append({

                    "sender": "Unknown",

                    "text": line,

                    "timestamp": ""

                })


    if current:

        messages.append(
            current
        )


    return clean_messages(
        messages
    )


# ============================================================
# ANALYSIS
# ============================================================

def analyze_chat(
    messages,
    user_sender
):

    user_messages = [

        message

        for message in messages

        if message["sender"]
        == user_sender

    ]


    other_messages = [

        message

        for message in messages

        if (
            message["sender"]
            != user_sender
            and
            message["sender"]
            != "Unknown"
        )

    ]


    other_senders = []


    for message in other_messages:

        sender = message["sender"]


        if sender not in other_senders:

            other_senders.append(
                sender
            )


    # ========================================================
    # MESSAGE ANALYSIS
    # ========================================================

    unanswered = 0
    conflict_indicators = 0
    user_short_responses = 0
    other_short_responses = 0
    user_all_caps = 0
    other_all_caps = 0
    user_questions = 0
    other_questions = 0
    user_avg_length = 0
    other_avg_length = 0
    response_time_issues = 0


    for i in range(len(messages) - 1):

        current = messages[i]
        next_message = messages[i + 1]

        if (
            current["sender"] == user_sender
            and next_message["sender"] == user_sender
        ):
            unanswered += 1
            response_time_issues += 1

        # Conflict indicators
        text_lower = current["text"].lower()
        if any(word in text_lower for word in ["why", "angry", "mad", "fed up", "sick", "done", "over", "???", "!!!"]):
            conflict_indicators += 1

    # Message length analysis
    if user_messages:
        user_avg_length = round(sum(len(m["text"].split()) for m in user_messages) / len(user_messages))
        user_short_responses = sum(1 for m in user_messages if len(m["text"].split()) < 3)
        user_all_caps = sum(1 for m in user_messages if m["text"].isupper() and len(m["text"]) > 3)
        user_questions = sum(1 for m in user_messages if m["text"].strip().endswith("?"))

    if other_messages:
        other_avg_length = round(sum(len(m["text"].split()) for m in other_messages) / len(other_messages))
        other_short_responses = sum(1 for m in other_messages if len(m["text"].split()) < 3)
        other_all_caps = sum(1 for m in other_messages if m["text"].isupper() and len(m["text"]) > 3)
        other_questions = sum(1 for m in other_messages if m["text"].strip().endswith("?"))


    total_words = sum(len(message["text"].split()) for message in messages)
    if messages:
        avg_length = round(total_words / len(messages))
    else:
        avg_length = 0


    # ========================================================
    # SITUATION ASSESSMENT
    # ========================================================

    situation = {
        "has_conflict": False,
        "conflict_type": None,
        "mood_assessment": None,
        "communication_issue": None,
        "who_at_fault": None,
        "insights": []
    }

    # Detect potential conflicts
    if conflict_indicators > 0:
        situation["has_conflict"] = True

    # Mood and communication analysis
    if other_short_responses > len(other_messages) * 0.5:
        situation["mood_assessment"] = "The other person seems to be giving short, dismissive responses. They might be upset, busy, or disengaged."
        situation["communication_issue"] = "Low engagement"
    elif user_short_responses > len(user_messages) * 0.5 and other_avg_length > user_avg_length * 1.5:
        situation["mood_assessment"] = "You appear to be giving short responses while they're making longer messages. This could indicate you're disengaged or not interested."
        situation["communication_issue"] = "You seem disengaged"
    elif other_all_caps > 0 or user_all_caps > 0:
        situation["mood_assessment"] = "There are messages in ALL CAPS, which can indicate frustration or strong emotion."
        situation["communication_issue"] = "High emotion detected"

    # Fault detection
    if situation["has_conflict"]:
        if user_questions > other_questions:
            situation["who_at_fault"] = "You seem to be asking more questions, possibly seeking clarification or confronting the issue."
        elif other_questions > user_questions and len(other_messages) > len(user_messages):
            situation["who_at_fault"] = "The other person is asking more questions and sending more messages. They might be trying to engage while you're being dismissive."
        else:
            situation["who_at_fault"] = "Both parties seem emotionally involved in this conversation."

    # Generate insights
    if len(user_messages) == 0:
        situation["insights"].append("You haven't sent any messages in this chat.")
    elif len(other_messages) == 0:
        situation["insights"].append("The other person hasn't responded to your messages.")
    else:
        engagement_ratio = len(user_messages) / len(other_messages) if other_messages else 0
        if engagement_ratio > 2:
            situation["insights"].append("You're doing most of the talking. The other person seems passive.")
        elif engagement_ratio < 0.5:
            situation["insights"].append("The other person is dominating the conversation. They might be excited, anxious, or trying hard to connect.")

    if other_avg_length > user_avg_length * 1.3:
        situation["insights"].append("The other person writes longer, more detailed messages than you.")
    elif user_avg_length > other_avg_length * 1.3:
        situation["insights"].append("You tend to write longer messages compared to the other person.")

    if unanswered > len(messages) * 0.1:
        situation["insights"].append(f"You have {unanswered} consecutive messages without a response. This pattern suggests lack of engagement from them.")

    # ========================================================
    # SCORE CALCULATION
    # ========================================================

    score = 20

    score += min(unanswered * 12, 36)

    if len(user_messages) > max(1, len(other_messages)) * 1.5:
        score += 20

    if len(other_messages) > max(1, len(user_messages)) * 2:
        score -= 5

    if avg_length <= 3 and len(messages) >= 4:
        score += 5

    score = max(0, min(100, score))


    # ========================================================
    # STATUS AND VERDICT
    # ========================================================

    if score < 30:
        status = "Probably Fine"
        verdict = (
            "The conversation looks reasonably balanced. Both parties seem engaged and responsive. "
            "There is no strong evidence of being ignored."
        )

    elif score < 55:
        status = "Slightly Suspicious"
        verdict = (
            "There are a few one-sided patterns in this conversation, but nothing conclusive. "
            "It could just be different communication styles or schedules."
        )

    elif score < 75:
        status = "Suspicious"
        verdict = (
            "The conversation shows some concerning patterns. The other person might be distracted, "
            "uninterested, or going through something. Consider having a direct conversation."
        )

    else:
        status = "You Might Be Ignored"
        verdict = (
            "The conversation shows strong signs of imbalance in engagement and response patterns. "
            "Give the other person some space, or consider asking if everything is okay between you two."
        )


    return {

        "score": score,
        "status": status,
        "message_count": len(messages),
        "user_messages": len(user_messages),
        "other_messages": len(other_messages),
        "unanswered": unanswered,
        "avg_length": avg_length,
        "other_senders": other_senders,
        "verdict": verdict,
        "messages": messages,
        "user_sender": user_sender,
        "situation": situation,
        "user_avg_length": user_avg_length,
        "other_avg_length": other_avg_length

    }


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ============================================================
# ANALYZE
# ============================================================

@app.route(
    "/analyze",
    methods=["POST"]
)
def analyze():

    try:

        pasted_chat = request.form.get(
            "chat",
            ""
        ).strip()


        # ====================================================
        # TEXT FILE
        # ====================================================

        text_file = request.files.get(
            "chat_file"
        )


        if (
            text_file
            and
            text_file.filename
        ):

            pasted_chat = (

                text_file.read()

                .decode(
                    "utf-8",
                    errors="replace"
                )

                .strip()

            )


        # ====================================================
        # INPUT
        # ====================================================

        if pasted_chat:

            messages = parse_text_chat(
                pasted_chat
            )


        else:

            return render_template(

                "index.html",

                error=(
                    "Please paste a conversation "
                    "or upload a .txt chat export."
                )

            )


        # ====================================================
        # CHECK
        # ====================================================

        if not messages:

            return render_template(

                "index.html",

                error=(
                    "No messages could be detected. "
                    "Make sure the screenshot is clear "
                    "and contains readable chat text."
                )

            )


        # ====================================================
        # PARTICIPANTS
        # ====================================================

        participants = []


        for message in messages:

            sender = message["sender"]


            if (

                sender
                not in participants

                and

                sender != "Unknown"

            ):

                participants.append(
                    sender
                )


        session["messages"] = messages

        session["participants"] = participants


        return redirect(
            url_for(
                "choose_user"
            )
        )


    except Exception as error:

        app.logger.exception(
            "Analysis failed"
        )


        return render_template(

            "index.html",

            error=(
                f"Could not process the chat: {error}"
            )

        )


# ============================================================
# CHOOSE USER
# ============================================================

@app.route(
    "/choose-user",
    methods=["GET", "POST"]
)
def choose_user():

    participants = session.get(
        "participants",
        []
    )


    messages = session.get(
        "messages",
        []
    )


    if not participants:

        return redirect(
            url_for("home")
        )


    if request.method == "POST":

        user_sender = request.form.get(
            "user_sender",
            ""
        ).strip()


        if user_sender not in participants:

            return render_template(

                "choose_user.html",

                participants=participants,

                messages=messages,

                error=(
                    "Please select one of "
                    "the detected participants."
                )

            )


        results = analyze_chat(

            messages,

            user_sender

        )


        session["results"] = results


        return redirect(
            url_for("results")
        )


    return render_template(

        "choose_user.html",

        participants=participants,

        messages=messages

    )


# ============================================================
# RESULTS
# ============================================================

@app.route("/results")
def results():

    results_data = session.get(
        "results"
    )


    if not results_data:

        return redirect(
            url_for("home")
        )


    return render_template(

        "results.html",

        results=results_data

    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )