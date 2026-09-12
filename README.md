<img width="1280" height="640" alt="git (1)" src="https://github.com/user-attachments/assets/8920b256-2ba8-4988-b824-5351134eb4bd" />

# Am I Being Ignored? 🎯

## Team Name

**Pointless**

## Team Members

* **Team Lead:** Agnivesh Manohar — College of Engineering, Perumon
* **Member 2:** Ian Luke — College of Engineering, Perumon

---

# Project Description

**ChatLens** is a fun, AI-inspired conversation analyzer that examines chat patterns to estimate whether someone might be ignoring you. It analyzes message frequency, unanswered messages, conversation balance, response patterns, message length, questions, and emotional indicators to generate an **Ignoring Score** and a humorous final verdict.

The project turns a common everyday situation — waiting for someone to reply — into an entertaining data-analysis experience.

**Live Demo:** https://pointless.streamlit.app/

---

# The Problem (that doesn't exist)

People are constantly worried about one of life's most unnecessary questions:

> **"Why haven't they replied?"**

Instead of simply waiting, overthinking, or touching grass, ChatLens attempts to scientifically investigate the situation.

Because apparently, we now need data analysis to answer:

**"Bro, are they ignoring me?" 💀**

---

# The Solution (that nobody asked for)

ChatLens turns ordinary chat drama into a mini investigation.

Users can paste a conversation or upload a `.txt` chat export. The system extracts the messages, identifies the participants, and analyzes the conversation from the user's perspective.

It then calculates an **Ignoring Score**, evaluates communication patterns, generates insights, and produces a final verdict such as:

* 🟢 Probably Fine
* 🟡 Slightly Suspicious
* 🟠 Suspicious
* 🔴 You Might Be Ignored

Because sometimes the most unnecessary problems deserve the most unnecessary technology.

---

# Technical Details

## Technologies / Components Used

### For Software

**Languages Used:**

* Python
* HTML
* CSS

**Framework:**

* Streamlit

**Libraries:**

* Streamlit
* Python `re` (Regular Expressions)

**Tools Used:**

* Visual Studio Code
* Python
* Streamlit
* Git / GitHub
* Web Browser

### For Hardware

**Main Components:**
No dedicated hardware required.

**Specifications:**
Any standard laptop, desktop, or smartphone capable of accessing a modern web browser.

**Tools Required for Development:**

* Laptop/Desktop
* Keyboard
* Mouse
* Internet connection

ChatLens is a completely software-based project and does not require sensors, microcontrollers, or other physical hardware.

---

# Implementation

## Software

### Installation

Install the required dependency:

```bash
pip install streamlit
```

### Run Locally

```bash
streamlit run app.py
```

The application will open in a web browser.

### Live Deployment

ChatLens is deployed using Streamlit and is publicly accessible at:

**https://pointless.streamlit.app/**

---

# How ChatLens Works

The application follows a simple workflow:

1. **Input Chat**
   The user pastes a conversation or uploads a `.txt` chat export.

2. **Message Parsing**
   ChatLens uses regular expressions to identify timestamps, participants, and message content.

3. **Participant Detection**
   The system identifies the participants present in the conversation.

4. **User Selection**
   The user selects which participant represents them.

5. **Conversation Analysis**
   ChatLens analyzes:

   * Message counts
   * Message length
   * Consecutive messages
   * Unanswered patterns
   * Questions
   * Short responses
   * ALL CAPS messages
   * Potential conflict indicators
   * Conversation balance

6. **Ignoring Score**
   The detected patterns are combined into a score between **0 and 100**.

7. **Final Verdict**
   The system presents a humorous interpretation of the results.

8. **Insights**
   Additional observations are generated to explain the detected communication patterns.

---

# Project Documentation

## Screenshots

### Screenshot 1 — Chat Input
<img width="1515" height="891" alt="image" src="https://github.com/user-attachments/assets/b81e733c-2176-4c57-b531-2452829a172f" />

**Caption:**
*ChatLens input interface where users can paste a conversation or upload a chat export for analysis.*

### Screenshot 2 — Participant Selection

Show the participant selection section after a chat has been processed.

**Caption:**
*The participant selection interface allows the user to identify themselves before analysis.*

### Screenshot 3 — Analysis Results

Show the final score, verdict, statistics, and insights.

**Caption:**
*ChatLens analysis dashboard displaying the Ignoring Score, verdict, chat statistics, and communication insights.*

---

# Workflow

```text
                 ┌─────────────────────┐
                 │    User Input Chat  │
                 │                     │
                 │ Paste / Upload .txt │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │   Message Parser    │
                 │                     │
                 │ Regex-based parsing │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Participant         │
                 │ Detection           │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Select "Your"       │
                 │ Participant         │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Conversation        │
                 │ Analysis             │
                 │                     │
                 │ • Message balance   │
                 │ • Short responses   │
                 │ • Questions        │
                 │ • Unanswered texts  │
                 │ • Conflict signals  │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Ignoring Score      │
                 │      0 – 100        │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Final Verdict +     │
                 │ Communication       │
                 │ Insights            │
                 └─────────────────────┘
```

**Caption:**
*Workflow of ChatLens from conversation input to message parsing, participant identification, communication analysis, Ignoring Score, and final verdict.*

---

# Hardware

## Schematic & Circuit

**Not Applicable**

ChatLens is a software-only project and does not use electronic circuits, sensors, microcontrollers, or other hardware components.

---

# Build Photos

## Components

**Not Applicable**

No physical components are required for ChatLens.

## Build Process

The project was developed as a web-based software application using Python and Streamlit. The application was tested locally and subsequently deployed online.

## Final Product

The final product is a publicly accessible web application:

**https://pointless.streamlit.app/**

---

# Project Demo

## Video

Add your project demonstration video link here.

The demonstration should show:

1. Opening the ChatLens website
2. Pasting or uploading a conversation
3. Detecting participants
4. Selecting the user
5. Generating the analysis
6. Viewing the Ignoring Score
7. Viewing the verdict and communication insights

---

# Additional Demos

**Live Website:**
https://pointless.streamlit.app/

Additional screenshots, demonstration videos, or project materials can be added here.

---

# Team Contributions

### Agnivesh Manohar — Team Lead

* Project concept development
* Overall project coordination
* Feature planning
* Testing and validation
* Project presentation and documentation

### Ian Luke — Team Member

* Application development
* Chat parsing and analysis logic
* Streamlit interface implementation
* UI and result presentation
* Testing and deployment support

---

# Disclaimer

ChatLens is designed as an **entertainment and educational project**.

The Ignoring Score is based on observable message patterns and does not determine a person's actual intentions, emotions, or reasons for not replying.

In other words:

**The algorithm doesn't know if they're busy. We just gave it a number. 💀**

---

Made with ❤️ at **TinkerHub Useless Projects**



