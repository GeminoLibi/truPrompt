#!/usr/bin/env python3
"""
Enhanced Agency Input Form with Workflow Selection
Integrates workflow selector with agency data collection
"""

import json
import os
import sys
from datetime import datetime
from prompt_generator import EnhancedPromptGeneratorV2
from workflow_selector import WorkflowSelector

def check_environment():
    """Check if we're running from executable or Python directly"""
    print(">>> dataPull Agent Prompt Generator")
    print("=" * 50)
    print()
    
    # Determine if we're running from executable (data files in data/ subdir) or Python directly
    data_dir = ""
    if os.path.exists('data/command_library.txt'):
        data_dir = "data/"
        print("Running from executable - using data/ subdirectory")
    elif os.path.exists('command_library.txt'):
        data_dir = ""
        print("Running from Python directly - using current directory")
    else:
        print("ERROR: command_library.txt not found!")
        print("Please make sure you're running this from the correct directory.")
        print("The command_library.txt file should be in the same folder or data/ subfolder.")
        input("Press Enter to exit...")
        return None
    
    # Check if required files exist
    required_files = ['prompt_generator.py', 'workflow_selector.py']
    missing_files = [f for f in required_files if not os.path.exists(data_dir + f)]
    
    if missing_files:
        print(f"ERROR: Missing required files: {', '.join(missing_files)}")
        print("Please make sure all required files are present.")
        input("Press Enter to exit...")
        return None
    
    print("SUCCESS: All required files found!")
    print()
    print("This will launch the interactive prompt generator.")
    print("You'll be guided through a step-by-step process to create")
    print("customized dataPull agent prompts for your agency.")
    print()
    
    confirm = input("Ready to start? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled. Run this script again when you're ready!")
        return None
    
    print()
    print("Launching prompt generator...")
    print("=" * 50)
    print()
    
    # Add data directory to Python path if needed
    if data_dir:
        sys.path.insert(0, data_dir)
    
    return True

def load_agency_data_from_json():
    """Load agency data from existing JSON file"""
    print("=" * 60)
    print("Load Agency Data from JSON File")
    print("=" * 60)
    print()
    print("You can load existing agency data from a JSON file.")
    print("This is useful for:")
    print("• Updating existing agency configurations")
    print("• Creating variations of existing setups")
    print("• Batch processing multiple agencies")
    print()
    
    while True:
        json_file = input("Enter path to JSON file (or 'cancel' to go back): ").strip()
        
        if json_file.lower() == 'cancel':
            return None
            
        if not json_file:
            print("Please enter a valid file path.")
            continue
            
        # Handle relative paths
        if not os.path.isabs(json_file):
            json_file = os.path.join(os.getcwd(), json_file)
            
        if not os.path.exists(json_file):
            print(f"File not found: {json_file}")
            print("Please check the path and try again.")
            continue
            
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                agency_data = json.load(f)
            
            # Validate required fields
            required_fields = ['agency_name', 'agency_abbrev', 'city', 'county', 'state']
            missing_fields = [field for field in required_fields if field not in agency_data]
            
            if missing_fields:
                print(f"ERROR: Missing required fields in JSON: {', '.join(missing_fields)}")
                print("Please check your JSON file format.")
                continue
                
            print(f"\n✅ Successfully loaded agency data for: {agency_data['agency_name']} ({agency_data['agency_abbrev']})")
            print(f"   Location: {agency_data['city']}, {agency_data['county']}, {agency_data['state']}")
            print(f"   RMS: {agency_data.get('rms_name', 'Not specified')}")
            
            # Ask if they want to modify the data
            modify = input("\nDo you want to modify any of this data? (y/n): ").strip().lower()
            if modify == 'y':
                print("\nYou can modify the data by editing the JSON file and reloading, or")
                print("choose to go through the full onboarding process instead.")
                return None
                
            return agency_data
            
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON format: {e}")
            print("Please check your JSON file and try again.")
            continue
        except Exception as e:
            print(f"ERROR: Failed to load file: {e}")
            print("Please check the file and try again.")
            continue

def collect_agency_data():
    """Collect agency data through interactive prompts"""
    print("=" * 60)
    print("dataPull Agent Prompt Generator - Enhanced Version")
    print("=" * 60)
    print()
    print("This enhanced version includes:")
    print("• Validated improvements from field testing")
    print("• Secure credential encryption")
    print("• Flexible workflow selection")
    print("• RMS-specific optimizations")
    print()
    
    agency_data = {}
    
    # Phase 1: Basic Agency Information
    print("=== Phase 1: Basic Agency Information ===")
    agency_data['agency_name'] = input("Agency Name: ").strip()
    agency_data['agency_abbrev'] = input("Agency Abbreviation: ").strip()
    agency_data['city'] = input("City: ").strip()
    agency_data['county'] = input("County: ").strip()
    agency_data['state'] = input("State: ").strip()
    
    # Phase 2: RMS System Information
    print("\n=== Phase 2: RMS System Information ===")
    agency_data['rms_name'] = input("RMS System Name (or 'None' for OSINT only): ").strip()
    if agency_data['rms_name'].lower() != 'none':
        agency_data['rms_vendor'] = input("RMS Vendor: ").strip()
        agency_data['rms_username'] = input("RMS Username: ").strip()
        agency_data['rms_password'] = input("RMS Password: ").strip()
    else:
        agency_data['rms_vendor'] = 'None'
        agency_data['rms_username'] = 'None'
        agency_data['rms_password'] = 'None'
    
    # Phase 3: RMS Quirks and Issues
    print("\n=== Phase 3: RMS Quirks and Issues ===")
    print("Enter any known quirks or issues with your RMS system (one per line, empty line to finish):")
    quirks = []
    while True:
        quirk = input("Quirk: ").strip()
        if not quirk:
            break
        quirks.append(quirk)
    agency_data['rms_quirks'] = quirks
    
    # Phase 4: Field Abbreviations
    print("\n=== Phase 4: Field Abbreviations ===")
    print("Enter any field abbreviations your RMS uses (format: 'abbrev=full_name', empty line to finish):")
    abbreviations = []
    while True:
        abbrev = input("Abbreviation: ").strip()
        if not abbrev:
            break
        abbreviations.append(abbrev)
    agency_data['field_abbreviations'] = abbreviations
    
    # Phase 5: Environment
    print("\n=== Phase 5: Environment ===")
    agency_data['os'] = input("Operating System (Windows/Linux/Mac): ").strip() or "Windows"
    
    # Phase 6: Agency-Specific Systems
    print("\n=== Phase 6: Agency-Specific Systems ===")
    
    # COPWARE
    use_copware = input("Do you use COPWARE? (y/n): ").lower().strip() == 'y'
    if use_copware:
        agency_data['copware_username'] = input("COPWARE Username: ").strip()
        agency_data['copware_password'] = input("COPWARE Password: ").strip()
    
    # Other Systems
    other_systems = {}
    while True:
        system_name = input("Other system name (or 'done'): ").strip()
        if system_name.lower() == 'done':
            break
        if system_name:
            username = input(f"{system_name} Username: ").strip()
            password = input(f"{system_name} Password: ").strip()
            other_systems[system_name] = {
                'username': username,
                'password': password
            }
    
    if other_systems:
        agency_data['other_systems'] = other_systems
    
    # Phase 7: Workflow Selection
    print("\n=== Phase 7: Workflow Selection ===")
    print("The system includes 5 basic workflows by default:")
    print("• _PRL - Person Lookup")
    print("• _CL - Case Lookup") 
    print("• _AL - Address Lookup")
    print("• _LPL - License Plate Lookup")
    print("• _UQN - Unknown Query NLP")
    
    workflow_selector = WorkflowSelector()
    additional_workflows = workflow_selector.display_workflow_menu()
    
    if additional_workflows:
        agency_data['additional_workflows'] = additional_workflows
        print(f"\nSelected {len(additional_workflows)} additional workflows:")
        print(workflow_selector.get_workflow_summary(additional_workflows))
    
    # Phase 8: Summary and Confirmation
    print("\n=== Phase 8: Summary and Confirmation ===")
    print("Please review your agency configuration:")
    print(f"Agency: {agency_data['agency_name']} ({agency_data['agency_abbrev']})")
    print(f"Location: {agency_data['city']}, {agency_data['county']}, {agency_data['state']}")
    print(f"RMS: {agency_data['rms_name']} ({agency_data['rms_vendor']})")
    print(f"OS: {agency_data['os']}")
    print(f"Workflows: 5 basic + {len(additional_workflows) if additional_workflows else 0} additional")
    
    confirm = input("\nIs this information correct? (y/n): ").lower().strip()
    if confirm != 'y':
        print("Please restart the process with correct information.")
        return None
    
    return agency_data

def generate_prompts(agency_data):
    """Generate all prompt formats"""
    print("\n=== Generating Prompts ===")
    
    generator = EnhancedPromptGeneratorV2()
    
    # Get additional workflows
    additional_workflows = agency_data.get('additional_workflows', [])
    
    # Generate enhanced prompt
    print("Generating enhanced prompt...")
    enhanced_prompt = generator.generate_enhanced_prompt(agency_data, additional_workflows)
    
    # Create output directory
    output_dir = f"outputs/{agency_data['agency_abbrev']}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save enhanced prompt
    enhanced_filename = f"{output_dir}/{agency_data['agency_abbrev']}_enhanced_prompt.txt"
    with open(enhanced_filename, 'w', encoding='utf-8') as f:
        f.write(enhanced_prompt)
    
    # Save agency data
    agency_filename = f"{output_dir}/{agency_data['agency_abbrev']}_agency_data.json"
    with open(agency_filename, 'w', encoding='utf-8') as f:
        json.dump(agency_data, f, indent=2)
    
    print(f"Enhanced prompt saved to: {enhanced_filename}")
    print(f"Agency data saved to: {agency_filename}")
    
    return output_dir

def main():
    """Main function"""
    try:
        # Check environment first
        if not check_environment():
            return
        
        # Welcome message and option selection
        print("=" * 60)
        print("dataPull Agent Prompt Generator - Enhanced Version")
        print("=" * 60)
        print()
        print("Choose how you'd like to provide agency data:")
        print("1. Interactive onboarding (guided step-by-step process)")
        print("2. Import from JSON file (load existing agency data)")
        print()
        
        while True:
            choice = input("Enter your choice (1 or 2): ").strip()
            if choice == '1':
                agency_data = collect_agency_data()
                break
            elif choice == '2':
                agency_data = load_agency_data_from_json()
                break
            else:
                print("Please enter 1 or 2.")
                continue
        
        if not agency_data:
            return
        
        # Generate prompts
        output_dir = generate_prompts(agency_data)
        
        print(f"\n=== Generation Complete ===")
        print(f"All files saved to: {output_dir}")
        print("\nThe enhanced prompt includes:")
        print("• Validated improvements from field testing")
        print("• Secure credential encryption")
        print("• RMS-specific optimizations")
        print("• Selected workflows")
        print("• 5-phase operational structure")
        
    except KeyboardInterrupt:
        print("\n\nProcess cancelled by user.")
    except Exception as e:
        print(f"\n\nERROR: An error occurred: {e}")
        print("Please check your input and try again.")

if __name__ == "__main__":
    main()
