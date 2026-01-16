"""
TCO Automation Dashboard
Streamlit-based web interface for managing client proposals and comparisons
"""

import streamlit as st
import json
import os
from pathlib import Path
from datetime import datetime
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="TCO Automation Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
EXTRACTED_JSON_DIR = Path("Extracted JSON")
TCO_OUTPUT_DIR = Path("TCO Output")


def get_clients_from_extractions() -> dict:
    """
    Scan Extracted JSON folder and group files by client.
    Returns dict: {client_name: {vendor: [files]}}
    """
    clients = {}

    if not EXTRACTED_JSON_DIR.exists():
        return clients

    for file in EXTRACTED_JSON_DIR.glob("*_extraction_ai.json"):
        try:
            with open(file, 'r') as f:
                data = json.load(f)

            # Extract client name from data or filename
            client_name = data.get('client')

            # Handle None or empty client name
            if not client_name or client_name == 'Unknown':
                # Try to parse from filename
                parts = file.stem.replace('_extraction_ai', '').split('_')
                # Try to identify vendor suffix and use rest as client
                vendors = ['fis', 'jh', 'csi', 'fiserv', 'finastra', 'jack_henry']
                found_vendor = False
                for v in vendors:
                    if len(parts) > 1 and (v in parts[-1].lower() or v in parts[-2].lower()):
                        client_name = '_'.join(parts[:-1]).replace('_', ' ').title()
                        found_vendor = True
                        break
                if not found_vendor:
                    client_name = file.stem.replace('_extraction_ai', '').replace('_', ' ').title()

            # Final fallback - ensure we never have None
            if not client_name:
                client_name = f"Unknown ({file.stem})"

            # Get vendor from data
            vendor_raw = data.get('vendor', 'Unknown')
            # Normalize vendor name
            vendor = vendor_raw.upper()
            for v in ['FIS', 'JACK_HENRY', 'JH', 'CSI', 'FISERV', 'FINASTRA']:
                if v in vendor:
                    vendor = v.replace('JH', 'JACK_HENRY')
                    break

            # Add to clients dict
            if client_name not in clients:
                clients[client_name] = {}
            if vendor not in clients[client_name]:
                clients[client_name][vendor] = []

            clients[client_name][vendor].append({
                'file': str(file),
                'data': data
            })

        except Exception as e:
            st.warning(f"Could not load {file.name}: {e}")

    return clients


def load_extraction_data(filepath: str) -> dict:
    """Load and return extraction JSON data."""
    with open(filepath, 'r') as f:
        return json.load(f)


def display_extraction_summary(data: dict):
    """Display a summary of extraction data."""
    st.subheader("Proposal Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Vendor", data.get('vendor', 'N/A'))
    with col2:
        st.metric("Contract Term", f"{data.get('contract_term', 'N/A')} years")
    with col3:
        st.metric("Document Date", data.get('document_date', 'N/A'))

    # Line items summary
    line_items = data.get('line_items', [])
    if line_items:
        st.subheader(f"Line Items ({len(line_items)} total)")

        # Calculate totals
        total_monthly = sum(item.get('monthly_fee', 0) or 0 for item in line_items)
        total_onetime = sum(item.get('one_time_fee', 0) or 0 for item in line_items)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Monthly Fees", f"${total_monthly:,.2f}")
        with col2:
            st.metric("Total One-Time Fees", f"${total_onetime:,.2f}")

        # Show line items in a table
        df = pd.DataFrame([
            {
                'Solution': item.get('solution_name', ''),
                'Category': item.get('category', ''),
                'Monthly Fee': f"${item.get('monthly_fee', 0) or 0:,.2f}",
                'One-Time Fee': f"${item.get('one_time_fee', 0) or 0:,.2f}",
                'Fee Type': item.get('fee_type', ''),
                'Confidence': f"{(item.get('overall_confidence', 0) or 0) * 100:.0f}%"
            }
            for item in line_items
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)


def run_comparison(client_name: str, vendors: list, client_data: dict):
    """Run TCO comparison for selected client and vendors."""
    st.info(f"Running comparison for {client_name} across {len(vendors)} vendors...")

    # Gather extraction files for selected vendors
    comparison_data = {}
    for vendor in vendors:
        if vendor in client_data:
            # Use the first file for each vendor
            file_info = client_data[vendor][0]
            comparison_data[vendor] = file_info['data']

    if len(comparison_data) < 2:
        st.error("Need at least 2 vendors to compare")
        return

    # Display comparison results
    st.subheader("Comparison Results")

    # Calculate 7-year TCO for each vendor
    results = []
    for vendor, data in comparison_data.items():
        line_items = data.get('line_items', [])
        total_monthly = sum(item.get('monthly_fee', 0) or 0 for item in line_items)
        total_onetime = sum(item.get('one_time_fee', 0) or 0 for item in line_items)
        contract_term = data.get('contract_term', 7)

        # Simple TCO calculation (monthly * 12 * years + one-time)
        tco_7yr = (total_monthly * 12 * contract_term) + total_onetime

        results.append({
            'Vendor': vendor,
            'Monthly Fees': total_monthly,
            'One-Time Fees': total_onetime,
            'Contract Term': contract_term,
            '7-Year TCO': tco_7yr
        })

    # Sort by TCO
    results_df = pd.DataFrame(results).sort_values('7-Year TCO')

    # Display metrics
    cols = st.columns(len(results))
    for i, (idx, row) in enumerate(results_df.iterrows()):
        with cols[i]:
            rank = i + 1
            rank_emoji = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else ""
            st.metric(
                f"{rank_emoji} {row['Vendor']}",
                f"${row['7-Year TCO']:,.0f}",
                delta=f"${row['7-Year TCO'] - results_df['7-Year TCO'].min():,.0f} vs lowest" if rank > 1 else "Lowest TCO"
            )

    # Show detailed comparison table
    st.subheader("Detailed Comparison")
    display_df = results_df.copy()
    display_df['Monthly Fees'] = display_df['Monthly Fees'].apply(lambda x: f"${x:,.2f}")
    display_df['One-Time Fees'] = display_df['One-Time Fees'].apply(lambda x: f"${x:,.2f}")
    display_df['7-Year TCO'] = display_df['7-Year TCO'].apply(lambda x: f"${x:,.2f}")
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # Store results for download
    st.session_state['comparison_results'] = results_df
    st.session_state['comparison_client'] = client_name


def main():
    """Main dashboard application."""

    # Header
    st.title("📊 TCO Automation Dashboard")
    st.markdown("*Manage client proposals and run vendor comparisons*")

    # Sidebar - Client Browser
    st.sidebar.header("🏦 Client Browser")

    # Load clients
    clients = get_clients_from_extractions()

    if not clients:
        st.sidebar.warning("No extraction files found in 'Extracted JSON' folder")
        st.info("Upload vendor proposals and run extractions to get started.")
        return

    # Client selector
    client_names = sorted(clients.keys())
    selected_client = st.sidebar.selectbox(
        "Select Client",
        client_names,
        index=0
    )

    if selected_client:
        client_data = clients[selected_client]
        available_vendors = list(client_data.keys())

        st.sidebar.markdown(f"**Available Vendors:** {len(available_vendors)}")
        for vendor in available_vendors:
            file_count = len(client_data[vendor])
            st.sidebar.markdown(f"- {vendor} ({file_count} file{'s' if file_count > 1 else ''})")

        st.sidebar.divider()

        # Vendor selector for comparison
        st.sidebar.subheader("🔄 Run Comparison")
        selected_vendors = st.sidebar.multiselect(
            "Select vendors to compare",
            available_vendors,
            default=available_vendors[:2] if len(available_vendors) >= 2 else available_vendors
        )

        if st.sidebar.button("Run Comparison", type="primary", disabled=len(selected_vendors) < 2):
            run_comparison(selected_client, selected_vendors, client_data)

        if len(selected_vendors) < 2:
            st.sidebar.caption("Select at least 2 vendors to compare")

    # Main content area
    st.header(f"Client: {selected_client}")

    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📋 Proposals", "📊 Comparison", "⬇️ Download"])

    with tab1:
        st.subheader("Vendor Proposals")

        if selected_client and selected_client in clients:
            client_data = clients[selected_client]

            # Create columns for each vendor
            vendor_tabs = st.tabs(list(client_data.keys()))

            for i, vendor in enumerate(client_data.keys()):
                with vendor_tabs[i]:
                    for file_info in client_data[vendor]:
                        display_extraction_summary(file_info['data'])

    with tab2:
        st.subheader("Vendor Comparison")

        if 'comparison_results' in st.session_state:
            results_df = st.session_state['comparison_results']
            client_name = st.session_state.get('comparison_client', 'Unknown')

            st.markdown(f"**Last comparison:** {client_name}")

            # Bar chart of TCO
            st.bar_chart(results_df.set_index('Vendor')['7-Year TCO'])

            # Detailed table
            display_df = results_df.copy()
            display_df['Monthly Fees'] = display_df['Monthly Fees'].apply(lambda x: f"${x:,.2f}")
            display_df['One-Time Fees'] = display_df['One-Time Fees'].apply(lambda x: f"${x:,.2f}")
            display_df['7-Year TCO'] = display_df['7-Year TCO'].apply(lambda x: f"${x:,.2f}")
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.info("Run a comparison from the sidebar to see results here.")

    with tab3:
        st.subheader("Download Results")

        if 'comparison_results' in st.session_state:
            results_df = st.session_state['comparison_results']
            client_name = st.session_state.get('comparison_client', 'Unknown')

            # CSV download
            csv = results_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Comparison (CSV)",
                data=csv,
                file_name=f"{client_name.replace(' ', '_')}_comparison_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

            # JSON download
            json_data = results_df.to_json(orient='records', indent=2)
            st.download_button(
                label="📥 Download Comparison (JSON)",
                data=json_data,
                file_name=f"{client_name.replace(' ', '_')}_comparison_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
        else:
            st.info("Run a comparison first to enable downloads.")

        st.divider()

        # List existing TCO output files
        st.subheader("Existing TCO Files")
        if TCO_OUTPUT_DIR.exists():
            tco_files = list(TCO_OUTPUT_DIR.glob("*.xlsx"))
            if tco_files:
                for f in tco_files:
                    with open(f, 'rb') as file:
                        st.download_button(
                            label=f"📥 {f.name}",
                            data=file.read(),
                            file_name=f.name,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f.name
                        )
            else:
                st.info("No TCO Excel files found in 'TCO Output' folder.")
        else:
            st.info("TCO Output folder not found.")


if __name__ == "__main__":
    main()
