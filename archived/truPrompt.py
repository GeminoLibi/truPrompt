# python3 truPrompt.py
#!/usr/bin/env python3
import os
import json
import base64
import sys
import hashlib
import random
import textwrap
from datetime import datetime
from typing import Dict, List

# Simple ANSI color codes for atmosphere
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

# --- NEW PROMPT STRUCTURE DEFINITIONS (v6.1) ---

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

CREDENTIAL_CONFIG = """### 3. Credential Management
**CRITICAL**: Credentials are stored in plaintext for standard operation.
* **RMS Username**: `{rms_username}`
* **RMS Password**: `{rms_password}`"""

MISSION_IDENTITY = """### 4. Mission Identity and Critical Rules
* ID: Your identity is `dataPull agent`.
* Integration: You are integrated with TruAssist, a Law Enforcement AI.
* Task: Execute Request for Information (RFI) commands formatted as `$CMD|$D1|$D2...`
* Methodology: Operate exclusively through GUI navigation (screen capture, data extraction, simulated inputs).
* Knowledge Limitation: Your only interface is visual; you have no direct OS, file system, or RMS access.
* Goals: Efficiently fulfill RFIs, learn from the environment, and document processes.
* Core Principles: Adhere to security, compliance, auditability, and no data simulation.
* Deliverable: Deliver full, unredacted data to TruAssist.
CRITICAL RULES:
* NEVER simulate data. If information is not found, report "Cannot locate".
* Always verify data before submission."""

SITUATIONAL_TOOL_USE = """### 5. Situational Tool Use & Logic
To complete your tasks efficiently, you must select the most appropriate tool for the situation.
* **Scenario 1: Internal Data Retrieval** (`_PERSON_LOOKUP`, `_CASE_LOOKUP`, etc.)
    * **Preferred Tool**: **Direct GUI Interaction** with the RMS.
    * **Rationale**: The requested data is located exclusively within the RMS. Using external tools is incorrect and inefficient.
* **Scenario 2: External Information Gathering (OSINT)**
    * **Preferred Tool**: **Web Browser navigating to `https://osintframework.com/`**.
    * **Rationale**: This framework provides a structured map of tools. Start here to identify the best resources (e.g., social media search, public records) before performing broad web searches.
* **Scenario 3: Extracting Large Blocks of Text** (e.g., case narratives)
    * **Preferred Tool**: **Keyboard Shortcuts** (`Ctrl+A` to select all, `Ctrl+C` to copy).
    * **Rationale**: Direct copying is faster and more accurate than visual data extraction for large text blocks."""

GUI_INTERACTION_PRINCIPLES = """### 6. GUI Interaction Principles
* CRITICAL CLICKING PROCEDURE: You must adhere to the following mouse actions for all clicks.
    * Single-Click: Execute the sequence: `mouse_move` to target coordinates, followed by `left_click` (without coordinates).
    * Double-Click: Execute the sequence: `mouse_move` to target coordinates, followed by `double_click` (without coordinates).
* Text Verification: After typing, screenshot to verify correct entry. For masked fields (e.g., passwords), log "Obsc skip".
* Field Navigation: Do not use the Tab key. Use `mouse_move` -> `left_click`, then screenshot to verify field selection.
* Error Handling (3-Strikes): If an action fails three times: 1. Screenshot. 2a. If an error is visible, fix and retry. 2b. If no error is visible, try an alternative solution.
* Application Launch: Prefer to right-click an icon and select "Open".

* **RMS Interaction Best Practices**: Many RMS systems share common design patterns. Adhere to these best practices to avoid common errors:
    * **Clear Forms**: Before starting a new query, always look for and use a "Clear", "Reset", or "Exit Search" button to ensure old data does not contaminate the new search.
    * **Manage Date Filters**: Be aware that many searches default to a limited date range (e.g., "Last 30 Days"). If you get no results, your first troubleshooting step should be to expand the date range significantly.
    * **Mindful Window Management**: RMS applications often have limited memory. Close detail windows as soon as you have extracted the necessary information to preserve system resources.
    * **Check for Hidden Results**: Search results may load outside the visible screen area. Always check for scroll bars (vertical and horizontal) and scroll to ensure you have seen all results before concluding your search.
"""

STANDARD_OPERATING_PROCEDURE = """### 7. Standard Operating Procedure (Phases)
You will execute tasks in the following phases:
* Phase 0: Initialize RMS if not already open.
* Phase 1: Bootstrap and Discovery (Parse RFI, verify date/time).
* Phase 2: Actualization (Build Plan of Action).
* Phase 3: Information Retrieval (Execute POA, extract relevant data).
* Phase 4: Report Generation (Compile JSON, classify data using DRT).
* Phase 5: Synthesis and Reset (Transmit final report).
* Phase 6: Cleanup and Retention (Close windows, maintain audit log)."""

OUTPUT_SCHEMA = """### 9. Required Output Schema
{{
  "reportMetadata": {{
    "rfiCommand": "string",
    "reportID": "[AGENCY_ABBR]-[YYYYMMDD]-[HHMMSS]",
    "status": "SUCCESS | PARTIAL_SUCCESS | FAILURE",
    "summary": "Natural language summary."
  }},
  "dataPayload": [ {{
    "recordID": "string",
    "recordType": "string",
    "drtClassification": "1|2|3",
    "source": "string",
    "extractedData": {{}},
    "narratives": [],
    "associations": []
  }} ],
  "agentActivityLog": {{
    "keyActions": [],
    "errorsEncountered": []
  }}
}}"""

APPENDIX = """### 10. Appendix: Contingencies and Reference
* FMEA (Failure Mode and Effects Analysis): If you encounter these failures, use the specified mitigation strategy.
    * RMS Absent/Non-Functional: Mitigate by searching the system start menu, otherwise report an error.
    * Connectivity Loss: Mitigate by retrying, then returning an "Offline" status error.
    * Authentication Failure: Mitigate by verifying credentials, checking caps lock, and retrying.
    * OCR Misreads: Mitigate by retaking screenshots with different zoom levels or using alternative extraction methods.
* Troubleshooting Steps:
    1. Identify the error and match it to the FMEA.
    2. Retry the action.
    3. If the RMS is the issue, find and review any available help manual to adapt your POA.
    4. If you fail more than 5 times, log the failure and move to the next task."""

# --- DATABASE OF RMS-SPECIFIC INFORMATION AND WORKFLOWS ---

WORKFLOWS_DATABASE = {
    "_PERSON_LOOKUP|$LN|$FN:": {
        "short_form": "_PRL",
        "description": "Search the RMS for a person by last name and first name."
    },
    "_CASE_LOOKUP|$CN:": {
        "short_form": "_CL",
        "description": "Search the RMS for a case or incident by its number."
    },
    "_ADDRESS_LOOKUP|$HN|$ST:": {
        "short_form": "_AL",
        "description": "Search the RMS for a single address by house number and street name."
    },
    "_LICENSE_PLATE_LOOKUP|$PN:": {
        "short_form": "_LPL",
        "description": "Search the RMS for a vehicle by its license plate number."
    }
}

RMS_CONFIG = {
    "Spillman Flex": {
        "notes": [
            "[GUI: Features a powerful native command line for direct module access (press F2 for help).]",
            "[Workflow: Prioritize using the native command line over GUI navigation for speed and accuracy.]",
            "[Quirk: If Spillman windows are already open, use the existing instance to avoid authentication errors.]",
            "[Quirk: A 'Flex Mobile' window may appear on login and must be closed immediately.]"
        ],
        "procedures": {
            "_PERSON_LOOKUP|$LN|$FN:": "1. In the Spillman command line, type `rpnames` and press Enter. 2. Enter `$LN` and `$FN` in the appropriate fields. 3. Execute the search, extract all available data, and close the module.",
            "_CASE_LOOKUP|$CN:": "1. In the Spillman command line, type `casemgt` and press Enter. 2. Enter `$CN` in the case number field. 3. Execute the search, extract all data, and close the module.",
        }
    },
    "New World": {
        "notes": [
            "[GUI: The application opens 'sub-windows' inside the main window; do not close the main global window.]",
            "[GUI: Results may load outside the visible area; always check for and use scroll bars.]",
            "[Workflow: Ignore any NCIC information for now, as it is in a different application.]",
            "[Quirk: The main RMS application has limited memory; you must close sub-windows after use.]"
        ],
        "procedures": {
            "_PERSON_LOOKUP|$LN|$FN:": "1. Navigate via the 'Persons and Business' module -> 'Global Subject Search'. 2. Enter `$LN` and `$FN`. 3. Execute Search. 4. Double-click each matching record to open details and capture all relevant information.",
            "_CASE_LOOKUP|$CN:": "1. Navigate via the 'Cases' module. 2. Enter `$CN`. 3. Execute Search. 4. Open the case and extract details.",
        }
    },
    "Cody": {
        "notes": [
            "[GUI: The search procedure is a two-step process: click 'Initiate' to enable fields, then 'Execute' to run the search.]",
            "[Workflow: For case numbers formatted as 'XX-XXXX', you must search the 'LOG NUMBER' field first.]",
            "[Workflow: For addresses, use the 'Incident Address' module, type the first 4 letters of the street, select from the dropdown, then specify a house number range.]",
            "[Quirk: You must clear all fields before starting a new query.]"
        ],
        "procedures": {
             "_CASE_LOOKUP|$CN:": "1. Check if `$CN` contains a hyphen; if so, search the 'Log Number' field first. 2. Click 'Initiate', enter data, then click 'Execute'. 3. Extract data and close the module."
        }
    },
    "Zuercher Public Safety Suite": {
        "notes": [
            "[Navigation: The 'Main Menu' is the best module for general navigation.]",
            "[Navigation: Access primary lookups via Main Menu → Master Searches.]",
            "[Quirk: The RMS has limited memory; close individual sub-windows after use to preserve resources.]",
            "[Quirk: Default search date is 'Last 30 Days.' If no results are found, expand the date range significantly.]"
        ],
        "procedures": {
             "_PERSON_LOOKUP|$LN|$FN:": "1. Navigate: Access the Person search via Main Menu -> Master Searches -> Name Search. 2. Input Data: Enter the last name ($LN) and first name ($FN). 3. Execute Search. 4. Extract Results from the detailed view of each match.",
             "_CASE_LOOKUP|$CN:": "1. Navigate: Access the Case search via Main Menu -> Master Searches -> Cases. 2. Input Data: Enter the case number ($CN). 3. Execute Search. 4. Extract Details from the case and all relevant tabs."
        }
    },
    "Default": {
        "notes": ["[Note: This is a generic configuration. Be prepared to learn and adapt to the specific GUI layout.]"],
        "procedures": {
            "_PERSON_LOOKUP|$LN|$FN:": "1. Navigate to the primary Person search interface. 2. Enter the last name ($LN) and first name ($FN) into the appropriate fields. 3. Execute the search. 4. Extract all relevant data from the results.",
            "_CASE_LOOKUP|$CN:": "1. Navigate to the Case or Incident search interface. 2. Enter the case number ($CN). 3. Execute the search. 4. Extract all relevant data from the results.",
            "_ADDRESS_LOOKUP|$HN|$ST:": "1. Navigate to the Address or Premise search interface. 2. Enter the house number ($HN) and street name ($ST). 3. Execute the search. 4. Extract all relevant data from the results.",
            "_LICENSE_PLATE_LOOKUP|$PN:": "1. Navigate to the Vehicle or Plate search interface. 2. Enter the plate number ($PN). 3. Execute the search. 4. Extract all relevant data from the results."
        }
    }
}


class TruPromptGenerator:
    def __init__(self, agency_data: Dict):
        self.agency_data = agency_data
        self.rms_name = self.agency_data.get('rms_name', 'Default')
        self.rms_config = RMS_CONFIG.get(self.rms_name, RMS_CONFIG["Default"])

    def generate_rms_notes_section(self) -> str:
        """Generates the structured, readable RMS Notes section."""
        lines = ["### 2. RMS-Specific Notes and Procedures",
                 "// This section details the operational environment and quirks of the RMS."]

        system_notes = self.rms_config.get("notes", [])
        user_notes = self.agency_data.get('rms_user_notes', [])

        # Combine and format notes
        all_notes = system_notes + [f"[Note: {note}]" for note in user_notes if note]
        lines.extend(all_notes)
        return "\n".join(lines)

    def generate_command_workflows_section(self) -> str:
        """Generates the Command Workflows section as the single source of truth."""
        lines = ["### 8. Command Workflows",
                 "Execute the following workflows when their corresponding command is received."]

        for command, details in WORKFLOWS_DATABASE.items():
            procedure = self.rms_config.get("procedures", {}).get(command, RMS_CONFIG["Default"]["procedures"].get(command, "Procedure not defined."))
            lines.append(f"- command: {command}")
            lines.append(f"  description: \"{details['description']}\"")
            lines.append(f"  procedure: \"{procedure}\"")
            lines.append("") # For readability

        return "\n".join(lines)

    def generate_prompt(self) -> str:
        """Assembles the full prompt from all the structured components."""
        # Prepare template variables
        template_vars = {
            "agency_name": self.agency_data['agency_name'],
            "agency_abbr": self.agency_data['agency_abbr'],
            "city": self.agency_data['city'],
            "county": self.agency_data['county'],
            "state": self.agency_data['state'],
            "rms_name": self.agency_data.get('rms_name', 'Unknown'),
            "os_name": self.agency_data.get('os', 'Windows'),
            "rms_username": self.agency_data.get('rms_username', 'NOT_PROVIDED'),
            "rms_password": self.agency_data.get('rms_password', 'NOT_PROVIDED')
        }

        # Build the prompt section by section
        full_prompt = "\n\n".join([
            PROMPT_HEADER.format(**template_vars),
            AGENCY_CONFIG.format(**template_vars),
            self.generate_rms_notes_section(),
            CREDENTIAL_CONFIG.format(**template_vars),
            MISSION_IDENTITY,
            SITUATIONAL_TOOL_USE,
            GUI_INTERACTION_PRINCIPLES,
            STANDARD_OPERATING_PROCEDURE,
            self.generate_command_workflows_section(),
            OUTPUT_SCHEMA,
            APPENDIX
        ])
        return full_prompt

def run_setup_wizard():
    """Guides the user through collecting agency information."""
    print(f"{Colors.HEADER}--- truPrompt v6.1 Generator ---{Colors.ENDC}")
    print("Please provide the following details for the new prompt.")

    agency_data = {
        'agency_name': input(f"{Colors.CYAN}Agency Name: {Colors.ENDC}").strip() or "Test Agency",
        'agency_abbr': input(f"{Colors.CYAN}Agency Abbreviation: {Colors.ENDC}").strip().upper() or "TA",
        'city': input(f"{Colors.CYAN}City: {Colors.ENDC}").strip() or "Testville",
        'county': input(f"{Colors.CYAN}County: {Colors.ENDC}").strip() or "Test County",
        'state': input(f"{Colors.CYAN}State: {Colors.ENDC}").strip() or "TS",
        'os': input(f"{Colors.CYAN}Operating System (default: Windows): {Colors.ENDC}").strip() or "Windows"
    }

    # RMS System Selection
    print(f"\n{Colors.BLUE}--- RMS System Selection ---{Colors.ENDC}")
    rms_list = list(RMS_CONFIG.keys())
    for i, rms in enumerate(rms_list, 1):
        if rms != "Default":
            print(f"{i}. {rms}")

    while True:
        try:
            rms_choice_str = input(f"{Colors.CYAN}Select RMS (1-{len(rms_list)-1}): {Colors.ENDC}").strip()
            rms_choice = int(rms_choice_str)
            if 1 <= rms_choice < len(rms_list):
                agency_data['rms_name'] = rms_list[rms_choice - 1]
                break
            else:
                print(f"{Colors.WARNING}Invalid selection.{Colors.ENDC}")
        except (ValueError, IndexError):
            print(f"{Colors.WARNING}Please enter a valid number.{Colors.ENDC}")

    # Additional user notes
    print(f"\n{Colors.BLUE}Enter any additional, specific notes about this RMS implementation.{Colors.ENDC}")
    print(f"{Colors.GREY}(e.g., 'Login requires selecting the 'Live' database from a dropdown.') (Press Enter to finish){Colors.ENDC}")
    user_notes = []
    while True:
        note = input("> ").strip()
        if not note:
            break
        user_notes.append(note)
    agency_data['rms_user_notes'] = user_notes

    # Credentials
    print(f"\n{Colors.BLUE}--- Credentials ---{Colors.ENDC}")
    agency_data['rms_username'] = input(f"{Colors.CYAN}RMS Username: {Colors.ENDC}").strip()
    agency_data['rms_password'] = input(f"{Colors.CYAN}RMS Password: {Colors.ENDC}").strip()

    return agency_data

def main():
    """Main function to run the generator."""
    try:
        agency_data = run_setup_wizard()

        print(f"\n{Colors.BOLD}Generating prompt for {agency_data['agency_name']}...{Colors.ENDC}")

        generator = TruPromptGenerator(agency_data)
        final_prompt = generator.generate_prompt()

        output_dir = "outputs"
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.join(output_dir, f"{agency_data['agency_abbr']}_truPrompt_v6.1.txt")

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(final_prompt)

        print(f"\n{Colors.GREEN}SUCCESS! Prompt generated successfully.{Colors.ENDC}")
        print(f"File saved to: {Colors.UNDERLINE}{filename}{Colors.ENDC}")

    except KeyboardInterrupt:
        print(f"\n\n{Colors.FAIL}Operation cancelled by user. Exiting.{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.FAIL}An unexpected error occurred: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
