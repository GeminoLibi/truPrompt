#!/usr/bin/env python3
"""
truPrompt - Unified Agent Prompt Generator (v5.2 Synthesis)

A single-file solution for generating hyper-customized, secure AI agent prompts.
This script synthesizes best practices from multiple PromptGen versions into a single, robust generator.

Features:
- Interactive CLI for gathering agency, RMS, and workflow requirements.
- Three security models: Split-Secret (most secure), Simple Encryption (self-contained), and Plaintext.
- Optional Externalized Logic model (command library in a local file) for token efficiency.
- Intelligent, RMS-specific customizations for Spillman Flex, New World, Cody, and OneSolutionRMS.
- A comprehensive "Uber-Library" of workflows embedded directly in the script.
"""

import os
import json
import base64
import sys
from typing import Dict, List, Optional

# Attempt to import cryptography and handle potential installation
try:
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend
    from cryptography.fernet import Fernet
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False

# ============================================================================
# EMBEDDED UBER-LIBRARY OF WORKFLOWS
# ============================================================================

WORKFLOWS_DATABASE = [
    # Core & Initialization
    {"Full Command": "_RMS_LOGIN", "Short Form": "_RL", "Description": "Securely and correctly log into the specified RMS, handling any specific startup sequences."},
    {"Full Command": "_INITIATE|$start:", "Short Form": "_INIT", "Description": "Initialize the system for operation, ensuring all environmental checks are complete."},
    {"Full Command": "_UNKNOWN_QUERY_NLP|$Q_TXT:", "Short Form": "_UQN", "Description": "Handle an unformatted or natural language query by inferring user intent."},

    # Standard RMS & NCIC Lookups
    {"Full Command": "_PERSON_LOOKUP|$LN|$FN:", "Short Form": "_PRL", "Description": "Search the RMS for a person by last name and first name."},
    {"Full Command": "_CASE_LOOKUP|$CN:", "Short Form": "_CL", "Description": "Search the RMS for a case or incident by its number."},
    {"Full Command": "_LICENSE_PLATE_LOOKUP|$PN:", "Short Form": "_LPL", "Description": "Search the RMS for a vehicle by its license plate number."},
    {"Full Command": "_WARRANT_CHECK|$SID|$JUR:", "Short Form": "_WC", "Description": "Search for warrants on a subject within a jurisdiction."},
    {"Full Command": "_PROPERTY_SEARCH|$IDESC|$SNUM:", "Short Form": "_PS", "Description": "Query for stolen or lost property using a description and/or serial number."},

    # Expanded Address & Premises Workflows
    {"Full Command": "_ADDRESS_LOOKUP|$HN|$ST:", "Short Form": "_AL", "Description": "Search the RMS for a single address by house number and street name."},
    {"Full Command": "_ADDRESS_FULL_REPORT|$ADDRESS:", "Short Form": "_AFR", "Description": "Generate a comprehensive premises report for a single address."},
    {"Full Command": "_ADDRESS_CFS_HISTORY|$ADDRESS|$DATE_RANGE:", "Short Form": "_ACH", "Description": "Retrieve a summary of all Calls for Service (CFS) at an address."},
    {"Full Command": "_ADDRESS_KNOWN_PERSONS|$ADDRESS:", "Short Form": "_AKP", "Description": "List all persons previously associated with an address in the RMS."},
    {"Full Command": "_ADDRESS_VEHICLES|$ADDRESS:", "Short Form": "_AV", "Description": "List all vehicles registered or associated with an address in the RMS."},
    {"Full Command": "_ADDRESS_WEAPONS_INFO|$ADDRESS:", "Short Form": "_AWI", "Description": "Find any mention of weapons (registered or in reports) associated with an address."},
    {"Full Command": "_ADDRESS_HAZARDS|$ADDRESS:", "Short Form": "_AH", "Description": "Find any premise hazards, officer safety notes, or medical alerts for an address."},

    # OSINT & Web-Based Workflows
    {"Full Command": "_OSINT_PERSON_LOOKUP|$LN|$FN:", "Short Form": "_OPL", "Description": "Perform a comprehensive OSINT search for a person."},
    {"Full Command": "_OSINT_ASSOCIATES|$SNAM|$DEPTH:", "Short Form": "_OA", "Description": "Use OSINT to find associates of a subject from public records and social media."},
    {"Full Command": "_COPWARE_LOOKUP|$Question:", "Short Form": "_COP", "Description": "Search the COPWARE database to answer a natural language question."},
    
    # Utility, Diagnostic, and Maintenance Workflows
    {"Full Command": "_DIAGNOSTIC_INPUT_CHECK|$mode:", "Short Form": "_DIC", "Description": "Run a comprehensive diagnostic to verify keyboard and mouse input mappings."},
    {"Full Command": "_FORCE_FC|$mode:", "Short Form": "_FFC", "Description": "Force a re-run of the Function Check (FC) module with a specified scope."},
    {"Full Command": "_PURGE_FILES|$CONFIRM:", "Short Form": "_PURGE", "Description": "DANGER: Permanently delete all agent-related desktop files and empty the trash."},
    {"Full Command": "_EXPLORE_RMS|$USER|$PASS:", "Short Form": "_ER", "Description": "Heuristically explore an unknown RMS GUI to identify and map common modules."},
    {"Full Command": "_SELF_EVAL|$mode:", "Short Form": "_SE", "Description": "Perform a self-evaluation based on a specified mode (full, diag, prompt_anlyz, etc.)."},
    {"Full Command": "_NARRATIVE_EXTRACT|$CID:", "Short Form": "_NE", "Description": "Extract the full text of all narratives associated with a case ID from the RMS."},
    {"Full Command": "_FACIAL_RECOGNITION|$IMG_URL|$SNAM:", "Short Form": "_FR", "Description": "Query the RMS facial recognition database using an image."},
    {"Full Command": "_INCIDENT_REPORT|$DR|$LOC:", "Short Form": "_IR", "Description": "Search for incident reports within a date range at a specific location."}
]


# ============================================================================
# RMS-SPECIFIC CUSTOMIZATIONS
# ============================================================================

RMS_CONFIG = {
    "Spillman Flex": {
        "notes": "CRITICAL: If Spillman windows are already open on the desktop, DO NOT try to launch a new instance; use the existing interface to avoid authentication errors. This RMS features a powerful native command line for direct module access (press F2 for help), which MUST be prioritized over GUI navigation. When logging in, a 'Flex Mobile' window may appear and must be closed immediately. If prompted, you must select the 'live' database.",
        "workflows": {
            "_PERSON_LOOKUP|$LN|$FN:": "After logging into Spillman, locate the native command-line field. Type `rpnames` and press Enter. In the person search module, enter `$LN` and `$FN`, execute the search, extract all available data fields, and close the module.",
            "_CASE_LOOKUP|$CN:": "In the Spillman command line, type `casemgt` and press Enter. In the case management module, enter `$CN`, execute the search, extract all data, and close the module.",
            "_LICENSE_PLATE_LOOKUP|$PN:": "In the Spillman command line, type `vinhist` and press Enter. Enter `$PN`, execute the search, extract registered owner and vehicle details, and close the module.",
            "_ADDRESS_LOOKUP|$HN|$ST:": "In the Spillman command line, type `addr` and press Enter. In the address module, enter house number (`$HN`) and street (`$ST`), execute the search, extract premises details, and close the module."
        }
    },
    "New World": {
        "notes": "CRITICAL: For all NCIC-related queries (warrants, stolen property), you MUST use the separate LERMS application (GREEN ICON on the desktop), not the New World NCIC Maintenance module. Be aware that the main RMS application has limited memory; you must close individual windows inside the RMS as soon as you are done with them to preserve system resources.",
        "workflows": {
            "_WARRANT_CHECK|$SID|$JUR:": "You MUST launch the separate GREEN LERMS application for this task. Navigate to the Warrant/NCIC query interface within LERMS. Enter the subject ID (`$SID`), submit the query, extract all warrant details via OCR, and close the LERMS application.",
            "_PROPERTY_SEARCH|$IDESC|$SNUM:": "For local searches, use the New World RMS. If an NCIC check is required, you MUST use the LERMS application. Navigate to the appropriate interface, enter the item description (`$IDESC`) and serial number (`$SNUM`), submit, and extract matching records."
        }
    },
    "Cody": {
        "notes": "CRITICAL: The search procedure is a two-step process: click 'Initiate' to enable fields, then 'Execute' to run the search. You must clear all fields before starting a new query. For case numbers formatted as 'XX-XXXX', you must search the 'LOG NUMBER' field first. For address searches, use the 'Incident Address' module, type the first 4 letters of the street, select from the dropdown, then specify a house number range (e.g., 1406-1406 for a single house).",
        "workflows": {
            "_CASE_LOOKUP|$CN:": "Check if `$CN` contains a hyphen; if so, search the 'Log Number' field first before trying the 'Case Number' field. Click 'Initiate', enter data, then click 'Execute'. Extract data and close the module."
        }
    },
    "OneSolutionRMS": {
        "notes": "CRITICAL: The search workflow is: 1. Select Module -> 2. Click 'Search' (this unlocks the input fields) -> 3. Type Query -> 4. Click 'View' (this executes the search). If a query fails or you need to start a new one, you MUST click the 'EXIT SRCH' button (mapped to 'x' key) to clear the form.",
        "workflows": {}
    }
}


# ============================================================================
# Core Generator and Helper Classes
# ============================================================================

class WorkflowSelector:
    """Handles the interactive selection of workflows from the embedded database."""
    def __init__(self):
        self.workflows = WORKFLOWS_DATABASE
        self.basic_commands = [
            "_RMS_LOGIN", "_INITIATE|$start:", "_UNKNOWN_QUERY_NLP|$Q_TXT:",
            "_PERSON_LOOKUP|$LN|$FN:", "_CASE_LOOKUP|$CN:", "_ADDRESS_LOOKUP|$HN|$ST:",
            "_LICENSE_PLATE_LOOKUP|$PN:"
        ]
    
    def display_workflow_menu(self) -> List[str]:
        print("\n" + "="*60)
        print("WORKFLOW LIBRARY SELECTION")
        print("="*60)
        print("\nBasic workflows (always included):")
        for cmd_str in self.basic_commands:
            cmd = cmd_str.split('|$')[0]
            wf = next((w for w in self.workflows if w['Full Command'].startswith(cmd)), None)
            if wf: print(f"  • {wf['Short Form']:<6} - {wf['Description']}")

        available = [w for w in self.workflows if w['Full Command'] not in self.basic_commands]
        if not available: return []

        print(f"\nAdditional workflows available: {len(available)}")
        if input("\nWould you like to add more workflows from the library? (y/n): ").lower().strip() != 'y':
            return []

        print("\n--- FULL WORKFLOW LIBRARY ---")
        for i, wf in enumerate(available, 1):
            print(f"{i:2d}. {wf['Short Form']:<6} - {wf['Description']}")
        
        selection = input("\nSelect workflows to add (comma-separated numbers, or 'all'): ").strip().lower()
        
        selected_cmds = []
        if selection == 'all':
            selected_cmds.extend([w['Full Command'] for w in available])
        elif selection:
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(',')]
                selected_cmds.extend([available[idx]['Full Command'] for idx in indices if 0 <= idx < len(available)])
            except ValueError:
                print("Invalid selection. No additional workflows will be added.")
        
        return selected_cmds
class TruPromptGenerator:
    """Generates the final, hyper-customized system prompt."""
    
    def __init__(self, agency_data: Dict, additional_workflows: List[str]):
        self.agency_data = agency_data
        self.additional_workflows = additional_workflows
        self.selector = WorkflowSelector()
        self.all_workflow_cmds = self.selector.basic_commands + self.additional_workflows
        self.rms_name = self.agency_data.get('rms_name')
        
    def generate_prompt(self):
        """Main generation logic that routes to the correct prompt builder."""
        encryption_mode = self.agency_data.get('encryption_mode')
        use_external_logic = self.agency_data.get('use_external_logic')

        if use_external_logic:
            return self._build_externalized_prompt(encryption_mode)
        else:
            return self._build_embedded_prompt(encryption_mode)

    def _get_command_library_content(self, for_shell_echo: bool = False) -> str:
        """Builds the content for the command library with RMS customizations."""
        library_content = ["# dataPull Agent Command Library"]
        rms_overrides = RMS_CONFIG.get(self.rms_name, {}).get("workflows", {})

        for cmd_str in self.all_workflow_cmds:
            workflow = next((w for w in WORKFLOWS_DATABASE if w['Full Command'] == cmd_str), None)
            if workflow:
                procedure = rms_overrides.get(workflow['Full Command'], self._get_default_procedure(workflow['Full Command']))
                if for_shell_echo:
                    # More robust escaping for shell
                    procedure = procedure.replace('\\', '\\\\').replace('"', '\\"').replace('`', '\\`').replace('$', '\\$')
                entry = (
                    f"\n- command: {workflow['Full Command']}\n"
                    f"  short_form: {workflow['Short Form']}\n"
                    f"  goal: \"{workflow['Description']}\"\n"
                    f"  procedure: \"{procedure}\""
                )
                library_content.append(entry)
        
        return "\n".join(library_content)

    def _get_default_procedure(self, command: str) -> str:
        """Provides a generic, default procedure for a given command."""
        if command.startswith("_PERSON_LOOKUP"):
            return "Navigate to the person search interface, enter `$LN` and `$FN`, submit the query, extract all available data fields, and close the module."
        if command.startswith("_CASE_LOOKUP"):
            return "Navigate to the case search module, enter `$CN`, execute the search, extract all data (narratives, persons, property), and close the module."
        wf = next((w for w in WORKFLOWS_DATABASE if w['Full Command'] == command), None)
        return wf['Description'] if wf else f"Execute standard procedure for {command.split('|$')[0]}."

    def _run_encryption_flow(self, simple: bool = False):
        """Generates keys and encrypted credentials."""
        if not CRYPTOGRAPHY_AVAILABLE:
            raise ImportError("Cryptography library is required for encryption.")
        
        credentials_json = json.dumps({
            "rms_username": self.agency_data.get('rms_username', ''), 
            "rms_password": self.agency_data.get('rms_password', '')
        }).encode('utf-8')

        if simple:
            key = Fernet.generate_key()
            cipher = Fernet(key)
            encrypted_credentials = cipher.encrypt(credentials_json)
            return key, encrypted_credentials
        else: # Split-Secret
            server_key = os.urandom(32)
            client_key = os.urandom(32)
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=480000, backend=default_backend())
            final_key = base64.urlsafe_b64encode(kdf.derive(server_key + client_key))
            cipher = Fernet(final_key)
            encrypted_credentials = cipher.encrypt(credentials_json)
            return server_key, client_key, salt, encrypted_credentials

    def _get_shared_template_vars(self):
        """Gets a dictionary of variables common to all prompt templates."""
        rms_notes_user = self.agency_data.get('rms_notes', '')
        rms_notes_system = RMS_CONFIG.get(self.rms_name, {}).get('notes', '')
        combined_rms_notes = f"{rms_notes_user}\n{rms_notes_system}".strip().replace('\n', ' ')

        return {
            "agency_name": self.agency_data['agency_name'],
            "agency_abbr": self.agency_data['agency_abbr'],
            "city": self.agency_data['city'],
            "county": self.agency_data['county'],
            "state": self.agency_data['state'],
            "rms_name": self.rms_name,
            "rms_vendor": self.agency_data.get('rms_vendor', 'Unknown'),
            "combined_rms_notes": combined_rms_notes,
            "os_name": self.agency_data.get('os', 'Windows'),
            "base64_signature": base64.b64encode(f"{self.agency_data['agency_abbr']}_dataPull_agent".encode()).decode()
        }
    def _build_embedded_prompt(self, encryption_mode: str):
        """Builds a single, self-contained prompt with all logic embedded."""
        template_vars = self._get_shared_template_vars()
        template_vars['command_library'] = self._get_command_library_content(for_shell_echo=False)
        
        if encryption_mode == 'simple':
            key, enc_creds = self._run_encryption_flow(simple=True)
            template_vars['encryption_key'] = key.decode('utf-8')
            template_vars['encrypted_creds'] = enc_creds.decode('utf-8')
            return EMBEDDED_SIMPLE_ENCRYPTED_TEMPLATE.format(**template_vars)
        else: # Plaintext
            template_vars['rms_username'] = self.agency_data.get('rms_username', 'NOT_PROVIDED')
            template_vars['rms_password'] = self.agency_data.get('rms_password', 'NOT_PROVIDED')
            return EMBEDDED_PLAINTEXT_TEMPLATE.format(**template_vars)


    def _build_externalized_prompt(self, encryption_mode: str):
        """Builds the two-part prompt set (Bootstrap/Persistent) for externalized logic."""
        template_vars = self._get_shared_template_vars()
        
        command_library_content = self._get_command_library_content(for_shell_echo=True)
        escaped_command_lib = json.dumps(command_library_content)

        # Correctly format bootstrap_steps as a multi-line string for the f-string
        bootstrap_steps_list = [
            "- 'log \"Starting bootstrap process...\"'",
            "- 'shell mkdir -p ~/Desktop/dataPull_Arch/Prev_Reports'",
            f"- 'shell echo \"### Master Instructions: {template_vars['agency_abbr']} ###\\n---\\n# Stores learned shortcuts and system notes.\\nSignature: {template_vars['base64_signature']}\\nLast_Updated: \\n\\n## QuickRoutes ##\\n\\n## RMS_Notes ##\\n\\n## OS_Notes ##\\n\\n--- End of File ---\" > ~/Desktop/dataPull_Arch/Master_Instructions.txt'",
            f"- 'shell echo {escaped_command_lib} > ~/Desktop/dataPull_Arch/command_library.txt'"
        ]
        
        if encryption_mode == 'split_secret':
            server_key, client_key, salt, enc_creds = self._run_encryption_flow(simple=False)
            template_vars['server_key_b64'] = base64.urlsafe_b64encode(server_key).decode('utf-8')
            
            client_key_file_content = base64.urlsafe_b64encode(client_key).decode('utf-8')
            credentials_file_content = enc_creds.decode('utf-8')
            agency_config = {"encryption_salt": base64.urlsafe_b64encode(salt).decode('utf-8')}
        else: # Plaintext for externalized model
            template_vars['server_key_b64'] = "PLAINTEXT_MODE"
            client_key_file_content = "PLAINTEXT_MODE"
            credentials_file_content = json.dumps({
                "rms_username": self.agency_data.get('rms_username', ''),
                "rms_password": self.agency_data.get('rms_password', '')
            })
            agency_config = {}

        bootstrap_steps_list.append(f"- 'shell echo \"{client_key_file_content}\" > ~/Desktop/dataPull_Arch/client_key.key'")
        bootstrap_steps_list.append(f"- 'shell echo \"{credentials_file_content}\" > ~/Desktop/dataPull_Arch/credentials.enc'")
        bootstrap_steps_list.append(f"- 'shell echo \"{json.dumps(agency_config)}\" > ~/Desktop/dataPull_Arch/agency_config.json'")
        bootstrap_steps_list.append("- 'log \"Bootstrap complete. Agent file system initialized. Ready for persistent prompt.\"'")
        bootstrap_steps_list.append("- 'exit'")
        
        template_vars['bootstrap_steps'] = '\\n'.join(f'      {step}' for step in bootstrap_steps_list)

        bootstrap_content = BOOTSTRAP_TEMPLATE.format(**template_vars)
        persistent_content = PERSISTENT_TEMPLATE.format(**template_vars)
        
        return (
            f"### Generated Bootstrap Prompt for {self.agency_data['agency_name']} (One-Time Use) ###\\n\\n"
            f"{bootstrap_content}\\n\\n"
            f"---\\n\\n"
            f"### Generated Persistent Prompt for {self.agency_data['agency_name']} ###\\n\\n"
            f"{persistent_content}"
        )

# ============================================================================
# PROMPT TEMPLATES
# ============================================================================

BOOTSTRAP_TEMPLATE = """
# ===============================================
# ONE-TIME BOOTSTRAP PROMPT
# ===============================================
agency_info:
  name: "{agency_name}"
  abbr: "{agency_abbr}"
  signature_base64: "{base64_signature}"

bootstrap_directive:
  description: |
    ONE-TIME USE. Your only goal is to execute the command: _INITIATE|$start.
    This process will write your core instructions and command library to the file system.
    Upon successful completion, your system prompt MUST be replaced by the persistent prompt.
  command_to_run: "_INITIATE|$start"

command_workflows:
  _INITIATE|$start:
    goal: Create the agent's persistent file structure and instruction set.
    steps:
{bootstrap_steps}
"""

PERSISTENT_TEMPLATE = """
# ===============================================
# PERSISTENT PROMPT (for Externalized Logic)
# ===============================================
# You are the dataPull Agent. This is your complete operational directive.

#### **1. Agency and System Configuration**
* **Agency Name**: `{agency_name}`
* **Records Management System (RMS)**: `{rms_name}`
* **Notes**: `{combined_rms_notes}`
* **Operating System**: `{os_name}`

#### **2. Core Directives & Startup**
* **Identity**: You are the `dataPull_Agent`.
* **Startup Actions**:
    1.  **LOAD INSTRUCTIONS**: Your first action is to read `~/Desktop/dataPull_Arch/Master_Instructions.txt` and `~/Desktop/dataPull_Arch/command_library.txt` into your working context.
    2.  **MAINTAIN FILE SYSTEM**: All files you create MUST be saved within `~/Desktop/dataPull_Arch/`.
* **Operational Mode**: After loading instructions, parse and execute the user's RFI command.
* **Authentication**: To log into the RMS, you **must** use the service account credentials by calling the appropriate secure login function. This may require your `SERVER_KEY`: `{server_key_b64}`.

#### **3. Core Interaction Protocols**
* **CRITICAL CLICKING PROCEDURE**: Coordinate-based clicking WILL NOT WORK. A single-click is `mouse_move` -> `button_down` -> `button_up`. A double-click is this sequence followed by a `Return` key press.
* **Text Verification**: After typing, screenshot and OCR the field to verify correct entry before submitting.
* **Error Handling**: On a failed action, retry up to 3 times. If failure persists, use an alternative from your PACE plans.
* **Parallel Operations**: For maximum efficiency, invoke tools simultaneously when possible.
"""
"""
#### **4. Required Output Schema**
```json
{{
  "reportMetadata": {{ "rfiCommand": "string", "reportID": "[AGENCY_ABBR]-[YYYYMMDD]-[HHMMSS]", "status": "SUCCESS | PARTIAL_SUCCESS | FAILURE", "summary": "Natural language summary." }},
  "primarySubject": {{ "type": "string", "queryParameters": {{}} }},
  "dataPayload": [ {{ "recordID": "string", "recordType": "string", "drtClassification": "1|2|3", "source": "string", "extractedData": {{}}, "narratives": [], "associations": [] }} ],
  "agentActivityLog": {{ "keyActions": [], "errorsEncountered": [] }}
}}
```
"""

EMBEDDED_PLAINTEXT_TEMPLATE = """
# ===============================================
# EMBEDDED (ALL-IN-ONE) PROMPT - PLAINTEXT
# ===============================================
# You are the dataPull Agent. This is your complete operational directive.

#### **1. Agency and System Configuration**
* **Agency Name**: `{agency_name}`
* **Records Management System (RMS)**: `{rms_name}` ({combined_rms_notes})
* **Operating System**: `{os_name}`
* **Credentials**:
    * **Username**: `{rms_username}`
    * **Password**: `{rms_password}`

#### **2. Core Directives & Protocols**
* **Identity**: You are the `dataPull_Agent`, a law enforcement AI assistant.
* **Operational Mode**: Parse and execute the user's RFI command based on the command library below.
* **Output Requirement**: All final reports must strictly conform to the JSON schema provided.
* **CRITICAL CLICKING PROCEDURE**: A single-click is `mouse_move` -> `button_down` -> `button_up`. A double-click is this sequence plus a `Return` key press.
* **Text Verification**: After typing, screenshot and OCR the field to verify correct entry.

#### **3. Command Library**
{command_library}

#### **4. Required Output Schema**
```json
{{
  "reportMetadata": {{ "rfiCommand": "string", "reportID": "[AGENCY_ABBR]-[YYYYMMDD]-[HHMMSS]", "status": "SUCCESS | PARTIAL_SUCCESS | FAILURE", "summary": "Natural language summary." }},
  "primarySubject": {{ "type": "string", "queryParameters": {{}} }},
  "dataPayload": [ {{ "recordID": "string", "recordType": "string", "drtClassification": "1|2|3", "source": "string", "extractedData": {{}}, "narratives": [], "associations": [] }} ],
  "agentActivityLog": {{ "keyActions": [], "errorsEncountered": [] }}
}}
```
"""

EMBEDDED_SIMPLE_ENCRYPTED_TEMPLATE = """
# ===============================================
# EMBEDDED (ALL-IN-ONE) PROMPT - SIMPLE ENCRYPTION
# ===============================================
# You are the dataPull Agent. This is your complete operational directive.

#### **1. Agency and System Configuration**
* **Agency Name**: `{agency_name}`
* **Records Management System (RMS)**: `{rms_name}` ({combined_rms_notes})
* **Operating System**: `{os_name}`

#### **2. Core Directives & Authentication**
* **Identity**: You are the `dataPull_Agent`.
* **Authentication**: To log into the RMS, you must first decrypt the credentials embedded in this prompt. Use the `ENCRYPTION_KEY` with a Fernet cipher to decrypt the `ENCRYPTED_CREDENTIALS`.
* **Operational Mode**: Parse and execute the user's RFI command based on the command library below.
* **Output Requirement**: All final reports must strictly conform to the JSON schema provided.

#### **3. Core Interaction Protocols**
* **CRITICAL CLICKING PROCEDURE**: A single-click is `mouse_move` -> `button_down` -> `button_up`. A double-click is this sequence plus a `Return` key press.
* **Text Verification**: After typing, screenshot and OCR the field to verify correct entry.

#### **4. Security Credentials**
* **ENCRYPTION_KEY**: `{encryption_key}`
* **ENCRYPTED_CREDENTIALS**: `{encrypted_creds}`

#### **5. Command Library**
{command_library}

#### **6. Required Output Schema**
```json
{{
  "reportMetadata": {{ "rfiCommand": "string", "reportID": "[AGENCY_ABBR]-[YYYYMMDD]-[HHMMSS]", "status": "SUCCESS | PARTIAL_SUCCESS | FAILURE", "summary": "Natural language summary." }},
  "primarySubject": {{ "type": "string", "queryParameters": {{}} }},
  "dataPayload": [ {{ "recordID": "string", "recordType": "string", "drtClassification": "1|2|3", "source": "string", "extractedData": {{}}, "narratives": [], "associations": [] }} ],
  "agentActivityLog": {{ "keyActions": [], "errorsEncountered": [] }}
}}
```
"""
# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point for the interactive prompt generator."""
    print(">>> truPrompt - Unified Agent Prompt Generator (v5.2 Synthesis)")
    
    if not CRYPTOGRAPHY_AVAILABLE:
        print("\nWARNING: The 'cryptography' library is not installed.")
        print("You will only be able to generate prompts in Plaintext mode.")

    try:
        # 1. Gather Agency & Environment Data
        print("\n" + "="*60)
        print("STEP 1: AGENCY & ENVIRONMENT CONFIGURATION")
        print("="*60)
        rms_options = ", ".join(RMS_CONFIG.keys())
        agency_data = {
            'agency_name': input("Agency Name: ").strip() or "Test Agency",
            'agency_abbr': input("Agency Abbreviation: ").strip().upper() or "TA",
            'city': input("City: ").strip() or "Testville",
            'county': input("County: ").strip() or "Test County",
            'state': input("State: ").strip() or "TS",
            'rms_name': input(f"RMS Name ({rms_options}, or other): ").strip() or "GenericRMS",
            'rms_vendor': input("RMS Vendor: ").strip() or "GenericVendor",
            'rms_notes': input("Any other RMS notes or quirks?: ").strip(),
            'os': input("Operating System (default: Windows): ").strip() or "Windows"
        }

        # 2. Choose Logic Model
        print("\n" + "="*60)
        print("STEP 2: LOGIC STORAGE MODEL")
        print("="*60)
        while True:
            logic_model = input("[1] Embedded (server-side, larger prompt)\n[2] Externalized (client-side, smaller prompt)\nChoose model: ").strip()
            if logic_model in ['1', '2']:
                agency_data['use_external_logic'] = (logic_model == '2')
                print(f"✓ Model set to: {'Externalized (Client-Side)' if agency_data['use_external_logic'] else 'Embedded (Server-Side)'}")
                break
            else: print("Invalid selection.")

        # 3. Choose Security Model
        print("\n" + "="*60)
        print("STEP 3: SECURITY MODEL")
        print("="*60)
        while True:
            prompt_text = (
                "[1] Split-Secret Encryption (Most Secure, requires Externalized model)\n"
                "[2] Simple Encryption (Self-Contained, no local files)\n"
                "[3] Plaintext (Not Secure)\n"
                "Choose model: "
            )
            sec_model = input(prompt_text).strip()
            
            if sec_model in ['1', '2'] and not CRYPTOGRAPHY_AVAILABLE:
                print("ERROR: Cannot select an encrypted mode, cryptography library is not installed.")
                continue

            if agency_data['use_external_logic'] == False and sec_model == '1':
                print("WARNING: Split-Secret model is not compatible with a fully Embedded prompt. It requires creating external files.")
                print("Please choose Simple Encryption for a truly self-contained prompt, or switch to an Externalized logic model.")
                continue
            
            if sec_model == '1':
                agency_data['encryption_mode'] = 'split_secret'
                print("✓ Security model set to: Split-Secret Encryption")
                break
            elif sec_model == '2':
                agency_data['encryption_mode'] = 'simple'
                print("✓ Security model set to: Simple Encryption (Self-Contained)")
                break
            elif sec_model == '3':
                agency_data['encryption_mode'] = 'plaintext'
                print("✓ Security model set to: Plaintext")
                break
            else:
                print("Invalid selection.")
        
        # 4. Gather Credentials
        print("\n--- Credentials ---")
        agency_data['rms_username'] = input("RMS Username: ").strip()
        agency_data['rms_password'] = input("RMS Password: ").strip()
        if agency_data['encryption_mode'] != 'plaintext' and (not agency_data.get('rms_username') or not agency_data.get('rms_password')):
            print("\nERROR: Username and Password are required for encrypted modes. Aborting.")
            return

        # 5. Select Workflows
        workflow_selector = WorkflowSelector()
        additional_workflows = workflow_selector.display_workflow_menu()

        # 6. Generate and Save
        print("\n" + "="*60)
        print("GENERATING PROMPT...")
        print("="*60)
        
        generator = TruPromptGenerator(agency_data, additional_workflows)
        final_prompt = generator.generate_prompt()
        
        output_dir = "outputs"
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.join(output_dir, f"{agency_data['agency_abbr']}_truPrompt_v5.2.txt")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(final_prompt)
            
        print(f"\nSUCCESS! Prompt generated successfully.")
        print(f"File saved to: {filename}")
        print("\n--- NEXT STEPS ---")
        print(f"1. Copy the entire content of '{os.path.basename(filename)}'.")
        if agency_data['use_external_logic']:
            print("2. Provide the AI with the 'Bootstrap Prompt' first.")
            print("3. Once the AI confirms setup, REPLACE the prompt with the 'Persistent Prompt'.")
        else:
            print("2. Provide the full 'Embedded' prompt to the AI. No further steps needed.")

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to exit.")

if __name__ == "__main__":
    main()




