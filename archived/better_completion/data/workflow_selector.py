#!/usr/bin/env python3
"""
Interactive Workflow Selector for Enhanced Prompt Generator
Allows users to select additional workflows beyond the basic 5
"""

import csv
import os
from typing import List, Dict

class WorkflowSelector:
    """Interactive workflow selection system"""
    
    def __init__(self, csv_file='workflows_database.csv'):
        # Try data/ subdirectory first (for executable), then current directory
        if os.path.exists('data/workflows_database.csv'):
            self.csv_file = 'data/workflows_database.csv'
        else:
            self.csv_file = csv_file
        self.workflows = self._load_workflows()
        self.basic_workflows = ['_PERSON_LOOKUP', '_CASE_LOOKUP', '_ADDRESS_LOOKUP', '_LICENSE_PLATE_LOOKUP', '_UNKNOWN_QUERY_NLP']
    
    def _load_workflows(self) -> List[Dict]:
        """Load workflows from CSV"""
        workflows = []
        with open(self.csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                workflows.append(row)
        return workflows
    
    def get_available_workflows(self) -> List[Dict]:
        """Get all available workflows excluding basic ones"""
        available = []
        for workflow in self.workflows:
            if workflow['Full Command'] not in self.basic_workflows:
                available.append(workflow)
        return available
    
    def get_workflows_by_category(self) -> Dict[str, List[Dict]]:
        """Group workflows by category"""
        categories = {}
        for workflow in self.workflows:
            if workflow['Full Command'] not in self.basic_workflows:
                rms = workflow['RMS System']
                if rms not in categories:
                    categories[rms] = []
                categories[rms].append(workflow)
        return categories
    
    def display_workflow_menu(self) -> List[str]:
        """Display interactive menu and return selected workflows"""
        print("\n" + "="*60)
        print("WORKFLOW SELECTION MENU")
        print("="*60)
        print("\nBasic workflows (always included):")
        for cmd in self.basic_workflows:
            workflow = next((w for w in self.workflows if w['Full Command'] == cmd), None)
            if workflow:
                print(f"  • {workflow['Short Form']} - {workflow['Description']}")
        
        print(f"\nAdditional workflows available: {len(self.get_available_workflows())}")
        print("\nWould you like to add additional workflows? (y/n): ", end="")
        
        if input().lower().strip() != 'y':
            return []
        
        # Group by category
        categories = self.get_workflows_by_category()
        
        selected_workflows = []
        
        for category, workflows in categories.items():
            print(f"\n--- {category.upper()} WORKFLOWS ---")
            for i, workflow in enumerate(workflows, 1):
                print(f"{i:2d}. {workflow['Short Form']:8} - {workflow['Description']}")
            
            print(f"\nSelect {category} workflows (comma-separated numbers, or 'all' for all, or 'skip' to skip): ", end="")
            selection = input().strip()
            
            if selection.lower() == 'skip':
                continue
            elif selection.lower() == 'all':
                selected_workflows.extend([w['Full Command'] for w in workflows])
            else:
                try:
                    indices = [int(x.strip()) - 1 for x in selection.split(',')]
                    for idx in indices:
                        if 0 <= idx < len(workflows):
                            selected_workflows.append(workflows[idx]['Full Command'])
                except ValueError:
                    print("Invalid selection, skipping this category.")
        
        return selected_workflows
    
    def get_workflow_summary(self, selected_workflows: List[str]) -> str:
        """Get summary of selected workflows"""
        summary = []
        for cmd in selected_workflows:
            workflow = next((w for w in self.workflows if w['Full Command'] == cmd), None)
            if workflow:
                summary.append(f"• {workflow['Short Form']} - {workflow['Description']}")
        return '\n'.join(summary)

def main():
    """Test the workflow selector"""
    print("=== Workflow Selector Test ===")
    
    selector = WorkflowSelector()
    
    # Display available workflows
    available = selector.get_available_workflows()
    print(f"Available workflows: {len(available)}")
    
    # Show categories
    categories = selector.get_workflows_by_category()
    print("\nWorkflow categories:")
    for category, workflows in categories.items():
        print(f"  {category}: {len(workflows)} workflows")
    
    # Interactive selection
    selected = selector.display_workflow_menu()
    
    print(f"\nSelected workflows: {len(selected)}")
    if selected:
        print(selector.get_workflow_summary(selected))

if __name__ == "__main__":
    main()
