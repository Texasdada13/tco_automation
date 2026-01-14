"""
Batch Generator - Creates standardized outputs for all vendors

Automatically discovers all JSON extractions and generates standardized Excel outputs
"""

import json
import glob
from pathlib import Path
from create_standardized_vendor_output import create_standardized_output


def discover_extractions():
    """Discover all JSON extraction files and group by client"""
    extraction_files = glob.glob('Extracted JSON/*_extraction_ai.json')

    clients = {}

    for file_path in extraction_files:
        # Parse filename to extract client and vendor
        filename = Path(file_path).stem  # Remove .json extension
        filename = filename.replace('_extraction_ai', '')  # Remove suffix

        # Try to parse client_vendor pattern
        parts = filename.split('_')

        # Heuristic to determine vendor (last 1-2 words)
        if 'fis' in filename.lower():
            vendor = 'FIS'
            client_parts = [p for p in parts if 'fis' not in p.lower()]
        elif 'csi' in filename.lower():
            vendor = 'CSI'
            client_parts = [p for p in parts if 'csi' not in p.lower()]
        elif 'jack' in filename.lower() or 'henry' in filename.lower():
            vendor = 'Jack Henry'
            client_parts = [p for p in parts if 'jack' not in p.lower() and 'henry' not in p.lower()]
        else:
            # Unknown vendor, use last part
            vendor = parts[-1].upper()
            client_parts = parts[:-1]

        # Construct client name
        client_name = ' '.join(word.capitalize() for word in client_parts)

        # Clean up common patterns
        client_name = client_name.replace('_', ' ')

        if client_name not in clients:
            clients[client_name] = []

        clients[client_name].append({
            'vendor': vendor,
            'file': file_path,
            'display_name': f"{client_name} - {vendor}"
        })

    return clients


def generate_all_standardized():
    """Generate standardized outputs for all discovered extractions"""

    print("="*120)
    print("BATCH STANDARDIZED OUTPUT GENERATOR")
    print("="*120)
    print()

    # Discover all extractions
    clients = discover_extractions()

    print(f"Discovered {len(clients)} clients with extractions:")
    for client_name, vendors in clients.items():
        print(f"  {client_name}:")
        for vendor_info in vendors:
            print(f"    - {vendor_info['vendor']}: {vendor_info['file']}")
    print()

    # Generate standardized output for each
    generated_files = []

    for client_name, vendors in clients.items():
        for vendor_info in vendors:
            print(f"\nProcessing: {vendor_info['display_name']}")
            print("-" * 120)

            try:
                output_file = create_standardized_output(
                    client_name=client_name,
                    vendor_name=vendor_info['vendor'],
                    json_file=vendor_info['file']
                )

                generated_files.append({
                    'client': client_name,
                    'vendor': vendor_info['vendor'],
                    'output': output_file
                })

            except Exception as e:
                print(f"[ERROR] Failed to process {vendor_info['display_name']}: {e}")

    # Summary
    print("\n" + "="*120)
    print("BATCH GENERATION COMPLETE")
    print("="*120)
    print(f"\nGenerated {len(generated_files)} standardized Excel files:")
    for file_info in generated_files:
        print(f"  [{file_info['vendor']:15s}] {file_info['client']:30s} -> {Path(file_info['output']).name}")

    print("\n" + "="*120)
    print("ALL OUTPUTS IN: TCO Output/")
    print("="*120)


if __name__ == '__main__':
    generate_all_standardized()
