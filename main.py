#!/usr/bin/env python3
"""
TCO Automation System - Main Entry Point

This script orchestrates the complete workflow:
1. Extract data from vendor proposals (FIS Word docs, Jack Henry Excel)
2. Normalize data to TCO schema
3. Populate TCO Excel template
"""

import argparse
import os
import sys
from extractors import extract_fis_proposal, extract_jack_henry_proposal
from mappers import normalize_vendor_data
from writers import TCOWriter


def process_fis_proposal(proposal_path: str, tco_template: str, output_path: str, term: str = '7_year'):
    """
    Process FIS proposal and populate TCO template
    
    Args:
        proposal_path: Path to FIS Word proposal
        tco_template: Path to TCO Excel template
        output_path: Path for output file
        term: Contract term ('5_year', '7_year', '10_year')
    """
    print("="*70)
    print("PROCESSING FIS PROPOSAL")
    print("="*70)
    print(f"Proposal: {proposal_path}")
    print(f"Template: {tco_template}")
    print(f"Term: {term}")
    print(f"Output: {output_path}")
    print()
    
    # Step 1: Extract data from FIS proposal
    print("Step 1: Extracting data from FIS proposal...")
    fis_data = extract_fis_proposal(proposal_path)
    
    # Step 2: Normalize data
    print("\nStep 2: Normalizing data to TCO schema...")
    normalized_data = normalize_vendor_data(fis_data, 'FIS', term=term)
    
    # Step 3: Populate TCO template
    print("\nStep 3: Populating TCO template...")
    writer = TCOWriter(tco_template, output_path)
    writer.write_vendor_data(normalized_data, 'FIS')
    result_path = writer.save()
    
    print("\n" + "="*70)
    print("SUCCESS!")
    print("="*70)
    print(f"TCO file created: {result_path}")
    print(f"Total line items: {len(normalized_data)}")
    
    return result_path


def process_jack_henry_proposal(proposal_path: str, tco_template: str, output_path: str, scenario: str = 'Proposal_1'):
    """
    Process Jack Henry proposal and populate TCO template
    
    Args:
        proposal_path: Path to Jack Henry Excel proposal
        tco_template: Path to TCO Excel template
        output_path: Path for output file
        scenario: Which proposal scenario to use ('Proposal_1', 'Proposal_2', 'Proposal_3')
    """
    print("="*70)
    print("PROCESSING JACK HENRY PROPOSAL")
    print("="*70)
    print(f"Proposal: {proposal_path}")
    print(f"Template: {tco_template}")
    print(f"Scenario: {scenario}")
    print(f"Output: {output_path}")
    print()
    
    # Step 1: Extract data from Jack Henry proposal
    print("Step 1: Extracting data from Jack Henry proposal...")
    jh_data = extract_jack_henry_proposal(proposal_path)
    
    # Step 2: Normalize data
    print("\nStep 2: Normalizing data to TCO schema...")
    normalized_data = normalize_vendor_data(jh_data, 'Jack Henry', scenario=scenario)
    
    # Step 3: Populate TCO template
    print("\nStep 3: Populating TCO template...")
    writer = TCOWriter(tco_template, output_path)
    writer.write_vendor_data(normalized_data, 'Jack Henry')
    result_path = writer.save()
    
    print("\n" + "="*70)
    print("SUCCESS!")
    print("="*70)
    print(f"TCO file created: {result_path}")
    print(f"Total line items: {len(normalized_data)}")
    
    return result_path


def process_both_vendors(fis_proposal: str, jh_proposal: str, tco_template: str, 
                        output_path: str, fis_term: str = '7_year', jh_scenario: str = 'Proposal_1'):
    """
    Process both FIS and Jack Henry proposals into a single TCO comparison
    
    Args:
        fis_proposal: Path to FIS Word proposal
        jh_proposal: Path to Jack Henry Excel proposal
        tco_template: Path to TCO Excel template
        output_path: Path for output file
        fis_term: FIS contract term
        jh_scenario: Jack Henry proposal scenario
    """
    print("="*70)
    print("PROCESSING BOTH VENDORS FOR SIDE-BY-SIDE COMPARISON")
    print("="*70)
    print(f"FIS Proposal: {fis_proposal}")
    print(f"Jack Henry Proposal: {jh_proposal}")
    print(f"Template: {tco_template}")
    print(f"Output: {output_path}")
    print()
    
    # Extract and normalize FIS data
    print("Processing FIS proposal...")
    fis_data = extract_fis_proposal(fis_proposal)
    fis_normalized = normalize_vendor_data(fis_data, 'FIS', term=fis_term)
    
    # Extract and normalize Jack Henry data
    print("\nProcessing Jack Henry proposal...")
    jh_data = extract_jack_henry_proposal(jh_proposal)
    jh_normalized = normalize_vendor_data(jh_data, 'Jack Henry', scenario=jh_scenario)
    
    # Populate TCO template with both vendors
    print("\nPopulating TCO template...")
    writer = TCOWriter(tco_template, output_path)
    writer.write_vendor_data(fis_normalized, 'FIS')
    writer.write_vendor_data(jh_normalized, 'Jack Henry')
    result_path = writer.save()
    
    print("\n" + "="*70)
    print("SUCCESS!")
    print("="*70)
    print(f"TCO comparison file created: {result_path}")
    print(f"FIS line items: {len(fis_normalized)}")
    print(f"Jack Henry line items: {len(jh_normalized)}")
    
    return result_path


def main():
    """Main entry point with CLI argument parsing"""
    parser = argparse.ArgumentParser(
        description='TCO Automation System - Extract and populate vendor proposals',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Process FIS proposal only
  python main.py --fis proposal.docx --template tco.xlsx --output result.xlsx
  
  # Process Jack Henry proposal only
  python main.py --jh proposal.xlsx --template tco.xlsx --output result.xlsx
  
  # Process both for side-by-side comparison
  python main.py --fis fis.docx --jh jh.xlsx --template tco.xlsx --output comparison.xlsx
        '''
    )
    
    parser.add_argument('--fis', type=str, help='Path to FIS Word proposal')
    parser.add_argument('--jh', type=str, help='Path to Jack Henry Excel proposal')
    parser.add_argument('--template', type=str, required=True, help='Path to TCO Excel template')
    parser.add_argument('--output', type=str, required=True, help='Path for output file')
    parser.add_argument('--fis-term', type=str, default='7_year', 
                       choices=['5_year', '7_year', '10_year'],
                       help='FIS contract term (default: 7_year)')
    parser.add_argument('--jh-scenario', type=str, default='Proposal_1',
                       choices=['Proposal_1', 'Proposal_2', 'Proposal_3'],
                       help='Jack Henry proposal scenario (default: Proposal_1)')
    
    args = parser.parse_args()
    
    # Validate inputs
    if not args.fis and not args.jh:
        parser.error("At least one of --fis or --jh must be provided")
    
    if args.fis and not os.path.exists(args.fis):
        parser.error(f"FIS proposal file not found: {args.fis}")
    
    if args.jh and not os.path.exists(args.jh):
        parser.error(f"Jack Henry proposal file not found: {args.jh}")
    
    if not os.path.exists(args.template):
        parser.error(f"TCO template file not found: {args.template}")
    
    # Process based on inputs
    try:
        if args.fis and args.jh:
            # Both vendors
            result = process_both_vendors(
                args.fis, args.jh, args.template, args.output,
                args.fis_term, args.jh_scenario
            )
        elif args.fis:
            # FIS only
            result = process_fis_proposal(
                args.fis, args.template, args.output, args.fis_term
            )
        else:
            # Jack Henry only
            result = process_jack_henry_proposal(
                args.jh, args.template, args.output, args.jh_scenario
            )
        
        return 0
    
    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
