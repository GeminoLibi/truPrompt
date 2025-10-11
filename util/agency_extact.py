#!/usr/bin/env python3
"""
Agency Information Extractor and Signature Recorder
===================================================

This script iterates through output files, extracts agency information,
and records existing signatures for documentation and tracking purposes.

Features:
- Extract agency data from existing output files
- Record existing signatures for each agency
- Comprehensive logging of all extracted information
- Generate reports of agency configurations
- No modifications to original files (read-only operation)
"""

import os
import re
import json
from datetime import datetime
from typing import Dict, List, Optional

# --- Configuration ---
OUTPUTS_DIR = "outputs"
LOG_FILE = "agency_extraction_log.txt"
AGENCY_DATA_FILE = "agency_data.json"

# --- Logging Class ---
class Logger:
    def __init__(self, log_file: str):
        self.log_file = log_file
        self.ensure_log_exists()
    
    def ensure_log_exists(self):
        """Create log file with header if it doesn't exist"""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write(f"Agency Update Log - Started {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        print(log_entry.strip())
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    
    def log_error(self, message: str):
        """Log an error message"""
        self.log(f"ERROR: {message}", "ERROR")
    
    def log_success(self, message: str):
        """Log a success message"""
        self.log(f"SUCCESS: {message}", "SUCCESS")

# --- Agency Data Extractor ---
class AgencyDataExtractor:
    def __init__(self, logger: Logger):
        self.logger = logger
    
    def extract_agency_data(self, file_path: str) -> Optional[Dict]:
        """Extract agency information from a prompt file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract agency information from Section 1
            agency_data = {}
            
            # Agency Name
            name_match = re.search(r'\* Agency Name: `([^`]+)`', content)
            if name_match:
                agency_data['agency_name'] = name_match.group(1)
            
            # Agency Abbreviation
            abbr_match = re.search(r'\* Agency Abbreviation: `([^`]+)`', content)
            if abbr_match:
                agency_data['agency_abbr'] = abbr_match.group(1)
            
            # City
            city_match = re.search(r'\* City: `([^`]+)`', content)
            if city_match:
                agency_data['city'] = city_match.group(1)
            
            # County
            county_match = re.search(r'\* County: `([^`]+)`', content)
            if county_match:
                agency_data['county'] = county_match.group(1)
            
            # State
            state_match = re.search(r'\* State: `([^`]+)`', content)
            if state_match:
                agency_data['state'] = state_match.group(1)
            
            # RMS Name
            rms_match = re.search(r'\* Records Management System \(RMS\): `([^`]+)`', content)
            if rms_match:
                agency_data['rms_name'] = rms_match.group(1)
            
            # Operating System
            os_match = re.search(r'\* Operating System: `([^`]+)`', content)
            if os_match:
                agency_data['os_name'] = os_match.group(1)
            
            # Extract existing signature if present
            sig_match = re.search(r'\* \*\*Secure Signature\*\*: `([^`]+)`', content)
            if sig_match:
                agency_data['existing_signature'] = sig_match.group(1)
            
            # Extract credentials
            rms_user_match = re.search(r'\* \*\*RMS Username\*\*: `([^`]+)`', content)
            if rms_user_match:
                agency_data['rms_username'] = rms_user_match.group(1)
            
            rms_pass_match = re.search(r'\* \*\*RMS Password\*\*: `([^`]+)`', content)
            if rms_pass_match:
                agency_data['rms_password'] = rms_pass_match.group(1)
            
            return agency_data if agency_data else None
            
        except Exception as e:
            self.logger.log_error(f"Failed to extract agency data from {file_path}: {e}")
            return None

# --- Agency Data Manager ---
class AgencyDataManager:
    def __init__(self, agency_data_file: str, logger: Logger):
        self.agency_data_file = agency_data_file
        self.logger = logger
        self.data = self.load_data()
    
    def load_data(self) -> Dict:
        """Load the agency data and processed files"""
        try:
            if os.path.exists(self.agency_data_file):
                with open(self.agency_data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {
                'processed_files': {},
                'agencies': {},
                'last_updated': None
            }
        except Exception as e:
            self.logger.log_error(f"Failed to load agency data file: {e}")
            return {
                'processed_files': {},
                'agencies': {},
                'last_updated': None
            }
    
    def save_data(self) -> None:
        """Save the agency data and processed files"""
        try:
            self.data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(self.agency_data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            self.logger.log_error(f"Failed to save agency data file: {e}")
    
    def is_file_processed(self, file_path: str) -> bool:
        """Check if a file has already been processed"""
        filename = os.path.basename(file_path)
        return filename in self.data['processed_files']
    
    def mark_file_processed(self, file_path: str, agency_data: Dict, file_hash: str = None) -> None:
        """Mark a file as processed and store agency data"""
        filename = os.path.basename(file_path)
        agency_abbr = agency_data.get('agency_abbr', 'UNKNOWN')
        
        # Store processed file info
        self.data['processed_files'][filename] = {
            'processed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'file_path': file_path,
            'file_hash': file_hash,
            'agency_abbr': agency_abbr
        }
        
        # Store agency data
        self.data['agencies'][agency_abbr] = {
            'agency_name': agency_data.get('agency_name', 'Unknown'),
            'agency_abbr': agency_abbr,
            'city': agency_data.get('city', 'Unknown'),
            'county': agency_data.get('county', 'Unknown'),
            'state': agency_data.get('state', 'Unknown'),
            'rms_name': agency_data.get('rms_name', 'Unknown'),
            'os_name': agency_data.get('os_name', 'Unknown'),
            'rms_username': agency_data.get('rms_username', 'N/A'),
            'rms_password': agency_data.get('rms_password', 'N/A'),
            'signature': agency_data.get('existing_signature', 'No signature found'),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'source_files': self.data['agencies'].get(agency_abbr, {}).get('source_files', [])
        }
        
        # Add this file to the agency's source files if not already there
        if filename not in self.data['agencies'][agency_abbr]['source_files']:
            self.data['agencies'][agency_abbr]['source_files'].append(filename)
        
        self.save_data()
        self.logger.log(f"Marked {filename} as processed and stored data for {agency_abbr}")
    
    def get_file_hash(self, file_path: str) -> str:
        """Get a simple hash of the file for change detection"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return str(hash(content))
        except Exception as e:
            self.logger.log_error(f"Failed to hash file {file_path}: {e}")
            return ""
    
    def get_all_agencies(self) -> Dict:
        """Get all stored agency data"""
        return self.data['agencies']
    
    def get_processed_files(self) -> Dict:
        """Get all processed files"""
        return self.data['processed_files']

# --- Signature Recorder ---
class SignatureRecorder:
    def __init__(self, logger: Logger):
        self.logger = logger
    
    def record_signature(self, agency_abbr: str, signature: str) -> None:
        """Record a signature for an agency"""
        self.logger.log(f"Recorded signature for {agency_abbr}: {signature}")

# --- File Analyzer ---
class FileAnalyzer:
    def __init__(self, logger: Logger):
        self.logger = logger
    
    def analyze_file(self, file_path: str, agency_data: Dict) -> Dict:
        """Analyze a file and return analysis results"""
        try:
            analysis = {
                'file_path': file_path,
                'agency_data': agency_data,
                'has_signature': bool(agency_data.get('existing_signature')),
                'signature': agency_data.get('existing_signature', 'No signature found'),
                'analysis_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            self.logger.log(f"Analyzed {file_path}: {'Has signature' if analysis['has_signature'] else 'No signature'}")
            return analysis
            
        except Exception as e:
            self.logger.log_error(f"Failed to analyze file {file_path}: {e}")
            return None

# --- Main Processor ---
class AgencyProcessor:
    def __init__(self):
        self.logger = Logger(LOG_FILE)
        self.extractor = AgencyDataExtractor(self.logger)
        self.analyzer = FileAnalyzer(self.logger)
        self.recorder = SignatureRecorder(self.logger)
        self.data_manager = AgencyDataManager(AGENCY_DATA_FILE, self.logger)
    
    def process_outputs_directory(self) -> Dict:
        """Process all files in the outputs directory"""
        if not os.path.exists(OUTPUTS_DIR):
            self.logger.log_error(f"Outputs directory '{OUTPUTS_DIR}' not found")
            return {}
        
        results = {
            'processed': 0,
            'new_files': 0,
            'skipped_files': 0,
            'successful': 0,
            'failed': 0,
            'agencies': {},
            'analyses': []
        }
        
        # Get all .txt files in outputs directory
        output_files = [f for f in os.listdir(OUTPUTS_DIR) if f.endswith('.txt')]
        
        if not output_files:
            self.logger.log("No .txt files found in outputs directory")
            return results
        
        self.logger.log(f"Found {len(output_files)} total files in outputs directory")
        
        # Filter to only new files
        new_files = []
        for filename in output_files:
            file_path = os.path.join(OUTPUTS_DIR, filename)
            if not self.data_manager.is_file_processed(file_path):
                new_files.append(filename)
            else:
                results['skipped_files'] += 1
                self.logger.log(f"Skipping already processed file: {filename}")
        
        if not new_files:
            self.logger.log("No new files to analyze - all files have been processed")
            return results
        
        self.logger.log(f"Found {len(new_files)} new files to analyze")
        
        for filename in new_files:
            file_path = os.path.join(OUTPUTS_DIR, filename)
            results['processed'] += 1
            results['new_files'] += 1
            
            self.logger.log(f"Analyzing new file: {filename}")
            
            # Extract agency data
            agency_data = self.extractor.extract_agency_data(file_path)
            
            if not agency_data:
                self.logger.log_error(f"Could not extract agency data from {filename}")
                results['failed'] += 1
                continue
            
            # Store agency data
            agency_abbr = agency_data.get('agency_abbr', 'UNKNOWN')
            results['agencies'][agency_abbr] = agency_data
            
            # Analyze file
            analysis = self.analyzer.analyze_file(file_path, agency_data)
            
            if analysis:
                results['analyses'].append(analysis)
                results['successful'] += 1
                
                # Record signature if it exists
                if agency_data.get('existing_signature'):
                    self.recorder.record_signature(agency_abbr, agency_data['existing_signature'])
                
                # Mark file as processed and store agency data
                file_hash = self.data_manager.get_file_hash(file_path)
                self.data_manager.mark_file_processed(file_path, agency_data, file_hash)
                
                self.logger.log_success(f"Successfully analyzed {filename}")
            else:
                results['failed'] += 1
        
        return results
    
    def generate_summary_report(self, results: Dict) -> str:
        """Generate a summary report of the analysis results"""
        report = []
        report.append("=" * 80)
        report.append("AGENCY INFORMATION EXTRACTION REPORT")
        report.append("=" * 80)
        report.append(f"Analysis completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        report.append("STATISTICS:")
        report.append(f"  Total files in directory: {results['processed'] + results['skipped_files']}")
        report.append(f"  New files analyzed: {results['new_files']}")
        report.append(f"  Previously processed files skipped: {results['skipped_files']}")
        report.append(f"  Successfully analyzed: {results['successful']}")
        report.append(f"  Failed analyses: {results['failed']}")
        report.append("")
        
        # Get all agencies from stored data
        all_agencies = self.data_manager.get_all_agencies()
        if all_agencies:
            report.append("AGENCY INFORMATION:")
            for abbr, data in all_agencies.items():
                report.append(f"  {abbr}: {data.get('agency_name', 'Unknown')}")
                report.append(f"    Location: {data.get('city', 'Unknown')}, {data.get('state', 'Unknown')}")
                report.append(f"    RMS: {data.get('rms_name', 'Unknown')}")
                signature = data.get('signature', 'No signature found')
                report.append(f"    Current Signature: {signature}")
                report.append(f"    Source Files: {', '.join(data.get('source_files', []))}")
                report.append("")
        
        # Add signature summary from stored data
        agencies_with_signatures = [a for a in all_agencies.values() if a.get('signature') != 'No signature found']
        report.append("SIGNATURE SUMMARY:")
        report.append(f"  Agencies with signatures: {len(agencies_with_signatures)}")
        report.append(f"  Agencies without signatures: {len(all_agencies) - len(agencies_with_signatures)}")
        report.append("")
        
        if agencies_with_signatures:
            report.append("RECORDED SIGNATURES:")
            for agency in agencies_with_signatures:
                abbr = agency.get('agency_abbr', 'UNKNOWN')
                signature = agency.get('signature', 'No signature found')
                report.append(f"  {abbr}: {signature}")
        
        report.append("=" * 80)
        return "\n".join(report)

def main():
    """Main execution function"""
    print("Agency Information Extractor and Signature Recorder")
    print("=" * 55)
    
    processor = AgencyProcessor()
    
    # Process all output files
    results = processor.process_outputs_directory()
    
    # Generate and display summary
    summary = processor.generate_summary_report(results)
    print("\n" + summary)
    
    # Log summary to file
    processor.logger.log("\n" + summary)
    
    print(f"\nDetailed log saved to: {LOG_FILE}")
    print("Note: This is a read-only operation - no files were modified.")

if __name__ == "__main__":
    main()
