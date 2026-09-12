import re
import streamlit as st


# ============================================================
# STREAMLIT CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ChatLens",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main {
        background-color: #0e1117;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .chatlens-title {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.2rem;
    }

    .chatlens-subtitle {
        text-align: center;
        color: #9ca3af;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    .result-card {
        padding: 1.5rem;
        border-radius: 15px;
        background: #161b22;
        border: 1px solid #30363d;
        margin-bottom: 1rem;
    }

    .score {
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
    }

    .status {
        font-size: 1.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 1rem;
    }

    .verdict {
        color: #c9d1d9;
        font-size: 1rem;
        line-height: 1.7;
    }

    .section-title {
        font-size: 1.5rem;
        font-weight: 700;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "participants" not in st.session_state:
    st.session_state.participants = []

if "results" not in st.session_state:
    st.session_state.results = None


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

        cleaned.append(
            {
                "sender": sender,
                "text": text,
                "timestamp": timestamp
            }
        )

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

                messages.append(
                    {
                        "sender": "Unknown",
                        "text": line,
                        "timestamp": ""
                    }
                )

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

    for i in range(
        len(messages) - 1
    ):

        current = messages[i]
        next_message = messages[i + 1]

        if (
            current["sender"]
            == user_sender
            and
            next_message["sender"]
            == user_sender
        ):

            unanswered += 1

            response_time_issues += 1

        # ====================================================
        # CONFLICT INDICATORS
        # ====================================================

        text_lower = current["text"].lower()

        if any(
            word in text_lower
            for word in [
                "why",
                "angry",
                "mad",
                "fed up",
                "sick",
                "done",
                "over",
                "???",
                "!!!"
            ]
        ):

            conflict_indicators += 1

    # ========================================================
    # USER MESSAGE LENGTH
    # ========================================================

    if user_messages:

        user_avg_length = round(
            sum(
                len(
                    m["text"].split()
                )
                for m in user_messages
            )
            /
            len(user_messages)
        )

        user_short_responses = sum(
            1
            for m in user_messages
            if len(
                m["text"].split()
            ) < 3
        )

        user_all_caps = sum(
            1
            for m in user_messages
            if (
                m["text"].isupper()
                and
                len(m["text"]) > 3
            )
        )

        user_questions = sum(
            1
            for m in user_messages
            if m["text"]
            .strip()
            .endswith("?")
        )

    # ========================================================
    # OTHER PERSON MESSAGE LENGTH
    # ========================================================

    if other_messages:

        other_avg_length = round(
            sum(
                len(
                    m["text"].split()
                )
                for m in other_messages
            )
            /
            len(other_messages)
        )

        other_short_responses = sum(
            1
            for m in other_messages
            if len(
                m["text"].split()
            ) < 3
        )

        other_all_caps = sum(
            1
            for m in other_messages
            if (
                m["text"].isupper()
                and
                len(m["text"]) > 3
            )
        )

        other_questions = sum(
            1
            for m in other_messages
            if m["text"]
            .strip()
            .endswith("?")
        )

    # ========================================================
    # GENERAL STATISTICS
    # ========================================================

    total_words = sum(
        len(
            message["text"].split()
        )
        for message in messages
    )

    if messages:

        avg_length = round(
            total_words
            /
            len(messages)
        )

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

    # ========================================================
    # DETECT POTENTIAL CONFLICT
    # ========================================================

    if conflict_indicators > 0:

        situation[
            "has_conflict"
        ] = True

    # ========================================================
    # MOOD AND COMMUNICATION ANALYSIS
    # ========================================================

    if (
        other_messages
        and
        other_short_responses
        >
        len(other_messages) * 0.5
    ):

        situation[
            "mood_assessment"
        ] = (
            "The other person seems to be giving "
            "short, dismissive responses. They might "
            "be upset, busy, or disengaged."
        )

        situation[
            "communication_issue"
        ] = "Low engagement"

    elif (
        user_messages
        and
        other_messages
        and
        user_short_responses
        >
        len(user_messages) * 0.5
        and
        other_avg_length
        >
        user_avg_length * 1.5
    ):

        situation[
            "mood_assessment"
        ] = (
            "You appear to be giving short responses "
            "while they're making longer messages. "
            "This could indicate you're disengaged "
            "or not interested."
        )

        situation[
            "communication_issue"
        ] = "You seem disengaged"

    elif (
        other_all_caps > 0
        or
        user_all_caps > 0
    ):

        situation[
            "mood_assessment"
        ] = (
            "There are messages in ALL CAPS, which "
            "can indicate frustration or strong emotion."
        )

        situation[
            "communication_issue"
        ] = "High emotion detected"

    # ========================================================
    # FAULT DETECTION
    # ========================================================

    if situation["has_conflict"]:

        if user_questions > other_questions:

            situation[
                "who_at_fault"
            ] = (
                "You seem to be asking more questions, "
                "possibly seeking clarification or "
                "confronting the issue."
            )

        elif (
            other_questions > user_questions
            and
            len(other_messages)
            >
            len(user_messages)
        ):

            situation[
                "who_at_fault"
            ] = (
                "The other person is asking more questions "
                "and sending more messages. They might be "
                "trying to engage while you're being dismissive."
            )

        else:

            situation[
                "who_at_fault"
            ] = (
                "Both parties seem emotionally involved "
                "in this conversation."
            )

    # ========================================================
    # GENERATE INSIGHTS
    # ========================================================

    if len(user_messages) == 0:

        situation[
            "insights"
        ].append(
            "You haven't sent any messages in this chat."
        )

    elif len(other_messages) == 0:

        situation[
            "insights"
        ].append(
            "The other person hasn't responded to your messages."
        )

    else:

        engagement_ratio = (
            len(user_messages)
            /
            len(other_messages)
        )

        if engagement_ratio > 2:

            situation[
                "insights"
            ].append(
                "You're doing most of the talking. "
                "The other person seems passive."
            )

        elif engagement_ratio < 0.5:

            situation[
                "insights"
            ].append(
                "The other person is dominating the conversation. "
                "They might be excited, anxious, or trying hard to connect."
            )

    if (
        other_avg_length
        >
        user_avg_length * 1.3
    ):

        situation[
            "insights"
        ].append(
            "The other person writes longer, more detailed "
            "messages than you."
        )

    elif (
        user_avg_length
        >
        other_avg_length * 1.3
    ):

        situation[
            "insights"
        ].append(
            "You tend to write longer messages compared "
            "to the other person."
        )

    if unanswered > len(messages) * 0.1:

        situation[
            "insights"
        ].append(
            f"You have {unanswered} consecutive messages "
            "without a response. This pattern suggests "
            "lack of engagement from them."
        )

    # ========================================================
    # SCORE CALCULATION
    # ========================================================

    score = 20

    score += min(
        unanswered * 12,
        36
    )

    if (
        len(user_messages)
        >
        max(
            1,
            len(other_messages)
        )
        * 1.5
    ):

        score += 20

    if (
        len(other_messages)
        >
        max(
            1,
            len(user_messages)
        )
        * 2
    ):

        score -= 5

    if (
        avg_length <= 3
        and
        len(messages) >= 4
    ):

        score += 5

    score = max(
        0,
        min(
            100,
            score
        )
    )

    # ========================================================
    # STATUS AND VERDICT
    # ========================================================

    if score < 30:

        status = "Probably Fine"

        verdict = (
            "The conversation looks reasonably balanced. "
            "Both parties seem engaged and responsive. "
            "There is no strong evidence of being ignored."
        )

    elif score < 55:

        status = "Slightly Suspicious"

        verdict = (
            "There are a few one-sided patterns in this "
            "conversation, but nothing conclusive. It could "
            "just be different communication styles or schedules."
        )

    elif score < 75:

        status = "Suspicious"

        verdict = (
            "The conversation shows some concerning patterns. "
            "The other person might be distracted, uninterested, "
            "or going through something. Consider having a direct conversation."
        )

    else:

        status = "You Might Be Ignored"

        verdict = (
            "The conversation shows strong signs of imbalance "
            "in engagement and response patterns. Give the other "
            "person some space, or consider asking if everything "
            "is okay between you two."
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

        "other_avg_length": other_avg_length,

        "user_short_responses": user_short_responses,

        "other_short_responses": other_short_responses,

        "user_all_caps": user_all_caps,

        "other_all_caps": other_all_caps,

        "user_questions": user_questions,

        "other_questions": other_questions,

        "conflict_indicators": conflict_indicators,

        "total_words": total_words,

        "response_time_issues": response_time_issues

    }


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="chatlens-title">💬 ChatLens</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="chatlens-subtitle">'
    'Analyze conversation patterns and communication behaviour'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("💬 ChatLens")

    st.write(
        "Upload or paste a chat conversation "
        "to analyze its communication patterns."
    )

    st.divider()

    st.subheader("Supported Input")

    st.write(
        "• WhatsApp text export\n\n"
        "• Plain text chat\n\n"
        "• Pasted conversation"
    )

    st.divider()

    st.caption(
        "ChatLens provides pattern-based analysis. "
        "The results are not a definitive judgment "
        "of someone's intentions."
    )


# ============================================================
# INPUT SECTION
# ============================================================

st.markdown(
    '<div class="section-title">📥 Conversation Input</div>',
    unsafe_allow_html=True
)

input_col1, input_col2 = st.columns(
    [2, 1]
)


with input_col1:

    pasted_chat = st.text_area(
        "Paste your conversation",
        height=350,
        placeholder=(
            "[12/09/2026, 10:30 PM] John: Hey\n"
            "[12/09/2026, 10:31 PM] You: Hi\n"
            "[12/09/2026, 10:35 PM] John: How are you?"
        )
    )


with input_col2:

    st.write("### 📄 Upload Chat")

    uploaded_file = st.file_uploader(
        "Upload a .txt chat export",
        type=["txt"],
        help="Upload a WhatsApp or plain-text chat export."
    )

    st.write("")

    st.info(
        "You can either paste the conversation "
        "or upload a .txt file."
    )


# ============================================================
# ANALYZE BUTTON
# ============================================================

if st.button(
    "🔍 Analyze Conversation",
    type="primary",
    use_container_width=True
):

    try:

        chat_text = pasted_chat.strip()

        # ====================================================
        # READ FILE
        # ====================================================

        if uploaded_file is not None:

            chat_text = (
                uploaded_file
                .read()
                .decode(
                    "utf-8",
                    errors="replace"
                )
                .strip()
            )

        # ====================================================
        # CHECK INPUT
        # ====================================================

        if not chat_text:

            st.error(
                "Please paste a conversation "
                "or upload a .txt chat export."
            )

            st.stop()

        # ====================================================
        # PARSE
        # ====================================================

        messages = parse_text_chat(
            chat_text
        )

        if not messages:

            st.error(
                "No messages could be detected. "
                "Make sure the chat contains readable "
                "messages in a supported format."
            )

            st.stop()

        # ====================================================
        # PARTICIPANTS
        # ====================================================

        participants = []

        for message in messages:

            sender = message["sender"]

            if (
                sender not in participants
                and
                sender != "Unknown"
            ):

                participants.append(
                    sender
                )

        if not participants:

            st.error(
                "No participants could be detected "
                "from this conversation."
            )

            st.stop()

        # ====================================================
        # SAVE TO SESSION
        # ====================================================

        st.session_state.messages = messages

        st.session_state.participants = participants

        st.session_state.results = None

        st.success(
            f"Successfully detected "
            f"{len(messages)} messages."
        )

    except Exception as error:

        st.error(
            f"Could not process the chat: {error}"
        )


# ============================================================
# PARTICIPANT SELECTION
# ============================================================

if st.session_state.participants:

    st.divider()

    st.markdown(
        '<div class="section-title">👤 Select Yourself</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Who are you in this conversation?"
    )

    participants = st.session_state.participants

    selected_user = st.selectbox(
        "Select your name",
        participants,
        key="selected_user"
    )

    if st.button(
        "📊 Generate Analysis",
        type="primary",
        use_container_width=True
    ):

        try:

            results = analyze_chat(
                st.session_state.messages,
                selected_user
            )

            st.session_state.results = results

            st.success(
                "Analysis completed successfully."
            )

        except Exception as error:

            st.error(
                f"Analysis failed: {error}"
            )


# ============================================================
# RESULTS
# ============================================================

if st.session_state.results:

    results = st.session_state.results

    st.divider()

    st.markdown(
        '<div class="section-title">📊 Analysis Results</div>',
        unsafe_allow_html=True
    )

    # ========================================================
    # SCORE
    # ========================================================

    score = results["score"]

    if score < 30:
        score_icon = "🟢"

    elif score < 55:
        score_icon = "🟡"

    elif score < 75:
        score_icon = "🟠"

    else:
        score_icon = "🔴"

    score_col1, score_col2, score_col3 = st.columns(
        [1, 2, 1]
    )

    with score_col2:

        st.markdown(
            f"""
            <div class="result-card">
                <div class="score">
                    {score_icon} {score}/100
                </div>
                <div class="status">
                    {results["status"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ========================================================
    # VERDICT
    # ========================================================

    st.markdown(
        '<div class="section-title">🧠 Verdict</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="result-card">
            <div class="verdict">
                {results["verdict"]}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ========================================================
    # CHAT STATISTICS
    # ========================================================

    st.markdown(
        '<div class="section-title">📈 Chat Statistics</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Total Messages",
            results["message_count"]
        )

    with col2:

        st.metric(
            "Your Messages",
            results["user_messages"]
        )

    with col3:

        st.metric(
            "Other Messages",
            results["other_messages"]
        )

    with col4:

        st.metric(
            "Average Words",
            results["avg_length"]
        )

    col5, col6, col7, col8 = st.columns(4)

    with col5:

        st.metric(
            "Your Avg. Length",
            f'{results["user_avg_length"]} words'
        )

    with col6:

        st.metric(
            "Other Avg. Length",
            f'{results["other_avg_length"]} words'
        )

    with col7:

        st.metric(
            "Unanswered Pattern",
            results["unanswered"]
        )

    with col8:

        st.metric(
            "Conflict Indicators",
            results["conflict_indicators"]
        )

    # ========================================================
    # MESSAGE DISTRIBUTION
    # ========================================================

    st.markdown(
        '<div class="section-title">💬 Message Distribution</div>',
        unsafe_allow_html=True
    )

    distribution_col1, distribution_col2 = st.columns(2)

    with distribution_col1:

        st.write(
            f"**You — {results['user_sender']}**"
        )

        st.progress(
            min(
                results["user_messages"]
                /
                max(
                    1,
                    results["message_count"]
                ),
                1.0
            )
        )

        st.write(
            f'{results["user_messages"]} messages'
        )

    with distribution_col2:

        other_count = results["other_messages"]

        st.write(
            "**Other participant(s)**"
        )

        st.progress(
            min(
                other_count
                /
                max(
                    1,
                    results["message_count"]
                ),
                1.0
            )
        )

        st.write(
            f"{other_count} messages"
        )

    # ========================================================
    # COMMUNICATION ANALYSIS
    # ========================================================

    st.markdown(
        '<div class="section-title">🗣️ Communication Analysis</div>',
        unsafe_allow_html=True
    )

    situation = results["situation"]

    if situation["mood_assessment"]:

        st.info(
            situation["mood_assessment"]
        )

    if situation["communication_issue"]:

        st.warning(
            "Communication issue: "
            +
            situation["communication_issue"]
        )

    if situation["who_at_fault"]:

        st.write(
            "**Conflict assessment:**"
        )

        st.write(
            situation["who_at_fault"]
        )

    if not situation["has_conflict"]:

        st.success(
            "No strong conflict indicators were detected."
        )

    # ========================================================
    # INSIGHTS
    # ========================================================

    st.markdown(
        '<div class="section-title">💡 Insights</div>',
        unsafe_allow_html=True
    )

    insights = situation["insights"]

    if insights:

        for insight in insights:

            st.write(
                "🔹 " + insight
            )

    else:

        st.write(
            "No additional insights were detected."
        )

    # ========================================================
    # DETAILED METRICS
    # ========================================================

    st.markdown(
        '<div class="section-title">🔎 Detailed Analysis</div>',
        unsafe_allow_html=True
    )

    detail_col1, detail_col2 = st.columns(2)

    with detail_col1:

        st.write("### Your Communication")

        st.write(
            f"Short responses: "
            f"**{results['user_short_responses']}**"
        )

        st.write(
            f"Questions asked: "
            f"**{results['user_questions']}**"
        )

        st.write(
            f"ALL CAPS messages: "
            f"**{results['user_all_caps']}**"
        )

    with detail_col2:

        st.write("### Other Communication")

        st.write(
            f"Short responses: "
            f"**{results['other_short_responses']}**"
        )

        st.write(
            f"Questions asked: "
            f"**{results['other_questions']}**"
        )

        st.write(
            f"ALL CAPS messages: "
            f"**{results['other_all_caps']}**"
        )

    # ========================================================
    # OTHER PARTICIPANTS
    # ========================================================

    if results["other_senders"]:

        st.markdown(
            '<div class="section-title">👥 Other Participants</div>',
            unsafe_allow_html=True
        )

        for sender in results["other_senders"]:

            st.write(
                f"• {sender}"
            )

    # ========================================================
    # CHAT PREVIEW
    # ========================================================

    st.markdown(
        '<div class="section-title">💬 Chat Preview</div>',
        unsafe_allow_html=True
    )

    with st.expander(
        "View analyzed messages"
    ):

        for message in results["messages"]:

            timestamp = message["timestamp"]

            sender = message["sender"]

            text = message["text"]

            if timestamp:

                st.markdown(
                    f"**[{timestamp}] {sender}:** {text}"
                )

            else:

                st.markdown(
                    f"**{sender}:** {text}"
                )

    # ========================================================
    # RESET
    # ========================================================

    st.divider()

    if st.button(
        "🔄 Analyze Another Chat",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.session_state.participants = []

        st.session_state.results = None

        st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <div style="
        text-align:center;
        color:#6b7280;
        padding:20px;
    ">
        ChatLens • Conversation Pattern Analyzer
        <br>
        <small>
        Results are based on message patterns and should not
        be treated as definitive conclusions about a person.
        </small>
    </div>
    """,
    unsafe_allow_html=True
)
