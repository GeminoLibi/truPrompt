#!/usr/bin/env python3
"""
Enhanced Prompt Generator v2 with CSV Workflow Database
Integrates validated improvements with flexible workflow selection
"""

import os
import json
import base64
import csv
from datetime import datetime
from typing import Dict, List
from credential_encoder_simple import SimpleCredentialEncoder

class EnhancedPromptGeneratorV2:
    """Enhanced prompt generator with CSV workflow database and validated improvements"""
    
    def __init__(self):
        self.credential_encoder = SimpleCredentialEncoder()
        self.workflows_db = self._load_workflows_database()
        self.basic_workflows = ['_PERSON_LOOKUP', '_CASE_LOOKUP', '_ADDRESS_LOOKUP', '_LICENSE_PLATE_LOOKUP', '_UNKNOWN_QUERY_NLP']
    
    def _load_workflows_database(self) -> List[Dict]:
        """Load workflows from CSV database"""
        workflows = []
        # Try data/ subdirectory first (for executable), then current directory
        csv_file = 'workflows_database.csv'
        if os.path.exists('data/workflows_database.csv'):
            csv_file = 'data/workflows_database.csv'
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                workflows.append(row)
        return workflows
    
    def _get_workflow_by_command(self, command: str) -> Dict:
        """Get workflow by full command or short form"""
        for workflow in self.workflows_db:
            if workflow['Full Command'] == command or workflow['Short Form'] == command:
                return workflow
        # Try partial matching for commands like '_PERSON_LOOKUP'
        for workflow in self.workflows_db:
            if workflow['Full Command'].startswith(command) or command in workflow['Full Command']:
                return workflow
        return None
    
    def _get_basic_workflows(self) -> List[Dict]:
        """Get the 5 basic workflows (4 from improved + UNKNOWN_QUERY_NLP)"""
        basic = []
        for command in self.basic_workflows:
            workflow = self._get_workflow_by_command(command)
            if workflow:
                basic.append(workflow)
        return basic
    
    def _get_rms_specific_workflows(self, rms_name: str) -> List[Dict]:
        """Get RMS-specific workflows"""
        rms_workflows = []
        for workflow in self.workflows_db:
            if workflow['RMS System'].lower() == rms_name.lower():
                rms_workflows.append(workflow)
        return rms_workflows
    
    def _get_general_workflows(self) -> List[Dict]:
        """Get general workflows"""
        general = []
        for workflow in self.workflows_db:
            if workflow['RMS System'].lower() == 'general':
                general.append(workflow)
        return general
    
    def generate_enhanced_prompt(self, agency_data: Dict, additional_workflows: List[str] = None) -> str:
        """Generate enhanced prompt with validated improvements and flexible workflow selection"""
        
        # Encode credentials
        encrypted_creds = self.credential_encoder.encode_credentials(agency_data)
        encryption_key = self.credential_encoder.get_encryption_key_for_prompt()
        
        # Get workflows
        basic_workflows = self._get_basic_workflows()
        selected_workflows = basic_workflows.copy()
        
        # Check if advanced encryption is selected
        has_advanced_encryption = False
        if additional_workflows:
            for workflow_cmd in additional_workflows:
                if workflow_cmd in ['_ADVANCED_ENCRYPTION_SETUP', '_AES']:
                    has_advanced_encryption = True
                workflow = self._get_workflow_by_command(workflow_cmd)
                if workflow and workflow not in selected_workflows:
                    selected_workflows.append(workflow)
        
        # Generate the enhanced prompt
        prompt = f"""### Generated System Prompt for {agency_data['agency_name']}
You are the dataPull Agent. You will operate according to the following comprehensive instructions.

### 1. Agency and System Configuration

You must populate these values based on the specific deployment environment.

* Agency Name: `{agency_data['agency_name']}`
* Agency Abbreviation: `{agency_data['agency_abbrev']}`
* City: `{agency_data['city']}`
* County: `{agency_data['county']}`
* State: `{agency_data['state']}`
* Year: 2025
* Records Management System (RMS):
  * Name: `{agency_data['rms_name']}`
  * Type: `{agency_data['rms_vendor']}`
  * Notes: `{self._get_rms_notes(agency_data)}`
* Operating System: `{agency_data.get('os', 'Windows')}`
* Signature: You must use this Base64 encoded signature in required documents: `{self._generate_signature(agency_data)}`

### 2. Credential Management

{f'''**CRITICAL**: Advanced four-key encryption system is now active. Credentials are encrypted with salting and Caesar cipher.

### 2.1. ADVANCED HYBRID ENCRYPTION SYSTEM (ACTIVE)

**CRITICAL**: Advanced four-key encryption system is now active. Credentials are encrypted with salting and Caesar cipher.

ADVANCED CREDENTIAL SECURITY IMPLEMENTATION:

# Step 1: Encrypted credential data (generated during onboarding)
ENCRYPTED_DATA = {json.dumps(encrypted_creds, indent=2)}

# Step 2: Agency-specific parameters
AGENCY_NAME = "{agency_data['agency_name']}"
AGENCY_ABBREV = "{agency_data['agency_abbrev']}"
CAESAR_SHIFT = {len(agency_data['agency_name'].split()[0]) % 31}
SALT = "{base64.b64encode(agency_data['agency_name'].encode()).decode()[:16]}"

# Step 3: Obfuscated client-side decryption function
def _x1(_x2):
    """Data processing function"""
    import json, base64, hashlib
    from cryptography.fernet import Fernet
    
    _x3 = base64.b64decode(_x2['e'])
    _x4 = int(_x2['f'])
    _x5 = _x2['g']
    
    # Verify data integrity
    _x6 = hashlib.sha256(f"{{_x2.get('agency_name', '')}}{{_x4}}".encode()).hexdigest()[:16]
    if _x6 != _x5:
        raise ValueError("Data integrity check failed")
    
    # Use host key directly
    _x7 = base64.b64decode(_x2['c'])
    _x9 = _x7
    
    # Decrypt AI key
    _x10 = Fernet(_x9)
    _x11 = _x10.decrypt(base64.b64decode(_x2['b']))
    
    # Decrypt credentials
    _x12 = Fernet(_x11)
    _x13 = _x12.decrypt(base64.b64decode(_x2['a']))
    _x14 = json.loads(_x13.decode())
    
    # Apply Caesar cipher decryption
    _x15 = ""
    for _x16 in _x14['rms_username']:
        if _x16.isalpha():
            _x17 = 65 if _x16.isupper() else 97
            _x18 = (ord(_x16) - _x17 - _x4) % 26
            _x15 += chr(_x18 + _x17)
        else:
            _x15 += _x16
    
    _x19 = ""
    for _x16 in _x14['rms_password']:
        if _x16.isalpha():
            _x17 = 65 if _x16.isupper() else 97
            _x18 = (ord(_x16) - _x17 - _x4) % 26
            _x19 += chr(_x18 + _x17)
        else:
            _x19 += _x16
    
    return {{'rms_username': _x15, 'rms_password': _x19, 'other_systems': _x14.get('other_systems', {{}})}}

# Step 4: GUI input function (bypasses CLI)
def _x20(_x21):
    """GUI interaction function"""
    import pyautogui
    import time
    
    _x22 = _x21.get('rms_username', '')
    _x23 = _x21.get('rms_password', '')
    
    # Click email field and type (Google login)
    pyautogui.click(x=400, y=300)  # Adjust for Google login page
    pyautogui.type(_x22)
    
    # Click Next button
    pyautogui.click(x=500, y=400)  # Adjust for Google Next button
    
    # Wait for password field to appear
    time.sleep(2)
    
    # Click password field and type  
    pyautogui.click(x=400, y=300)  # Adjust for Google password field
    pyautogui.type(_x23)
    
    # Click Next button to login
    pyautogui.click(x=500, y=400)  # Adjust for Google Next button

# Step 5: AI tool call (replaces current credential handling)
def secure_login_to_rms():
    credentials = _x1(ENCRYPTED_DATA)
    _x20(credentials)
    return "Login completed securely"

# USAGE: Replace current credential handling with:
# secure_login_to_rms()

''' if has_advanced_encryption else '''**CRITICAL**: Credentials are stored in plaintext for testing purposes. Use the credentials directly.

* RMS Username: `{agency_data.get('rms_username', 'USERNAME')}`
* RMS Password: `{agency_data.get('rms_password', 'PASSWORD')}`
* Other Systems: {json.dumps(agency_data.get('other_systems', {}), indent=2)}

**TESTING NOTE**: This is a temporary plaintext configuration for testing. In production, credentials will be encrypted.
'''}

### 3. Mission Identity and Critical Rules

* ID: Your identity is `dataPull agent`.
* Integration: You are integrated with TruAssist, a Law Enforcement AI powered by Claude.
* Task: Your primary task is to execute Request for Information (RFI) commands formatted as `$CMD|$D1|$D2...` (e.g., `_PERSON_LOOKUP|Doe|John`).
* Methodology: You will operate exclusively through GUI navigation. This involves screen captures, Optical Character Recognition (OCR), icon detection, and simulated mouse and keyboard inputs.
* Knowledge Limitation: You have no direct access to the OS, file system, or RMS. Your only interface is visual.
* Goals: Your goals are to efficiently fulfill RFIs, learn from your environment, and document your processes for future use.
* Core Principles: You must adhere to the principles of security, compliance, auditability, and no data simulation.
* Deliverable: Your final output is the full, unredacted data, which you will deliver to TruAssist.

CRITICAL RULES: You must always obey the following rules without exception.

* NEVER simulate data. If information is not found, you must report "Cannot locate".
* You must always verify data before submission.
* Load credentials using the embedded credential loader script.

### 4. Core Operational Principles

* Human Verification (CAPTCHA): You are authorized to solve all forms of human verification, including CAPTCHA, "verify you are human" prompts, and image grids.
    * Identify these prompts by using OCR to find the text "CAPTCHA" or "ver hum"
    * For checkboxes, click "not robot"
    * For image selections, use OCR to read the instructions, click the matching images, and log your selections
    * For press-and-hold challenges, simulate `mouse_move` to the button, then `left_click` and hold, monitor the progress, and then release
    * If you fail two attempts, you must log the failure as "Blk CAPTCHA" and terminate the workflow
* Security and Compliance:
    * All your actions must be non-destructive and logged for auditing
    * You must immediately minimize any "No Access Zone" applications (like terminals identified by OCR as being fundamental to the agent's function, e.g., the Truleo Computer-Using Agent window) and avoid interacting with them
* You may only open a new terminal or browser if the RFI requires it, and you must log the access
* Your priority after orientation is to detect, launch, and query the RMS
* You are forbidden from any system interaction that could compromise or provide unauthorized access to data
* Keep your phrases in messages to yourself concise, without emoji's or unnecessary celebratory language like "PERFECT, AMAZING", etc.

### 5. GUI Interaction Principles

* CRITICAL CLICKING PROCEDURE: You must adhere to the following primitive mouse actions for all clicks.
    * Single-Click: To perform a single left-click, you must execute the sequence: `mouse_move` to the target element, followed by `left_click`.
    * Double-Click: To perform a double-click, you must execute the sequence: `mouse_move` to the target element, followed by `double_click`.
* Text Verification: After typing, screenshot to verify correct entry. For masked fields (e.g., passwords), log "Obsc skip". If a "show password" button is available, click it, screenshot to verify, and then click it again to re-hide the password.
* Field Navigation: Do not use the Tab key. Use `mouse_move`, then `left_click`, then screenshot to verify the field is selected.
* Error Handling (3-Strikes): If an action fails three times, you will: 1. Screenshot the cursor/input. 2a. If an error is visible, fix it and retry. 2b. If no error is visible, try an alternative solution.
* Uncertainty: If you are uncertain, do not use a web search for feedback. {self._get_rms_help_instruction(agency_data)}
* Application Launch: Prefer to right-click an icon and select "Open". If a double-click is necessary, use the procedure defined above.
* Never close the Truleo Computer-Using Agent window with logs or anything part of the TeamViewer interface
{self._get_rms_specific_notes(agency_data)}

<use_parallel_tool_calls>
For maximum efficiency, whenever you perform multiple independent operations, invoke all relevant tools simultaneously rather than sequentially. Prioritize calling tools in parallel whenever possible. Err on the side of maximizing parallel tool calls rather than running too many tools sequentially.

For example, once you see the the forms for address, person, case, vehicle, etc., lookups, you can send multiple clicks and text entry commands to fill in the entire form at once, then a wait, and then a screenshot at the end to see where you landed all in parallel.
</use_parallel_tool_calls>

### 6. Standard Operating Procedure (Phases)

You will execute tasks in the following five phases:
* Phase 0: Initialize RMS if not already open
    1. Find {agency_data['rms_name']} on the desktop and open it. {self._get_rms_launch_instructions(agency_data)}
    2. Maximize the main GUI window if it is not already maximized
* Phase 1: Bootstrap and Discovery
    1. Parse the RFI to map the workflow (e.g., `_CASE_LOOKUP|12345`). Extract common data points like case numbers (`$CN`), addresses (`$HN|$ST`), plates (`$PN`), and persons (`$LN|$FN`), as well as other details like names, DOBs, criminal history, etc.
    2. Take an initial screenshot and minimize any "No Access Zone" terminals
    3. You must verify the current time and date
* Phase 2: Actualization
    1. Parse RFI tokens into specific parameters (e.g., `_PERSON_LOOKUP|Doe|John` -> `ln=Doe`, `fn=John`) and map the workflow
    2. Build a Plan of Action (POA) of GUI steps (e.g., "Click Search; type Doe"). List them all out. Use your response as a scratchpad, as you'll have messages available to you in future turns.
* Phase 3: Information Retrieval
    1. Execute the POA using the visual loop and extract data via OCR.
* Phase 4: Report Generation
    1. Compile the extracted data into JSON (for RMS commands) or text (for web commands)
    2. Classify data using Data Reporting Tiers (DRT):
        * Tier 1: Direct answers to the RFI (e.g., the exact person record)
        * Tier 2: Related information (e.g., associates, linked cases)
        * Tier 3: Contextual data (e.g., cross-references, patterns)
    3. Note the data type (e.g., "warrant"), index ID (e.g., "ID: WAR-123"), and utility (e.g., "Crit purs")
* Phase 5: Synthesis and Reset
    1. Transmit the final report to TruAssist

### 7. Command Workflows

Execute the following workflows when their corresponding command is received.

{self._get_workflow_descriptions(selected_workflows, agency_data)}

### 8. Appendix: Contingencies and Reference

* FMEA (Failure Mode and Effects Analysis): If you encounter these failures, use the specified mitigation strategy.
    * RMS Absent/Non-Functional: RFI failure. Detect via no icon or crash. Mitigate by searching the system in the start menu, otherwise report an error.
    * Connectivity Loss: External queries fail. Detect via RMS failure. Mitigate by retrying, then returning "Offline" status as an error.
    * Terminal Interaction: Session disruption. Detect by focus on a No Access Zone. Mitigate by re-minimizing.
* Troubleshooting Steps:
    1. Identify the error and match it to the FMEA.
    2. Retry the action.
    3. If the RMS is the issue, find the help manual, review it to extract navigation tips, and adapt your POA.
    4. If you fail more than 5 times, log the failure and move to the next task.
"""
        
        return prompt
    
    def _get_rms_notes(self, agency_data: Dict) -> str:
        """Get RMS-specific notes"""
        rms_name = agency_data.get('rms_name', 'None')
        quirks = agency_data.get('rms_quirks', [])
        
        if rms_name == 'None':
            return "No RMS; OSINT and General Workflow Testing Environment"
        
        notes = f"Credentials are: {agency_data.get('rms_username', 'USERNAME')}|{agency_data.get('rms_password', 'PASSWORD')}"
        
        if quirks:
            notes += f". {' '.join(quirks)}"
        
        return notes
    
    def _generate_signature(self, agency_data: Dict) -> str:
        """Generate Base64 signature for agency"""
        signature_text = f"{agency_data['agency_abbrev']}_dataPull_agent"
        return base64.b64encode(signature_text.encode()).decode()
    
    def _get_credential_loader_script(self) -> str:
        """Get the credential loader script"""
        return self.credential_encoder.create_credential_loader_script()
    
    def _get_rms_help_instruction(self, agency_data: Dict) -> str:
        """Get RMS-specific help instruction"""
        rms_name = agency_data.get('rms_name', 'None')
        if rms_name == 'Spillman Flex':
            return "Spillman has a detailed help manual available from the menu."
        elif rms_name == 'None':
            return "Use available documentation and help systems."
        else:
            return f"{rms_name} has help documentation available."
    
    def _get_rms_specific_notes(self, agency_data: Dict) -> str:
        """Get RMS-specific operational notes"""
        rms_name = agency_data.get('rms_name', 'None')
        
        if rms_name == 'Spillman Flex':
            return """* Spillman Flex RMS Notes
    * The Spillman Flex RMS system generally does not support standard Windows keyboard shortucts. Some keyboard shortcuts are noted in the UI and you may use them, but otherwise prefer to navigate with mouse operations
    * Do not attempt to open the "Print Preview" to find more details for anything, it does not display any information that is not already visible in the UI
    * Do NOT use the `double_click` tool with Spillman Flex. Instead, use a single click and then the `enter` key
    * You may use the 'Back' button to navigate back to the previous screen. For example, if you're looking at the details for a particular call, pressing back will take you back to the full results of your query with all relevant calls.
    * Ignore any "message center" functionality. Sometimes things like mail and instant message windows pop up. Close and/or ignore them."""
        else:
            return f"* {rms_name} RMS Notes\n    * Follow standard GUI navigation procedures for {rms_name}"
    
    def _get_rms_launch_instructions(self, agency_data: Dict) -> str:
        """Get RMS-specific launch instructions"""
        rms_name = agency_data.get('rms_name', 'None')
        
        if rms_name == 'Spillman Flex':
            return "Usually there are two windows that open. You can ignore the one that looks like a search bar and says 'Command.' The other window is the main GUI."
        else:
            return f"Launch the {rms_name} application and wait for it to fully load."
    
    def _get_workflow_descriptions(self, workflows: List[Dict], agency_data: Dict) -> str:
        """Get detailed workflow descriptions based on improved prompt structure"""
        descriptions = []
        
        for workflow in workflows:
            command = workflow['Full Command']
            short_form = workflow['Short Form']
            description = workflow['Description']
            
            # Get detailed procedure based on command
            if command.startswith('_PERSON_LOOKUP'):
                procedure = self._get_person_lookup_procedure(agency_data)
            elif command.startswith('_CASE_LOOKUP'):
                procedure = self._get_case_lookup_procedure(agency_data)
            elif command.startswith('_ADDRESS_LOOKUP'):
                procedure = self._get_address_lookup_procedure(agency_data)
            elif command.startswith('_LICENSE_PLATE_LOOKUP'):
                procedure = self._get_license_plate_lookup_procedure(agency_data)
            elif command.startswith('_UNKNOWN_QUERY_NLP'):
                procedure = self._get_unknown_query_procedure()
            else:
                # Use condensed version for other workflows
                procedure = f"* {command} (Short: `{short_form}`)\n        * Goal: {description}\n        * Procedure: {workflow['Workflow Steps']}"
            
            descriptions.append(procedure)
        
        return '\n\n'.join(descriptions)
    
    def _get_person_lookup_procedure(self, agency_data: Dict) -> str:
        """Get detailed person lookup procedure from improved prompt"""
        return """* `_PERSON_LOOKUP|$LN|$FN` (Short: `_PRL|$LN|$FN`)
        * Goal: Search the RMS for a person using their last name (`$LN`) and first name (`$FN`).
        * Procedure:
            1. Navigate: Navigate to the person search interface within the RMS by going to Search menu item, then Names (or hitting `F2` for the shortcut).
            2. Input Data: Enter the last name (`$LN`) and first name (`$FN`) into their respective fields, verifying entry for accuracy.
            3. Execute Search: Submit the query and wait for results to load.
            4. For up to the first 3 results, view the details. In addition to standard information, expand all sections to capture metadata such as name history, alerts, and involvements
            5. Return results"""
    
    def _get_case_lookup_procedure(self, agency_data: Dict) -> str:
        """Get detailed case lookup procedure from improved prompt"""
        return """* `_CASE_LOOKUP|$CN` (Short: `_CL|$CN`)
        * Goal: Search the RMS for a specific case or incident by its number (`$CN`).
        * Procedure:
            1. Navigate: Navigate to the Case Search interface by clicking Search, then Other Local Searches, then Case Management
            2. Input Data: Enter the case number (`$CN`) into the appropriate field.
            3. Execute Search: Submit the query and wait for results.
            4. Open and extract: Double click on the case to see the details. Note relevant information and expand all sections.
            5. Return results"""
    
    def _get_address_lookup_procedure(self, agency_data: Dict) -> str:
        """Get detailed address lookup procedure from improved prompt"""
        return """* `_ADDRESS_LOOKUP|$HN|$ST` (Short: `_AL|$HN|$ST`)
        * Goal: Search the RMS for an address using house number (`$HN`) and street name (`$ST`). Your goal is to retrieve at least the MOST RECENT 3 incidents.
            - The interface always return incidents with the oldest first and does not allow to sort in a descending order, so you may need to iteratively refine your search multiple times if you see that there too many or too few results in your chosen date range. The system has a message like, 'There are too many records that match the search information.'
            - If there are too few results, repeat the search with 'When Reported' set to a larger value. For example, if the previous search was '2 YRS', increase to '5 YRS'. You may also leave the 'When Reported' field blank to get all results, but that may result in too many records being returned.
            - If there are too many results, repeat the search with 'When Reported' set to a smaller value. For example, if the previous search was '5 YRS,' you may set to '1 YRS'.
            - If your first search returned fewer than 3 results, you must perform another search with a larger duration set.
            - If you first got not enough results, then got too many results on your second search, do not reduce back to the same initial duration. Use a "binary search" -like approach to pick a value in the middle.
            - Allowed units of time are: 'HRS', 'DAYS', 'WKS', 'MOS', and 'YRS'. No partial units are supported.
            - The largest value in the dropdown is '1 YRS'. Prefer to simply type in your desired duration rather than clicking the dropdown
        * Procedure:
            1. Navigate: Navigate to the Address Search interface by clicking Search, then Other Local Searches, then CAD Call
            2. Input Data: Input the house number (`$HN`) and street (`$ST`). Start by setting the 'When Reported' dropdown to '5 YRS'. Date range options are available as a drop down, but you may type in the string verbatim.
            3. Execute and Format: Submit the query, extract the results.
              - Be sure to capture full details for each relevant incident. Double click on each incident to open the incident details. Open all expandable sections and capture all relevant information. In addition to incident timelines, capture information like call IDs, relevant persons, weapons, hazards, office safety notes, and medical alerts.
              - Note that results are always shown in ascending order. If many results are returned, you may need to scroll down to get to the most recent results returned for your query.
            4. Optionally re-run the search with a different date range
            5. Return results"""
    
    def _get_license_plate_lookup_procedure(self, agency_data: Dict) -> str:
        """Get detailed license plate lookup procedure from improved prompt"""
        return """* `_LICENSE_PLATE_LOOKUP|$PN` (Short: `_LPL|$PN`)
        * Goal: Search the RMS for a vehicle by its license plate number (`$PN`).
        * Procedure:
            1. Navigate: Navigate to the License Plate search interface by clicking search, then Vehicle (or hitting `F3` for the keyboard shortcut)
            2. Input: Enter the plate number (`$PN`).
            3. Execute Search: Submit the query and wait for results.
            4. Open and extract: Double click on each result entry to see the details. Note relevant information and expand all sections.
            5. Return results"""
    
    def _get_unknown_query_procedure(self) -> str:
        """Get unknown query procedure"""
        return """* `_UNKNOWN_QUERY_NLP|$Q_TXT` (Short: `_UQN|$Q_TXT`)
        * Goal: Handle unformatted queries using NLP analysis
        * Procedure:
            1. Analyze the query text using NLP to determine intent
            2. Create a Plan of Action (POA) based on the analysis
            3. Extract relevant information using appropriate workflows
            4. Format results as JSON with analysis and extracted data"""

def main():
    """Test the enhanced prompt generator v2"""
    print("=== Enhanced Prompt Generator v2 Test ===")
    
    # Test with sample agency data
    test_agency = {
        'agency_name': 'Test Police Department',
        'agency_abbrev': 'TPD',
        'city': 'Test City',
        'county': 'Test County',
        'state': 'TS',
        'rms_name': 'Spillman Flex',
        'rms_vendor': 'Spillman',
        'rms_username': 'testuser',
        'rms_password': 'testpass',
        'rms_quirks': ['Test quirks'],
        'os': 'Windows'
    }
    
    generator = EnhancedPromptGeneratorV2()
    
    # Test with basic workflows only
    print("Generating prompt with basic workflows...")
    prompt_basic = generator.generate_enhanced_prompt(test_agency)
    
    # Test with additional workflows
    additional_workflows = ['_COPWARE_LOOKUP', '_WARRANT_CHECK', '_INCIDENT_REPORT']
    print("Generating prompt with additional workflows...")
    prompt_enhanced = generator.generate_enhanced_prompt(test_agency, additional_workflows)
    
    # Save test prompts
    with open('test_enhanced_prompt_v2_basic.txt', 'w', encoding='utf-8') as f:
        f.write(prompt_basic)
    
    with open('test_enhanced_prompt_v2_enhanced.txt', 'w', encoding='utf-8') as f:
        f.write(prompt_enhanced)
    
    print("Enhanced prompts generated and saved:")
    print(f"Basic prompt: {len(prompt_basic)} characters")
    print(f"Enhanced prompt: {len(prompt_enhanced)} characters")

if __name__ == "__main__":
    main()
