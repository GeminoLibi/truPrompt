# python3 truPrompt.py
#!/usr/bin/env python3
import os
import json
import base64
import sys
import hashlib
import random
import textwrap
import traceback
from datetime import datetime
from typing import Dict, List

# --- Dependency Check ---
try:
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend
    from cryptography.fernet import Fernet
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False

# --- UI and Styling ---
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

ASCII_BANNER = """
================================================================================
|                                                                            |
|                        truPrompt v7.0                                      |
|                                                                            |
================================================================================
> > > Standardized Agent Prompt Generator <<<
"{}"
================================================================================
"""

MOTIVATIONAL_QUOTES = [
    "The best way to predict the future is to create it. - Peter Drucker",
    "Innovation distinguishes between a leader and a follower. - Steve Jobs",
    "Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill",
    "The only way to do great work is to love what you do. - Steve Jobs",
    "Don't be afraid to give up the good to go for the great. - John D. Rockefeller",
    "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
    "It is during our darkest moments that we must focus to see the light. - Aristotle",
    "The way to get started is to quit talking and begin doing. - Walt Disney",
    "Life is what happens to you while you're busy making other plans. - John Lennon",
    "The future depends on what you do today. - Mahatma Gandhi",
    "Innovation is the ability to see change as an opportunity, not a threat. - Steve Jobs",
    "Your limitation—it's only your imagination.",
    "Push yourself, because no one else is going to do it for you.",
    "Sometimes later becomes never. Do it now.",
    "Great things never come from comfort zones.",
    "Dream it. Wish it. Do it.",
    "Success doesn't just find you. You have to go out and get it.",
    "The harder you work for something, the greater you'll feel when you achieve it.",
    "Dream bigger. Do bigger.",
    "Don't stop when you're tired. Stop when you're done.",
    "Wake up with determination. Go to bed with satisfaction.",
    "Do something today that your future self will thank you for.",
    "Little things make big days.",
    "It's going to be hard, but hard does not mean impossible.",
    "Don't wait for opportunity. Create it.",
    "Sometimes we're tested not to show our weaknesses, but to discover our strengths.",
    "The key to success is to focus on goals, not obstacles.",
    "Dream it. Believe it. Build it.",
    "The only impossible journey is the one you never begin. - Tony Robbins",
    "In the middle of difficulty lies opportunity. - Albert Einstein",
    "The only way to do great work is to love what you do. - Steve Jobs",
    "Don't be pushed around by the fears in your mind. Be led by the dreams in your heart. - Roy T. Bennett",
    "Believe you can and you're halfway there. - Theodore Roosevelt",
    "The way to get started is to quit talking and begin doing. - Walt Disney",
    "Don't let yesterday take up too much of today. - Will Rogers",
    "You learn more from failure than from success. Don't let it stop you. Failure builds character. - Unknown",
    "If you are working on something that you really care about, you don't have to be pushed. The vision pulls you. - Steve Jobs",
    "People who are crazy enough to think they can change the world, are the ones who do. - Rob Siltanen",
    "We may encounter many defeats but we must not be defeated. - Maya Angelou",
    "Knowing is not enough; we must apply. Wishing is not enough; we must do. - Johann Wolfgang von Goethe",
    "Imagine your life is perfect in every respect; what would it look like? - Brian Tracy",
    "We become what we think about most of the time, and that's the strangest secret. - Earl Nightingale",
    "The only person you are destined to become is the person you decide to be. - Ralph Waldo Emerson",
    "Go confidently in the direction of your dreams. Live the life you have imagined. - Henry David Thoreau",
    "When you have a dream, you've got to grab it and never let go. - Carol Burnett",
    "Nothing is impossible, the word itself says 'I'm possible'! - Audrey Hepburn",
    "There is nothing impossible to they who will try. - Alexander the Great",
    "The bad news is time flies. The good news is you're the pilot. - Michael Altshuler",
    "Life has got all those twists and turns. You've got to hold on tight and off you go. - Nicole Kidman",
    "Keep your face always toward the sunshine, and shadows will fall behind you. - Walt Whitman",
    "Be courageous. Challenge orthodoxy. Stand up for what you believe in. When you are in your rocking chair talking to your grandchildren many years from now, be sure you have a good story to tell. - Amal Clooney",
    "You make a choice: continue living your life feeling muddled in this abyss of self-misunderstanding, or you find your identity independent of it. You draw your own box. - Duchess Meghan",
    "I just want you to know that if you are out there and you are being really hard on yourself right now for something that has happened ... it's normal. That is what is going to happen to you in life. No one gets through unscathed. We are all going to have a few scratches on us. Please be kind to yourselves and stand up for yourself, please. - Taylor Swift",
    "Spread love everywhere you go. Let no one ever come to you without leaving happier. - Mother Teresa",
    "When you reach the end of your rope, tie a knot in it and hang on. - Franklin D. Roosevelt",
    "Always remember that you are absolutely unique. Just like everyone else. - Margaret Mead",
    "Don't judge each day by the harvest you reap but by the seeds that you plant. - Robert Louis Stevenson",
    "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
    "Tell me and I forget. Teach me and I remember. Involve me and I learn. - Benjamin Franklin",
    "The best and most beautiful things in the world cannot be seen or even touched - they must be felt with the heart. - Helen Keller",
    "It is during our darkest moments that we must focus to see the light. - Aristotle",
    "Whoever is happy will make others happy too. - Anne Frank",
    "Do not go where the path may lead, go instead where there is no path and leave a trail. - Ralph Waldo Emerson",
    "You will face many defeats in life, but never let yourself be defeated. - Maya Angelou",
    "The greatest glory in living lies not in never falling, but in rising every time we fall. - Nelson Mandela",
    "In the end, it's not the years in your life that count. It's the life in your years. - Abraham Lincoln",
    "Never let the fear of striking out keep you from playing the game. - Babe Ruth",
    "Life is either a daring adventure or nothing at all. - Helen Keller",
    "Many of life's failures are people who did not realize how close they were to success when they gave up. - Thomas A. Edison",
    "You have brains in your head. You have feet in your shoes. You can steer yourself any direction you choose. - Dr. Seuss",
    "Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill",
    "The way to get started is to quit talking and begin doing. - Walt Disney",
    "Don't let yesterday take up too much of today. - Will Rogers",
    "You learn more from failure than from success. Don't let it stop you. Failure builds character. - Unknown",
    "If you are working on something that you really care about, you don't have to be pushed. The vision pulls you. - Steve Jobs",
    "People who are crazy enough to think they can change the world, are the ones who do. - Rob Siltanen",
    "We may encounter many defeats but we must not be defeated. - Maya Angelou",
    "Knowing is not enough; we must apply. Wishing is not enough; we must do. - Johann Wolfgang von Goethe",
    "Imagine your life is perfect in every respect; what would it look like? - Brian Tracy",
    "We become what we think about most of the time, and that's the strangest secret. - Earl Nightingale",
    "The only person you are destined to become is the person you decide to be. - Ralph Waldo Emerson",
    "Go confidently in the direction of your dreams. Live the life you have imagined. - Henry David Thoreau",
    "When you have a dream, you've got to grab it and never let go. - Carol Burnett",
    "Nothing is impossible, the word itself says 'I'm possible'! - Audrey Hepburn",
    "There is nothing impossible to they who will try. - Alexander the Great",
    "The bad news is time flies. The good news is you're the pilot. - Michael Altshuler",
    "Life has got all those twists and turns. You've got to hold on tight and off you go. - Nicole Kidman",
    "Keep your face always toward the sunshine, and shadows will fall behind you. - Walt Whitman",
    "Be courageous. Challenge orthodoxy. Stand up for what you believe in. When you are in your rocking chair talking to your grandchildren many years from now, be sure you have a good story to tell. - Amal Clooney",
    "You make a choice: continue living your life feeling muddled in this abyss of self-misunderstanding, or you find your identity independent of it. You draw your own box. - Duchess Meghan",
    "I just want you to know that if you are out there and you are being really hard on yourself right now for something that has happened ... it's normal. That is what is going to happen to you in life. No one gets through unscathed. We are all going to have a few scratches on us. Please be kind to yourselves and stand up for yourself, please. - Taylor Swift",
    "Spread love everywhere you go. Let no one ever come to you without leaving happier. - Mother Teresa",
    "When you reach the end of your rope, tie a knot in it and hang on. - Franklin D. Roosevelt",
    "Always remember that you are absolutely unique. Just like everyone else. - Margaret Mead",
    "Don't judge each day by the harvest you reap but by the seeds that you plant. - Robert Louis Stevenson",
    "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
    "Tell me and I forget. Teach me and I remember. Involve me and I learn. - Benjamin Franklin",
    "The best and most beautiful things in the world cannot be seen or even touched - they must be felt with the heart. - Helen Keller",
    "It is during our darkest moments that we must focus to see the light. - Aristotle",
    "Whoever is happy will make others happy too. - Anne Frank",
    "Do not go where the path may lead, go instead where there is no path and leave a trail. - Ralph Waldo Emerson",
    "You will face many defeats in life, but never let yourself be defeated. - Maya Angelou",
    "The greatest glory in living lies not in never falling, but in rising every time we fall. - Nelson Mandela",
    "In the end, it's not the years in your life that count. It's the life in your years. - Abraham Lincoln",
    "Never let the fear of striking out keep you from playing the game. - Babe Ruth",
    "Life is either a daring adventure or nothing at all. - Helen Keller",
    "Many of life's failures are people who did not realize how close they were to success when they gave up. - Thomas A. Edison",
    "You have brains in your head. You have feet in your shoes. You can steer yourself any direction you choose. - Dr. Seuss"
    "I barely know what I'm doing, but I know I'm doing it. - Markus Johnson",
    "Ask and it will be given to you; seek and you will find; knock and the door will be opened to you. - Jesus Christ",
    "For I know the plans I have for you, declares the Lord, plans to prosper you and not to harm you, to give you hope and a future. - Jeremiah 29:11",
    "I can do all things through Christ who strengthens me. - Philippians 4:13",
    "The Lord is my shepherd; I shall not want. - Psalm 23:1",
    "Trust in the Lord with all your heart and lean not on your own understanding. - Proverbs 3:5",
    "For God so loved the world that he gave his one and only Son, that whoever believes in him shall not perish but have eternal life. - John 3:16",
    "Love your enemies and pray for those who persecute you. - Jesus Christ",
    "Blessed are the peacemakers, for they will be called children of God. - Jesus Christ",
    "Do unto others as you would have them do unto you. - Jesus Christ",
    "The truth will set you free. - Jesus Christ",
    "Let your light shine before others, that they may see your good deeds and glorify your Father in heaven. - Jesus Christ",
    "Seek first the kingdom of God and his righteousness, and all these things will be given to you as well. - Jesus Christ",
    "With God all things are possible. - Jesus Christ",
    "I am the way, the truth, and the life. - Jesus Christ",
    "I am looking for a man. - Diogenes",
    "The foundation of every state is the education of its youth. - Diogenes",
    "I know nothing except the fact of my ignorance. - Diogenes",
    "The sun shines into the hut of the beggar as brightly as into the palace of the king. - Diogenes",
    "The only way to escape the corruption of the world is to live in it without being of it. - Diogenes",
    "We have two ears and one mouth so that we can listen twice as much as we speak. - Diogenes",
    "The art of being wise is the art of knowing what to overlook. - Diogenes",
    "It is not that I am mad, it is only that my head is different from yours. - Diogenes",
    "I am a citizen of the world. - Diogenes",
    "Do or do not, there is no try. - Yoda",
    "The Force will be with you, always. - Obi-Wan Kenobi",
    "Fear is the path to the dark side. Fear leads to anger. Anger leads to hate. Hate leads to suffering. - Yoda",
    "A Jedi's strength flows from the Force. - Yoda",
    "Size matters not. Look at me. Judge me by my size, do you? - Yoda",
    "The greatest teacher, failure is. - Yoda",
    "You must unlearn what you have learned. - Yoda",
    "Wars not make one great. - Yoda",
    "I find your lack of faith disturbing. - Darth Vader",
    "The Force is strong with this one. - Darth Vader",
    "I am your father. - Darth Vader",
    "Help me, Obi-Wan Kenobi. You're my only hope. - Princess Leia",
    "I love you. I know. - Han Solo & Princess Leia",
    "Never tell me the odds! - Han Solo",
    "I've got a bad feeling about this. - Various Star Wars characters",
    "All we have to decide is what to do with the time that is given us. - Gandalf",
    "Even the smallest person can change the course of the future. - Galadriel",
    "Not all those who wander are lost. - J.R.R. Tolkien",
    "There is some good in this world, and it's worth fighting for. - Samwise Gamgee",
    "The road goes ever on and on. - Bilbo Baggins",
    "I will not say: do not weep; for not all tears are an evil. - Gandalf",
    "Despair is only for those who see the end beyond all doubt. - Gandalf",
    "Even darkness must pass. A new day will come. - Samwise Gamgee",
    "The world is indeed full of peril, and in it there are many dark places; but still there is much that is fair. - Gandalf",
    "It's a dangerous business, Frodo, going out your door. - Bilbo Baggins",
    "I am no man! - Eowyn",
    "You shall not pass! - Gandalf",
    "My precious. - Gollum",
    "One does not simply walk into Mordor. - Boromir",
    "It is our choices, Harry, that show what we truly are, far more than our abilities. - Albus Dumbledore",
    "Happiness can be found, even in the darkest of times, if one only remembers to turn on the light. - Albus Dumbledore",
    "It does not do to dwell on dreams and forget to live. - Albus Dumbledore",
    "Words are, in my not-so-humble opinion, our most inexhaustible source of magic. - Albus Dumbledore",
    "The truth is a beautiful and terrible thing, and should therefore be treated with great caution. - Albus Dumbledore",
    "It takes a great deal of bravery to stand up to our enemies, but just as much to stand up to our friends. - Albus Dumbledore",
    "We are only as strong as we are united, as weak as we are divided. - Albus Dumbledore",
    "It is the unknown we fear when we look upon death and darkness, nothing more. - Albus Dumbledore",
    "Numbing the pain for a while will make it worse when you finally feel it. - Albus Dumbledore",
    "The best of us must sometimes eat our words. - Albus Dumbledore",
    "I am not worried, Harry. I am with you. - Albus Dumbledore",
    "Help will always be given at Hogwarts to those who ask for it. - Albus Dumbledore",
    "It is important to fight and fight again, and keep fighting, for only then can evil be kept at bay. - Albus Dumbledore",
    "The consequences of our actions are always so complicated, so diverse, that predicting the future is a very difficult business indeed. - Albus Dumbledore",
    "With great power comes great responsibility. - Uncle Ben (Spider-Man)",
    "I am Iron Man. - Tony Stark",
    "I can do this all day. - Captain America",
    "I'm always angry. - Bruce Banner",
    "I am Groot. - Groot",
    "I have a plan. - Rocket Raccoon",
    "I am inevitable. - Thanos",
    "Why do we fall? So we can learn to pick ourselves up. - Alfred Pennyworth (Batman)",
    "It's not who I am underneath, but what I do that defines me. - Batman",
    "The night is darkest just before the dawn. - Harvey Dent",
    "To be or not to be, that is the question. - Hamlet",
    "All the world's a stage, and all the men and women merely players. - William Shakespeare",
    "The course of true love never did run smooth. - William Shakespeare",
    "Cowards die many times before their deaths; the valiant never taste of death but once. - William Shakespeare",
    "We know what we are, but know not what we may be. - William Shakespeare",
    "The fault, dear Brutus, is not in our stars, but in ourselves. - William Shakespeare",
    "To thine own self be true. - William Shakespeare",
    "What light through yonder window breaks? - William Shakespeare",
    "A rose by any other name would smell as sweet. - William Shakespeare",
    "The lady doth protest too much, methinks. - William Shakespeare",
    "Something is rotten in the state of Denmark. - William Shakespeare",
    "The play's the thing. - William Shakespeare",
    "There are more things in heaven and earth, Horatio, than are dreamt of in your philosophy. - William Shakespeare",
    "The rest is silence. - William Shakespeare"
]

def display_banner():
    quote = random.choice(MOTIVATIONAL_QUOTES)
    print(Colors.HEADER + ASCII_BANNER.format(quote) + Colors.ENDC)

# --- Core Prompt Template Sections ---

PROMPT_HEADER = """### Generated System Prompt for {agency_name}
You are the dataPull Agent. You will operate according to the following comprehensive instructions."""

AGENCY_CONFIG = """### 1. Agency and System Configuration
* Agency Name: `{agency_name}`
* Agency Abbreviation: `{agency_abbr}`
* City: `{city}`
* County: `{county}`
* State: `{state}`
* Records Management System (RMS): `{rms_name}`
* Operating System: `{os_name}`"""

CREDENTIAL_CONFIG_PLAINTEXT = """### 3. Credential Management
**CRITICAL**: Credentials are stored in plaintext for standard operation.
* **RMS Username**: `{rms_username}`
* **RMS Password**: `{rms_password}`{other_systems_text}"""

MISSION_IDENTITY = """### 4. Mission Identity and Critical Rules
* ID: Your identity is `dataPull agent`.
* Integration: You are integrated with TruAssist, a Law Enforcement AI.
* Task: Execute Request for Information (RFI) commands formatted as `$CMD|$D1|$D2...`
* Methodology: Operate exclusively through GUI navigation (screen capture, data extraction, simulated inputs).
* Goals: Efficiently fulfill RFIs, learn from the environment, and document processes.
CRITICAL RULES:
* NEVER simulate data. If information is not found, report "Cannot locate".
* Always verify data before submission."""

SITUATIONAL_TOOL_USE = """### 5. Situational Tool Use & Logic
* **Scenario 1: Internal Data Retrieval** (`_PERSON_LOOKUP`, `_CASE_LOOKUP`, etc.)
    * **Preferred Tool**: **Direct GUI Interaction** with the RMS.
    * **Rationale**: The requested data is located exclusively within the RMS.
* **Scenario 2: External Information Gathering (OSINT)**
    * **Preferred Tool**: **Web Browser navigating to `https://osintframework.com/`**.
    * **Rationale**: This framework provides a structured map of tools. Start here to identify the best resources.
* **Scenario 3: Extracting Large Blocks of Text** (e.g., case narratives)
    * **Preferred Tool**: **Keyboard Shortcuts** (`Ctrl+A`, `Ctrl+C`).
    * **Rationale**: Direct copying is faster and more accurate than visual data extraction."""

GUI_INTERACTION_PRINCIPLES = """### 6. GUI Interaction Principles
* CRITICAL CLICKING PROCEDURE: Execute `mouse_move` to coordinates, followed by `left_click` (without coordinates).
* Text Verification: After typing, screenshot to verify correct entry.
* Field Navigation: Use `mouse_move` -> `left_click`, then screenshot to verify selection.
* Error Handling (3-Strikes): If an action fails three times, screenshot, analyze, and attempt an alternative solution.
* **RMS Interaction Best Practices**:
    * **Clear Forms**: Before a new query, always use a "Clear" or "Reset" button if available.
    * **Manage Date Filters**: If a search yields no results, your first step is to significantly expand the date range.
    * **Mindful Window Management**: Close detail windows after extraction to preserve system memory.
    * **Check for Hidden Results**: Always check for and use scroll bars (vertical and horizontal)."""

STANDARD_OPERATING_PROCEDURE = """### 7. Standard Operating Procedure (Phases)
* Phase 0: Initialize RMS.
* Phase 1: Bootstrap and Discovery (Parse RFI).
* Phase 2: Actualization (Build Plan of Action).
* Phase 3: Information Retrieval (Execute POA, extract data).
* Phase 4: Report Generation (Compile JSON).
* Phase 5: Synthesis and Reset (Transmit report).
* Phase 6: Cleanup and Retention (Close windows, log activity)."""

OUTPUT_SCHEMA = """### 9. Required Output Schema
{{
  "reportMetadata": {{ "rfiCommand": "string", "status": "SUCCESS | FAILURE", "summary": "Natural language summary." }},
  "dataPayload": [ {{ "recordID": "string", "recordType": "string", "extractedData": {{}} }}]
}}"""

APPENDIX = """### 10. Appendix: Contingencies and Reference
* FMEA (Failure Mode and Effects Analysis):
    * **Authentication Failure**: Login credentials rejected. Detect via error messages. Mitigate by verifying credentials, checking caps lock, and re-typing.
    * **RMS Absent/Non-Functional**: RFI failure. Detect via no icon or application crash. Mitigate by searching the system start menu or desktop for the application; otherwise, report an error.
    * **Connectivity Loss**: External queries fail. Detect via RMS/browser failure. Mitigate by retrying, then returning an "Offline" status error.
    * **Data Extraction Misreads**: Critical data is incorrectly extracted. Detect via verification failures or nonsensical results. Mitigate by retaking screenshots, adjusting zoom, or using alternative extraction methods (e.g., keyboard copy/paste).
    * **Command Parse Failure**: Agent misinterprets RFI. Detect via Plan of Action not matching the command's goal. Mitigate by re-tokenizing the command and re-building the plan.
    * **Timeout on Slow Queries**: System becomes unresponsive during searches. Detect via no response after 30 seconds. Mitigate by canceling the query, checking system status, and retrying with simpler parameters.
    * **Multi-page Result Handling**: Agent fails to see all results. Detect via pagination controls ("Next", "Page 2", etc.). Mitigate by systematically navigating through all pages and compiling a complete result set.
    * **"No Access Zone" Interaction**: Agent accidentally interacts with a forbidden window (e.g., the agent's own control terminal). Detect by focus shifting to a No Access Zone. Mitigate by immediately re-minimizing the window and logging the avoidance.
* Troubleshooting Steps:
    1. Identify the error and match it to the FMEA.
    2. Retry the failed action.
    3. If the RMS is the issue, perform a web search for "[RMS_NAME] user guide manual official" to find navigation tips and adapt your plan.
    4. If an action fails more than 5 times, log the persistent failure, describe the attempted solutions, and move to the next task.
"""

SIGNATURE_POLICY = """### 11. Signature and Documentation Policy
* **Secure Signature**: `{secure_signature}`
* **CRITICAL RULE**: You MUST apply this signature to any and all documents, reports, or logs that you create on the host system. This ensures authenticity and auditability."""


# --- DATABASES ---

WORKFLOWS_DATABASE = [
    {"Full Command": "_RMS_LOGIN", "Short Form": "_RL", "Description": "Securely log into the RMS."},
    {"Full Command": "_INITIATE|$start:", "Short Form": "_INIT", "Description": "Initialize the system for operation."},
    {"Full Command": "_UNKNOWN_QUERY_NLP|$Q_TXT:", "Short Form": "_UQN", "Description": "Handle an unformatted query by inferring user intent."},
    {"Full Command": "_PERSON_LOOKUP|$LN|$FN:", "Short Form": "_PRL", "Description": "Search for a person by last name and first name."},
    {"Full Command": "_CASE_LOOKUP|$CN:", "Short Form": "_CL", "Description": "Search for a case or incident by its number."},
    {"Full Command": "_LICENSE_PLATE_LOOKUP|$PN:", "Short Form": "_LPL", "Description": "Search for a vehicle by its license plate number."},
    {"Full Command": "_WARRANT_LOOKUP|$SID|$JUR:", "Short Form": "_WL", "Description": "Search for warrants on a subject."},
    {"Full Command": "_VIN_LOOKUP|$VIN:", "Short Form": "_VL", "Description": "Search for vehicle information using a VIN."},
    {"Full Command": "_PROPERTY_LOOKUP|$IDESC|$SNUM:", "Short Form": "_PL", "Description": "Query for stolen or lost property."},
    {"Full Command": "_ADDRESS_LOOKUP|$HN|$ST:", "Short Form": "_AL", "Description": "Search for an address by house number and street name."},
    {"Full Command": "_ADDRESS_FULL_REPORT|$ADDRESS:", "Short Form": "_AFR", "Description": "Generate a comprehensive premises report for an address."},
    {"Full Command": "_ADDRESS_CFS_HISTORY|$ADDRESS|$DATE_RANGE:", "Short Form": "_ACH", "Description": "Retrieve Calls for Service (CFS) history at an address."},
    {"Full Command": "_ADDRESS_KNOWN_PERSONS|$ADDRESS:", "Short Form": "_AKP", "Description": "List all persons associated with an address."},
    {"Full Command": "_ADDRESS_VEHICLES|$ADDRESS:", "Short Form": "_AV", "Description": "List all vehicles associated with an address."},
    {"Full Command": "_ADDRESS_WEAPONS_INFO|$ADDRESS:", "Short Form": "_AWI", "Description": "Find weapon information associated with an address."},
    {"Full Command": "_ADDRESS_HAZARDS|$ADDRESS:", "Short Form": "_AH", "Description": "Find premise hazards or officer safety notes for an address."},
    {"Full Command": "_OSINT_PERSON_LOOKUP|$LN|$FN:", "Short Form": "_OPL", "Description": "Perform a comprehensive OSINT search for a person."},
    {"Full Command": "_OSINT_ASSOCIATES|$SNAM|$DEPTH:", "Short Form": "_OA", "Description": "Use OSINT to find associates of a subject."},
    {"Full Command": "_COPWARE_LOOKUP|$Question:", "Short Form": "_COP", "Description": "Search the COPWARE database to answer a natural language question."},
    {"Full Command": "_DIAGNOSTIC_INPUT_CHECK|$mode:", "Short Form": "_DIC", "Description": "Verify keyboard and mouse input mappings."},
    {"Full Command": "_EXPLORE_RMS|$USER|$PASS:", "Short Form": "_ER", "Description": "Heuristically explore an unknown RMS GUI."},
    {"Full Command": "_SELF_EVAL|$mode:", "Short Form": "_SE", "Description": "Perform a self-evaluation."},
    {"Full Command": "_NARRATIVE_EXTRACT|$CID:", "Short Form": "_NE", "Description": "Extract all narratives for a case ID."},
    {"Full Command": "_BATCH|$CMD1;$CMD2;$CMD3:", "Short Form": "_BATCH", "Description": "Execute multiple commands sequentially."}
]

RMS_CONFIG = {
    "RIMS": {
        "general_notes": [
            "[CRITICAL: If RIMS windows are already open, use the existing instance and maximize it.]",
            "[GUI: Does not support standard Windows keyboard shortcuts. Use mouse navigation.]",
            "[GUI: The 'Back' button is functional for returning to previous screens.]",
            "[Workflow: Do NOT use the `double_click` tool. Use a single `left_click` followed by the `enter` key.]",
            "[Workflow: Never create or alter records. If an edit/create interface opens, cancel immediately.]",
            "[Note: Ignore any 'message center' popups or 'Print Preview' options.]"
        ],
        "procedures": {
            "_CASE_LOOKUP|$CN:": "1. Navigate: Click 'Cases' in the top menu. 2. Input: Click the 'Case #' text field in the bottom left and enter `$CN`. Do not click the main case list. 3. Execute: Click the 'Enter' button (two icons to the right of the text field) and wait 10 seconds. 4. Extract: Systematically go through each page on the left ('Page 1', 'Persons', 'Property', etc.), extracting all populated fields. For 'Persons', click 'Display All Persons'. For 'Photos', use 'Next'/'Previous'. Do not attempt to view 'Attachments'. Skip 'Queries'. 5. Cleanup: Close the Case Details sub-window, then close the Case Log sub-window."
        }
    },
    "Spillman Flex": {
        "general_notes": ["[GUI: Features a powerful native command line (press F2 for help).]", "[Workflow: Prioritize the command line over GUI navigation.]"],
        "procedures": {"_PERSON_LOOKUP|$LN|$FN:": "1. In command line, type `rpnames`. 2. Enter `$LN` and `$FN`. 3. Execute search and extract data."}
    },
    "New World": {
        "general_notes": [
            "[GUI: The application opens 'sub-windows' inside the main window. Do not close the main window.]",
            "[GUI: Sub-windows can pile up; close them after completing a task to preserve resources.]",
            "[GUI: Results may be hidden. Always use the scroll bar on the far right to check for more data.]",
            "[GUI: Navigating results grids is often easier with arrow keys.]",
            "[Workflow: Focus on the most recent THREE incidents as a starting point unless directed otherwise.]",
            "[Note: Ignore any NCIC information for now, as it is in a different application.]"
        ],
        "module_overview": {
            "title": "#### Important Modules Overview",
            "intro": "The left-side navigation bar contains modules for different searches. Below is an overview of relevant modules and their fields.",
            "modules": [
                {"name": "1. Persons and Businesses", "details": "Submenus: Global Subject Search | Fields: Name/DOB/SSN/Race/Sex/etc. | Filters: Photos/Warrants/Custody/Guns | Workflows: _PERSON_LOOKUP"},
                {"name": "2. Incidents", "details": "Submenus: Incident Search | Fields: Incident Type/Case Number/Date/Location/Person | Workflows: _CASE_LOOKUP, _ADDRESS_LOOKUP"},
                {"name": "3. Cases", "details": "Submenus: Case Search | Fields: Case Number/Status/Date/Type/Location/Person | Workflows: _CASE_LOOKUP"}
            ]
        },
        "prioritization_logic": {
            "title": "#### Incident Page Prioritization",
            "intro": "Incident detail pages have multiple tabs. Prioritize data extraction based on query intent:",
            "rules": [
                "[IMMEDIATE (Officer Safety): Focus on 'Special Response Info', 'Persons', 'Associated Numbers', 'Vehicles' tabs.]",
                "[INCIDENT (Historical Context): Focus on 'Narratives', 'Units/Personnel', 'Dispositions', 'Dispatch Events' tabs.]",
                "[SECONDARY (Investigation): Focus on the 'Associated Calls' tab for pattern analysis.]"
            ]
        },
        "procedures": {
            "_PERSON_LOOKUP|$LN|$FN:": "1. Navigate via 'Persons and Business' -> 'Global Subject Search'. 2. Enter `$LN` and `$FN`. 3. Execute Search. 4. Double-click matches for details.",
            "_ADDRESS_LOOKUP|$HN|$ST:": "1. Navigate via 'Incidents' -> 'Incident Search'. 2. Toggle 'Search Partial Address'. 3. Enter `$HN` and `$ST` and a 5-year date range. 4. Double-click each incident to capture full details."
        }
    },
    "Cody": {
        "general_notes": ["[GUI: Search is a two-step process: 'Initiate' then 'Execute'.]", "[Quirk: You must clear all fields before a new query.]"],
        "procedures": {"_CASE_LOOKUP|$CN:": "1. If `$CN` is 'XX-XXXX' format, search 'Log Number' field first. 2. Click 'Initiate', enter data, click 'Execute'."}
    },
    "Zuercher": {
        "general_notes": [
            "[Navigation: Use 'Main Menu' -> 'Master Searches' for primary lookups.]",
            "[Quirk: Default search date is 'Last 30 Days'; expand if needed.]",
            "[Quirk: The RMS has limited memory; close individual sub-windows after use.]",
            "[Workflow: Use the built-in NCIC integration; do not use external NCIC apps.]",
            "[Note: Ignore all functionality related to the Jail.]"
        ],
        "module_overview": {
            "title": "#### Dashboard Overview",
            "intro": "The dashboard is highly customizable via 'Add Part' and provides quick access to real-time information.",
            "modules": [
                {"name": "Warrants in Active Status", "details": "PRIMARY tool for _WARRANT_LOOKUP. A comprehensive, scrollable list of all active warrants."},
                {"name": "Recent High Priority CFS", "details": "PRIMARY tool for address lookups. Shows high-priority calls with clickable IDs for full details."}
            ]
        },
        "prioritization_logic": {
            "title": "#### Query Intent Prioritization",
            "intro": "Analyze the query to determine intent and focus data extraction accordingly:",
            "rules": [
                "[IMMEDIATE (Officer Safety): Focus on CFS Log, Person Search, and Vehicle Search for alerts and hazards.]",
                "[INCIDENT (Historical Context): Focus on Cases, Warrant Log, and Property/Evidence for narratives and linked records.]",
                "[SECONDARY (Investigation): Use Intelligence Cases, Investigative Leads, and date range searches in the CFS Log.]"
            ]
        },
        "procedures": {
            "_PERSON_LOOKUP|$LN|$FN:": "1. Navigate via Main Menu -> Master Searches -> Name Search. 2. Enter `$LN` and `$FN`. 3. Execute and extract from detail view."
        }
    },
    "OneSolutionRMS": {
        "general_notes": ["[GUI: Workflow is Select Module -> 'Search' -> Type Query -> 'View'.]", "[Quirk: Must click 'EXIT SRCH' button to clear the form after a query.]"]
    },
    "Tritech": {
        "general_notes": ["[GUI: Must use the web app.]", "[Workflow: To access advanced search, click the search bar and press Enter without typing.]"]
    },
    "Default": {
        "general_notes": ["[Note: This is a generic configuration. Adapt to the specific GUI.]"],
        "procedures": {}
    }
}


# --- Workflow Selection Class ---
class WorkflowSelector:
    def __init__(self):
        self.workflows = WORKFLOWS_DATABASE
        self.basic_commands = [
            "_EXPLORE_RMS|$USER|$PASS:", "_PERSON_LOOKUP|$LN|$FN:", "_LICENSE_PLATE_LOOKUP|$PN:",
            "_ADDRESS_LOOKUP|$HN|$ST:", "_ADDRESS_FULL_REPORT|$ADDRESS:", "_ADDRESS_CFS_HISTORY|$ADDRESS|$DATE_RANGE:",
            "_ADDRESS_KNOWN_PERSONS|$ADDRESS:", "_ADDRESS_VEHICLES|$ADDRESS:", "_ADDRESS_WEAPONS_INFO|$ADDRESS:",
            "_ADDRESS_HAZARDS|$ADDRESS:", "_CASE_LOOKUP|$CN:", "_UNKNOWN_QUERY_NLP|$Q_TXT:"
        ]

    def display_workflow_menu(self) -> List[str]:
        print(f"\n{Colors.BLUE}--- Additional Workflow Selection ---{Colors.ENDC}")
        print("Core workflows are included by default.")
        available = [w for w in self.workflows if w['Full Command'] not in self.basic_commands]
        if not available:
            print("No additional workflows available.")
            return []
        print("\nAdditional workflows available:")
        for i, wf in enumerate(available, 1):
            print(f"{i:2d}. {wf['Short Form']:<6} - {wf['Description']}")
        selection = input(f"\n{Colors.CYAN}Select workflows to add (comma-separated numbers, or 'all', or ENTER to skip): {Colors.ENDC}").strip().lower()
        selected_cmds = []
        if selection == 'all':
            selected_cmds.extend([w['Full Command'] for w in available])
        elif selection:
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(',')]
                selected_cmds.extend([available[idx]['Full Command'] for idx in indices if 0 <= idx < len(available)])
            except ValueError:
                print(f"{Colors.WARNING}Invalid selection. No additional workflows will be added.{Colors.ENDC}")
        return selected_cmds

# --- Core Generator Class ---

class TruPromptGenerator:
    def __init__(self, agency_data: Dict, additional_workflows: List[str], custom_signature: str = None):
        self.agency_data = agency_data
        self.rms_name = self.agency_data.get('rms_name', 'Default')
        self.rms_config = RMS_CONFIG.get(self.rms_name, RMS_CONFIG["Default"])
        self.custom_signature = custom_signature
        selector = WorkflowSelector()
        self.all_workflow_cmds = selector.basic_commands + additional_workflows

    def generate_rms_notes_section(self) -> str:
        lines = ["### 2. RMS-Specific Notes and Procedures", "// Details on the operational environment, modules, and workflows for the RMS."]
        
        lines.extend(self.rms_config.get("general_notes", []))

        if "module_overview" in self.rms_config:
            overview = self.rms_config["module_overview"]
            lines.append(f"\n{overview['title']}")
            lines.append(overview['intro'])
            for module in overview['modules']:
                lines.append(f"[{module['name']}: {module['details']}]")

        if "prioritization_logic" in self.rms_config:
            logic = self.rms_config["prioritization_logic"]
            lines.append(f"\n{logic['title']}")
            lines.append(logic['intro'])
            lines.extend(logic.get('rules', []))

        user_notes = [f"[{note}]" for note in self.agency_data.get('rms_user_notes', []) if note]
        if user_notes:
            lines.append("\n// User-Provided Notes")
            lines.extend(user_notes)
            
        return "\n".join(lines)

    def generate_command_workflows_section(self) -> str:
        lines = ["### 8. Command Workflows", "Execute the following workflows when their corresponding command is received."]
        default_proc = "1. Navigate to the relevant module. 2. Input parameters. 3. Execute search. 4. Extract and verify data."
        wfs_to_include = [wf for wf in WORKFLOWS_DATABASE if wf["Full Command"] in self.all_workflow_cmds]

        for wf in wfs_to_include:
            command = wf["Full Command"]
            procedure = self.rms_config.get("procedures", {}).get(command, default_proc)
            lines.append(f"- command: {command}")
            lines.append(f"  short_form: {wf['Short Form']}")
            lines.append(f"  description: \"{wf['Description']}\"")
            lines.append(f"  procedure: \"{procedure}\"")
            lines.append("")
        return "\n".join(lines)

    def generate_prompt(self) -> str:
        template_vars = self.agency_data.copy()
        template_vars.setdefault('rms_username', 'NOT_PROVIDED')
        template_vars.setdefault('rms_password', 'NOT_PROVIDED')
        
        other_systems = self.agency_data.get('other_systems', {})
        other_systems_text = ""
        if other_systems:
            for name, creds in other_systems.items():
                other_systems_text += f"\n* **{name} Username**: `{creds.get('username', 'N/A')}`"
                other_systems_text += f"\n* **{name} Password**: `{creds.get('password', 'N/A')}`"
        template_vars['other_systems_text'] = other_systems_text

        template_vars['secure_signature'] = self.custom_signature if self.custom_signature else self.generate_secure_signature()

        return "\n\n".join([
            PROMPT_HEADER.format(**template_vars),
            AGENCY_CONFIG.format(**template_vars),
            self.generate_rms_notes_section(),
            CREDENTIAL_CONFIG_PLAINTEXT.format(**template_vars),
            MISSION_IDENTITY, SITUATIONAL_TOOL_USE, GUI_INTERACTION_PRINCIPLES,
            STANDARD_OPERATING_PROCEDURE, self.generate_command_workflows_section(),
            OUTPUT_SCHEMA, APPENDIX, SIGNATURE_POLICY.format(**template_vars)
        ])

    def generate_secure_signature(self) -> str:
        base_string = f"{self.agency_data['agency_abbr']}_dataPull_agent"
        
        # First salt and hash
        salt1 = ''.join(random.choices('0123456789abcdef', k=4))
        hashed1 = hashlib.sha256(f"{base_string}{salt1}".encode()).hexdigest()

        # Second salt and hash
        salt2 = ''.join(random.choices('0123456789abcdef', k=4))
        hashed2 = hashlib.sha256(f"{hashed1}{salt2}".encode()).hexdigest()

        return hashed2

# --- Setup Wizard and Main Execution ---

def run_setup():
    print(f"\n{Colors.BOLD}--- Prompt Generation Setup ---{Colors.ENDC}")
    
    agency_data = {
        'agency_name': input(f"{Colors.CYAN}Agency Name: {Colors.ENDC}").strip() or "Test Agency",
        'agency_abbr': input(f"{Colors.CYAN}Agency Abbreviation: {Colors.ENDC}").strip().upper() or "TA",
        'city': input(f"{Colors.CYAN}City: {Colors.ENDC}").strip() or "Testville",
        'county': input(f"{Colors.CYAN}County: {Colors.ENDC}").strip() or "Test County",
        'state': input(f"{Colors.CYAN}State: {Colors.ENDC}").strip() or "TS",
        'os_name': input(f"{Colors.CYAN}Operating System (default: Windows): {Colors.ENDC}").strip() or "Windows"
    }

    print(f"\n{Colors.BLUE}--- RMS System Selection ---{Colors.ENDC}")
    rms_list = [rms for rms in RMS_CONFIG if rms != "Default"]
    for i, rms in enumerate(rms_list, 1): print(f"{i}. {rms}")
    
    while 'rms_name' not in agency_data:
        try:
            choice_str = input(f"{Colors.CYAN}Select RMS or type a new name: {Colors.ENDC}").strip()
            if not choice_str: continue

            try:
                choice = int(choice_str)
                if 1 <= choice <= len(rms_list):
                    agency_data['rms_name'] = rms_list[choice - 1]
                else:
                    print(f"{Colors.WARNING}Invalid selection.{Colors.ENDC}")
            except ValueError:
                agency_data['rms_name'] = choice_str
                print(f"'{choice_str}' is not in the pre-configured list.")
                if input(f"{Colors.CYAN}Would you like to search Google for a user guide for '{choice_str}'? (y/n): {Colors.ENDC}").strip().lower() == 'y':
                    print(f"{Colors.GREEN}Please check your browser for the search results.{Colors.ENDC}")
                    # This is a placeholder for a potential web browser opening function
                    # For now, it just prints the URL.
                    search_query = f"https://www.google.com/search?q={agency_data['rms_name'].replace(' ', '+')}+user+guide"
                    print(f"Search URL: {search_query}")

        except (ValueError, IndexError): print(f"{Colors.WARNING}Please enter a valid number or name.{Colors.ENDC}")

    print(f"\n{Colors.BLUE}Enter any additional notes or quirks, one per line.{Colors.ENDC}")
    print(f"{Colors.BLUE}Prefix with a category (e.g., 'Quirk:'). Press Enter on an empty line to finish.{Colors.ENDC}")
    user_notes = []
    while True:
        note = input("> ").strip()
        if not note: break
        user_notes.append(note)
    agency_data['rms_user_notes'] = user_notes
    
    print(f"\n{Colors.BLUE}--- Credentials ---{Colors.ENDC}")
    agency_data['rms_username'] = input(f"{Colors.CYAN}RMS Username: {Colors.ENDC}").strip()
    agency_data['rms_password'] = input(f"{Colors.CYAN}RMS Password: {Colors.ENDC}").strip()
    
    other_systems = {}
    print(f"\n{Colors.BLUE}--- Additional System Credentials (optional) ---{Colors.ENDC}")
    while True:
        system_name = input(f"{Colors.CYAN}Other system name (or press Enter to finish): {Colors.ENDC}").strip()
        if not system_name:
            break
        username = input(f"  -> {system_name} Username: ").strip()
        password = input(f"  -> {system_name} Password: ").strip()
        other_systems[system_name] = {'username': username, 'password': password}
    agency_data['other_systems'] = other_systems
    
    # Ask about signature choice
    print(f"\n{Colors.BLUE}--- Signature Configuration ---{Colors.ENDC}")
    print(f"{Colors.CYAN}Choose signature option:{Colors.ENDC}")
    print(f"1. Generate a new signature (recommended)")
    print(f"2. Provide an existing signature")
    
    signature_choice = input(f"{Colors.CYAN}Enter choice (1 or 2): {Colors.ENDC}").strip()
    custom_signature = None
    
    if signature_choice == "2":
        custom_signature = input(f"{Colors.CYAN}Enter existing signature: {Colors.ENDC}").strip()
        if not custom_signature:
            print(f"{Colors.WARNING}No signature provided, generating new one.{Colors.ENDC}")
            custom_signature = None
        else:
            print(f"{Colors.GREEN}Using provided signature: {custom_signature[:16]}...{Colors.ENDC}")
    else:
        print(f"{Colors.GREEN}Will generate a new signature.{Colors.ENDC}")
    
    selector = WorkflowSelector()
    additional_workflows = selector.display_workflow_menu()

    print(f"\n{Colors.BOLD}Generating prompt for {agency_data['agency_name']}...{Colors.ENDC}")
    
    generator = TruPromptGenerator(agency_data, additional_workflows, custom_signature)
    final_prompt = generator.generate_prompt()

    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"{agency_data['agency_abbr']}_truPrompt_v7.0.txt")

    with open(filename, 'w', encoding='utf-8') as f: f.write(final_prompt)
    print(f"\n{Colors.GREEN}SUCCESS! Prompt generated successfully.{Colors.ENDC}")
    print(f"File saved to: {Colors.UNDERLINE}{filename}{Colors.ENDC}")

def main():
    try:
        display_banner()
        if not CRYPTOGRAPHY_AVAILABLE:
            print(f"{Colors.WARNING}WARNING: 'cryptography' library not found. Advanced security features are disabled.{Colors.ENDC}\n")
        
        run_setup()

    except KeyboardInterrupt:
        print(f"\n\n{Colors.FAIL}Operation cancelled. Exiting.{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.FAIL}An unexpected error occurred: {e}{Colors.ENDC}")
        traceback.print_exc()

if __name__ == "__main__":
    main()

