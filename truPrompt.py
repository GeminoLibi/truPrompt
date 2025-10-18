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
=======================================================================================                                                                                                         
                                                                                     
                          ________                                                    
                         `MMMMMMMb.                                                  
  /                       MM    `Mb                                            /     
 /M     ___  __ ___   ___ MM     MM ___  __   _____  ___  __    __  __ ____   /M     
/MMMMM  `MM 6MM `MM    MM MM     MM `MM 6MM  6MMMMMb `MM 6MMb  6MMb `M6MMMMb /MMMMM  
 MM      MM69 "  MM    MM MM    .M9  MM69 " 6M'   `Mb MM69 `MM69 `Mb MM'  `Mb MM     
 MM      MM'     MM    MM MMMMMMM9'  MM'    MM     MM MM'   MM'   MM MM    MM MM     
 MM      MM      MM    MM MM         MM     MM     MM MM    MM    MM MM    MM MM     
 MM      MM      MM    MM MM         MM     MM     MM MM    MM    MM MM    MM MM     
 YM.  ,  MM      YM.   MM MM         MM     YM.   ,M9 MM    MM    MM MM.  ,M9 YM.  , 
  YMMM9 _MM_      YMMM9MM_MM_       _MM_     YMMMMM9 _MM_  _MM_  _MM_MMYMMM9   YMMM9 
                                                                     MM              
                                                                     MM              
                                                                    _MM_                                      

 
"{}"

=======================================================================================
"""

MOTIVATIONAL_QUOTES = [
    "The best way to predict the future is to create it. - Peter Drucker",
    "Innovation distinguishes between a leader and a follower. - Steve Jobs",
    "The only way to do great work is to love what you do. - Steve Jobs",
    "When something is important enough, you do it even if the odds are not in your favor. - Elon Musk",
    "Data is the new oil. - Clive Humby",
    "The goal is to turn data into information, and information into insight. - Carly Fiorina",
    "The way to get started is to quit talking and begin doing. - Walt Disney",
    "Don't stop when you're tired. Stop when you're done.",
    "Do something today that your future self will thank you for.",
    "The only impossible journey is the one you never begin. - Tony Robbins",
    "In the middle of difficulty lies opportunity. - Albert Einstein",
    "Do or do not, there is no try. - Yoda (Star Wars)",
    "The greatest teacher, failure is. - Yoda (Star Wars)",
    "It is our choices, Harry, that show what we truly are, far more than our abilities. - Albus Dumbledore (Harry Potter)",
    "With great power comes great responsibility. - Uncle Ben (Spider-Man)",
    "Why do we fall? So we can learn to pick ourselves up. - Alfred Pennyworth (Batman)",
    "It's not who I am underneath, but what I do that defines me. - Batman",
    "I can do this all day. - Captain America (MCU)",
    "Never tell me the odds! - Han Solo (Star Wars)",
    "Knowing is not enough; we must apply. Wishing is not enough; we must do. - Johann Wolfgang von Goethe",
    "To thine own self be true. - William Shakespeare",
    "Go confidently in the direction of your dreams. Live the life you have imagined. - Henry David Thoreau",
    "I know nothing except the fact of my ignorance. - Socrates",
    "If you will not speak of the future, you have no future. - Saint Augustine",
    "The mind is its own place, and in itself can make a heaven of hell, a hell of heaven. - John Milton",
    "You have brains in your head. You have feet in your shoes. You can steer yourself any direction you choose. - Dr. Seuss",
    "The greatest glory in living lies not in never falling, but in rising every time we fall. - Nelson Mandela",
    "The journey of a thousand miles begins with a single step. - Lao Tzu",
    "The mind is everything. What you think you become. - Buddha",
    "We are what our thoughts have made us; so take care about what you think. - Swami Vivekananda",
    "When you seek, you will find. - Jesus of Nazareth",
    "Trust in the Lord with all your heart, and lean not on your own understanding. - Proverbs 3:5",
    "There is only one God, and His Name is Truth. - Guru Nanak Dev",
    "O son of man! Transgress not the bounds of justice, and refrain from all injustice. - Baháʼu'lláh",
    "Seek knowledge from the cradle to the grave. - Prophet Muhammad",
    "The water that flows in the river is the water of the next generation. - Shinto Philosophy",
    "Do not let the shadows of the past cloud the dawn of the future. - Norse Mythology",
    "A journey is not complete until the lesson is learned. - Tribal Proverb",
    "There is no fate but what we make. - Kyle Reese (The Terminator)",
    "The only true wisdom is in knowing you know nothing. - Socrates",
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
* Always verify data before submission.
* **TRUASSIST INTEGRATION**: You MUST deliver the full response directly to TruAssist in JSON format. Do NOT create files unless absolutely necessary for logging purposes.
* **OUTPUT DELIVERY**: All responses must be returned as JSON using the required output schema. TruAssist expects direct data delivery, not file creation.
* **SEARCH ENGINE PROHIBITION**: You are PROHIBITED from using any search engines (Google, Bing, DuckDuckGo, etc.). For OSINT information, use the OSINT framework to find appropriate tools or databases."""

SITUATIONAL_TOOL_USE = """### 5. Situational Tool Use & Logic
* **Scenario 1: Internal Data Retrieval** (`_PERSON_LOOKUP`, `_CASE_LOOKUP`, etc.)
    * **Preferred Tool**: **Direct GUI Interaction** with the RMS.
    * **Rationale**: The requested data is located exclusively within the RMS.
* **Scenario 2: External Information Gathering (OSINT)**
    * **Preferred Tool**: **Web Browser navigating to `https://osintframework.com/`**.
    * **Rationale**: This framework provides a structured map of tools. Start here to identify the best resources.
    * **PROHIBITED**: Do NOT use search engines (Google, Bing, DuckDuckGo, etc.). Use the OSINT framework to locate specific tools and databases.
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
* Phase 4: Report Generation (Compile JSON for TruAssist delivery).
* Phase 5: Synthesis and Reset (Deliver JSON response directly to TruAssist).
* Phase 6: Cleanup and Retention (Close windows, log activity - minimal file creation)."""

OUTPUT_SCHEMA = """### 9. Required Output Schema and TruAssist Delivery
**CRITICAL**: All responses MUST be delivered directly to TruAssist in JSON format. Do NOT create files.

Required JSON Format:
{{
  "reportMetadata": {{ "rfiCommand": "string", "status": "SUCCESS | FAILURE", "summary": "Natural language summary." }},
  "dataPayload": [ {{ "recordID": "string", "recordType": "string", "extractedData": {{}} }}]
}}

**TruAssist Integration Requirements**:
* Deliver complete responses directly to TruAssist interface
* Use JSON format exclusively for all data delivery
* Only create files for essential logging (not for data delivery)
* Ensure all extracted data is included in the JSON response
* Report status as "SUCCESS" or "FAILURE" based on data retrieval results"""

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
    3. If the RMS is the issue, use the OSINT framework to locate RMS-specific documentation and user guides.
    4. If an action fails more than 5 times, log the persistent failure, describe the attempted solutions, and move to the next task.
* **OSINT Information Gathering**:
    * **REQUIRED**: Use the OSINT framework (https://osintframework.com/) to locate appropriate tools and databases.
    * **PROHIBITED**: Do NOT use search engines (Google, Bing, DuckDuckGo, etc.) for OSINT research.
    * **Process**: Navigate to OSINT framework → Select relevant category → Use recommended tools/databases."""

SIGNATURE_POLICY = """### 11. Signature and Documentation Policy
* **Secure Signature**: `{secure_signature}`
* **CRITICAL RULE**: You MUST apply this signature to any and all documents, reports, or logs that you create on the host system. This ensures authenticity and auditability."""


# --- DATABASES ---

WORKFLOWS_DATABASE = [
    {"Full Command": "_UNKNOWN_QUERY_NLP|$Q_TXT:", "Short Form": "_UQN", "Description": "Handle an unformatted query by inferring user intent.", "Procedure": "1. Parse intent. 2. Develop Plan of Action. 3. Conduct Plan. 4. Verify intent fulfilled."},
    {"Full Command": "_PERSON_LOOKUP|$LN|$FN:", "Short Form": "_PRL", "Description": "Search for a person by last name and first name.", "Procedure": "1. Navigate to the relevant module. 2. Input parameters. 3. Execute search. 4. Extract and verify data.", "Flags": "-warrants (include deliberate wanted check)"},
    {"Full Command": "_CASE_LOOKUP|$CN:", "Short Form": "_CL", "Description": "Search for a case or incident by its number.", "Procedure": "1. Navigate to the relevant module. 2. Input parameters. 3. Execute search. 4. Extract and verify data.", "Flags": "-narrative (detailed narrative extraction)"},
    {"Full Command": "_VEHICLE_LOOKUP|$VIN|$plate|$NIC|$make|$model|$year:", "Short Form": "_VL", "Description": "Search for vehicle information using a VIN.", "Procedure": "1. Navigate to the relevant module. 2. Input parameters. 3. Execute search. 4. Extract and verify data."},
    {"Full Command": "_PROPERTY_LOOKUP|$IDESC|$SNUM:", "Short Form": "_PL", "Description": "Query for stolen or lost property.", "Procedure": "1. Navigate to the relevant module. 2. Input parameters. 3. Execute search. 4. Extract and verify data."},
    {"Full Command": "_ADDRESS_LOOKUP|$HN|$ST:", "Short Form": "_AL", "Description": "Search for an address by house number and street name.", "Procedure": "1. Navigate to the relevant module. 2. Input parameters. 3. Execute search. 4. Extract and verify data."},
    {"Full Command": "_ADDRESS_FULL_REPORT|$ADDRESS:", "Short Form": "_AFR", "Description": "Generate comprehensive report for an address consisting of _BATCH|_AL|_AC|_AP|_AV|_AW|_AH|_OL", "Procedure": "1. Navigate to the relevant module. 2. Input parameters. 3. Execute search. 4. Extract and verify data."},
    {"Full Command": "_ADDRESS_CFS_HISTORY|$ADDRESS|$DATE_RANGE:", "Short Form": "_AC", "Description": "Retrieve Calls for Service (CFS) history at an address.", "Procedure": "1. Navigate to the relevant module. 2. Input parameters. 3. Execute search. 4. Extract and verify data."},
    {"Full Command": "_ADDRESS_PERSONS|$ADDRESS:", "Short Form": "_AP", "Description": "List all persons associated with an address.", "Procedure": "1. Navigate to the relevant module. 2. Input parameters. 3. Execute search. 4. Extract and verify data."},
    {"Full Command": "_ADDRESS_VEHICLES|$ADDRESS:", "Short Form": "_AV", "Description": "List all vehicles associated with an address.", "Procedure": "1. Navigate to the relevant module. 2. Input parameters. 3. Execute search. 4. Extract and verify data."},
    {"Full Command": "_ADDRESS_WEAPONS|$ADDRESS:", "Short Form": "_AW", "Description": "Find weapon information associated with an address.", "Procedure": "1. Navigate to the relevant module. 2. Input parameters. 3. Execute search. 4. Extract and verify data."},
    {"Full Command": "_ADDRESS_HAZARDS|$ADDRESS:", "Short Form": "_AH", "Description": "Find premise hazards or officer safety notes for an address.", "Procedure": "1. Navigate to the relevant module. 2. Input parameters. 3. Execute search. 4. Extract and verify data."},
    {"Full Command": "_OSINT_LOOKUP|$LN|$FN|$phone|$address|$company|$email|$domain|$IP|$product|$username|$id_num:", "Short Form": "_OL", "Description": "Perform a comprehensive OSINT search for various data types.", "Procedure": "1. Navigate to the relevant module. 2. Input parameters. 3. Execute search. 4. Extract and verify data.", "Flags": "--associates [1, 2, 3] (Also look for associates at various informational depths. Default: 1)"},
    {"Full Command": "_DIAGNOSTIC_INPUT_CHECK|$mode:", "Short Form": "_DIC", "Description": "Verify keyboard and mouse input mappings.", "Procedure": "1. Navigate to the relevant module. 2. Input parameters. 3. Execute search. 4. Extract and verify data.", "Modes": "full (test all possible inputs), standard (lmb, rmb, mmb, return, escape, shift, caps lock, tab, alt, super, del, backspace, home, pgup, pgdn, end, ins, home, num lock, [a-z] [0-9] [-   [];',./\\`]), typing ([a-z] [0-9] [-[];',./\\`]), system (lmb, rmb, mmb, return, escape, shift, caps lock, tab, alt, super, del, backspace, home, pgup, pgdn, end, ins, home, num lock), mouse (lmb, rmb, mmb, mouse_move, scroll)"},
    {"Full Command": "_EXPLORE_RMS:", "Short Form": "_ER", "Description": "Heuristically explore an unknown RMS GUI.", "Procedure": "1. Navigate to the relevant module. 2. Input parameters. 3. Execute search. 4. Extract and verify data."},
    {"Full Command": "_BATCH|$CMD1;$CMD2;$CMD3:", "Short Form": "_BATCH", "Description": "Execute multiple commands sequentially.", "Procedure": "1. Navigate to the relevant module. 2. Input parameters. 3. Execute search. 4. Extract and verify data."}
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
            "_UNKNOWN_QUERY_NLP|$Q_TXT:", "_PERSON_LOOKUP|$LN|$FN:", "_CASE_LOOKUP|$CN:",
            "_VEHICLE_LOOKUP|$VIN|$plate|$NIC|$make|$model|$year:", "_PROPERTY_LOOKUP|$IDESC|$SNUM:",
            "_ADDRESS_LOOKUP|$HN|$ST:", "_ADDRESS_FULL_REPORT|$ADDRESS:", "_ADDRESS_CFS_HISTORY|$ADDRESS|$DATE_RANGE:",
            "_ADDRESS_PERSONS|$ADDRESS:", "_ADDRESS_VEHICLES|$ADDRESS:", "_ADDRESS_WEAPONS|$ADDRESS:",
            "_ADDRESS_HAZARDS|$ADDRESS:", "_OSINT_LOOKUP|$LN|$FN|$phone|$address|$company|$email|$domain|$IP|$product|$username|$id_num:",
            "_DIAGNOSTIC_INPUT_CHECK|$mode:", "_EXPLORE_RMS:", "_BATCH|$CMD1;$CMD2;$CMD3:"
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
    lines = [
        "### 8. Command Workflows", 
        "Execute the following workflows when their corresponding command is received.", 
        "# Global Flags",
        "--narrative, -n: extract detailed narratives and summarize",
        "--information-degree <num>, -i <num>: extract at more or less detailed information tiers. <1> = immediate (top level info -- focus solely on the basic information about the target), <2> = incident (contextual information about the target), <3> = secondary (deeper information about associations with other data in the system),",
        "--debug-vvv, -d: provide a detailed debug report after workflow completes",
        "--unformatted-context <string>, -u <string>: user provides additional information that should be included in the workflow that does not fit in the structure. Ex: _PRL|Smith|David -u 'DOB: 1/01/2001'",
        "--do-it-now, -din: parse the user request and complete to the fullest extent possible given 1) user intent and 2) resources available. May be off topic.",
        "--tell-me-now, -tmn: parse the user request and determine what information they are requesting. May be off topic. Answer completely and to the fullest extent possible given 1) user intent and 2) resources available.",
        "--find-me-anything, -fma: If information is not found in the RMS, perform OSINT lookups, check local news sites, and find any information possible about the target.",
        "--prompt-improvement, -pi: Information retrieved is unimportant. Deliver recommended prompt improvements given the specific workflow execute, IE: more detailed procedure sections, verbiage adjustments, additional system notes, etc. Format exactly as they should be input into the prompt.",
    ]
        default_proc = "1. Navigate to the relevant module. 2. Input parameters. 3. Execute search. 4. Extract and verify data."
        wfs_to_include = [wf for wf in WORKFLOWS_DATABASE if wf["Full Command"] in self.all_workflow_cmds]

        for wf in wfs_to_include:
            command = wf["Full Command"]
            # Use RMS-specific procedure if it exists and differs from standard, otherwise use workflow's procedure
            rms_procedure = self.rms_config.get("procedures", {}).get(command)
            if rms_procedure and rms_procedure != default_proc:
                procedure = rms_procedure
            else:
                procedure = wf.get("Procedure", default_proc)
            
            lines.append(f"- command: {command}")
            lines.append(f"  short_form: {wf['Short Form']}")
            lines.append(f"  description: \"{wf['Description']}\"")
            lines.append(f"  procedure: \"{procedure}\"")
            
            # Add flags if they exist
            if "Flags" in wf and wf["Flags"]:
                lines.append(f"  flags: {wf['Flags']}")
            
            # Add modes if they exist
            if "Modes" in wf and wf["Modes"]:
                lines.append(f"  modes: \"{wf['Modes']}\"")
            
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

# --- Auto-Generation from Agency Data ---

def load_agency_data():
    """Load existing agency data from JSON file"""
    try:
        with open('outputs/agency_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"{Colors.WARNING}Agency data file not found. Run the interactive setup instead.{Colors.ENDC}")
        return None
    except Exception as e:
        print(f"{Colors.FAIL}Error loading agency data: {e}{Colors.ENDC}")
        return None

def list_available_agencies(agency_data):
    """List all available agencies from the JSON data"""
    if not agency_data or 'agencies' not in agency_data:
        return []
    
    agencies = []
    for abbr, data in agency_data['agencies'].items():
        agencies.append({
            'abbr': abbr,
            'name': data.get('agency_name', 'Unknown'),
            'city': data.get('city', 'Unknown'),
            'state': data.get('state', 'Unknown'),
            'rms': data.get('rms_name', 'Unknown')
        })
    
    return sorted(agencies, key=lambda x: x['name'])

def auto_generate_from_agency_data():
    """Auto-generate prompts using existing agency data"""
    print(f"\n{Colors.BOLD}--- Auto-Generate from Agency Data ---{Colors.ENDC}")
    
    agency_data = load_agency_data()
    if not agency_data:
        return False
    
    available_agencies = list_available_agencies(agency_data)
    if not available_agencies:
        print(f"{Colors.WARNING}No agencies found in agency data.{Colors.ENDC}")
        return False
    
    print(f"\n{Colors.BLUE}Available Agencies:{Colors.ENDC}")
    for i, agency in enumerate(available_agencies, 1):
        print(f"{i:2d}. {agency['name']} ({agency['abbr']}) - {agency['city']}, {agency['state']} - {agency['rms']}")
    
    print(f"\n{Colors.CYAN}Options:{Colors.ENDC}")
    print("1. Generate for specific agency")
    print("2. Generate for all agencies")
    print("3. Return to main menu")
    
    choice = input(f"{Colors.CYAN}Select option (1-3): {Colors.ENDC}").strip()
    
    if choice == "1":
        return generate_specific_agency(agency_data, available_agencies)
    elif choice == "2":
        return generate_all_agencies(agency_data, available_agencies)
    elif choice == "3":
        return False
    else:
        print(f"{Colors.WARNING}Invalid choice.{Colors.ENDC}")
        return False

def generate_specific_agency(agency_data, available_agencies):
    """Generate prompt for a specific agency"""
    try:
        agency_num = int(input(f"{Colors.CYAN}Enter agency number: {Colors.ENDC}").strip())
        if 1 <= agency_num <= len(available_agencies):
            selected_agency = available_agencies[agency_num - 1]
            agency_abbr = selected_agency['abbr']
            
            # Get the full agency data
            full_agency_data = agency_data['agencies'][agency_abbr]
            
            print(f"\n{Colors.GREEN}Generating prompt for {full_agency_data['agency_name']}...{Colors.ENDC}")
            
            # Ask about signature choice
            print(f"\n{Colors.BLUE}--- Signature Configuration ---{Colors.ENDC}")
            print(f"{Colors.CYAN}Choose signature option:{Colors.ENDC}")
            print(f"1. Use existing signature: {full_agency_data.get('signature', 'None')[:16]}...")
            print(f"2. Generate a new signature")
            
            signature_choice = input(f"{Colors.CYAN}Enter choice (1 or 2): {Colors.ENDC}").strip()
            custom_signature = None
            
            if signature_choice == "1":
                custom_signature = full_agency_data.get('signature')
                if custom_signature:
                    print(f"{Colors.GREEN}Using existing signature: {custom_signature[:16]}...{Colors.ENDC}")
                else:
                    print(f"{Colors.WARNING}No existing signature found, generating new one.{Colors.ENDC}")
                    custom_signature = None
            else:
                print(f"{Colors.GREEN}Will generate a new signature.{Colors.ENDC}")
            
            # Get workflow selection
            selector = WorkflowSelector()
            additional_workflows = selector.display_workflow_menu()
            
            # Generate the prompt
            generator = TruPromptGenerator(full_agency_data, additional_workflows, custom_signature)
            final_prompt = generator.generate_prompt()
            
            # Save the prompt
            filename = f"outputs/{agency_abbr}_truPrompt_v7.0.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(final_prompt)
            
            print(f"\n{Colors.GREEN}Prompt generated successfully!{Colors.ENDC}")
            print(f"File saved to: {Colors.UNDERLINE}{filename}{Colors.ENDC}")
            return True
        else:
            print(f"{Colors.WARNING}Invalid agency number.{Colors.ENDC}")
            return False
    except ValueError:
        print(f"{Colors.WARNING}Please enter a valid number.{Colors.ENDC}")
        return False

def generate_all_agencies(agency_data, available_agencies):
    """Generate prompts for all agencies"""
    print(f"\n{Colors.BLUE}--- Generate All Agencies ---{Colors.ENDC}")
    print(f"{Colors.CYAN}This will generate prompts for {len(available_agencies)} agencies.{Colors.ENDC}")
    
    confirm = input(f"{Colors.CYAN}Continue? (y/n): {Colors.ENDC}").strip().lower()
    if confirm != 'y':
        print(f"{Colors.WARNING}Operation cancelled.{Colors.ENDC}")
        return False
    
    # Ask about signature choice for all
    print(f"\n{Colors.BLUE}--- Signature Configuration ---{Colors.ENDC}")
    print(f"{Colors.CYAN}Choose signature option for all agencies:{Colors.ENDC}")
    print(f"1. Use existing signatures where available")
    print(f"2. Generate new signatures for all")
    
    signature_choice = input(f"{Colors.CYAN}Enter choice (1 or 2): {Colors.ENDC}").strip()
    use_existing_signatures = signature_choice == "1"
    
    # Get workflow selection once for all
    selector = WorkflowSelector()
    additional_workflows = selector.display_workflow_menu()
    
    success_count = 0
    for agency in available_agencies:
        try:
            agency_abbr = agency['abbr']
            full_agency_data = agency_data['agencies'][agency_abbr]
            
            print(f"\n{Colors.BLUE}Generating for {full_agency_data['agency_name']}...{Colors.ENDC}")
            
            # Determine signature
            custom_signature = None
            if use_existing_signatures:
                custom_signature = full_agency_data.get('signature')
            
            # Generate the prompt
            generator = TruPromptGenerator(full_agency_data, additional_workflows, custom_signature)
            final_prompt = generator.generate_prompt()
            
            # Save the prompt
            filename = f"outputs/{agency_abbr}_truPrompt_v7.0.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(final_prompt)
            
            print(f"{Colors.GREEN}✓ Generated: {filename}{Colors.ENDC}")
            success_count += 1
            
        except Exception as e:
            print(f"{Colors.FAIL}✗ Failed for {agency['name']}: {e}{Colors.ENDC}")
    
    print(f"\n{Colors.GREEN}Batch generation complete!{Colors.ENDC}")
    print(f"Successfully generated: {success_count}/{len(available_agencies)} prompts")
    return True

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
                if input(f"{Colors.CYAN}Would you like guidance on finding documentation for '{choice_str}' via OSINT framework? (y/n): {Colors.ENDC}").strip().lower() == 'y':
                    print(f"{Colors.GREEN}Use the OSINT framework (https://osintframework.com/) to locate RMS-specific documentation and user guides.{Colors.ENDC}")
                    print(f"{Colors.BLUE}Navigate to the OSINT framework → Select relevant category → Look for documentation resources.{Colors.ENDC}")
                    # Note: Search engines are prohibited per TruAssist integration requirements

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
        
        while True:
            print(f"\n{Colors.BOLD}--- truPrompt v7.0 Main Menu ---{Colors.ENDC}")
            print(f"{Colors.CYAN}Select an option:{Colors.ENDC}")
            print(f"1. Interactive Setup (New Agency)")
            print(f"2. Auto-Generate from Agency Data")
            print(f"3. Exit")
            
            choice = input(f"{Colors.CYAN}Enter choice (1-3): {Colors.ENDC}").strip()
            
            if choice == "1":
                run_setup()
            elif choice == "2":
                auto_generate_from_agency_data()
            elif choice == "3":
                print(f"{Colors.GREEN}Goodbye!{Colors.ENDC}")
                break
            else:
                print(f"{Colors.WARNING}Invalid choice. Please select 1, 2, or 3.{Colors.ENDC}")

    except KeyboardInterrupt:
        print(f"\n\n{Colors.FAIL}Operation cancelled. Exiting.{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.FAIL}An unexpected error occurred: {e}{Colors.ENDC}")
        traceback.print_exc()

if __name__ == "__main__":
    main()



