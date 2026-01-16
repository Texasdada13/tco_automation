"""
TCO Automation Dashboard - Flask Application
Arriba Advisors branded client-ready dashboard
"""

import json
import os
from datetime import datetime
from functools import wraps
from pathlib import Path

from flask import Flask, render_template, request, session, redirect, url_for, jsonify, g

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Configuration
BASE_DIR = Path(__file__).parent.parent
EXTRACTED_JSON_DIR = BASE_DIR / "Extracted JSON"
TCO_OUTPUT_DIR = BASE_DIR / "TCO Output"

# User roles
ROLES = {
    'analyst': {
        'name': 'Analyst',
        'description': 'Extract proposals, review matches, run comparisons',
        'permissions': ['view_all', 'edit', 'review', 'compare', 'export']
    },
    'manager': {
        'name': 'Manager',
        'description': 'Review comparisons, approve/reject, see all clients',
        'permissions': ['view_all', 'approve', 'compare', 'export']
    },
    'executive': {
        'name': 'Executive',
        'description': 'High-level summaries, KPIs, no line-item details',
        'permissions': ['view_summary', 'export']
    }
}


def get_current_role():
    """Get current user role from session."""
    return session.get('role', 'analyst')


def has_permission(permission):
    """Check if current role has a permission."""
    role = get_current_role()
    return permission in ROLES.get(role, {}).get('permissions', [])


@app.before_request
def before_request():
    """Set up request context."""
    g.role = get_current_role()
    g.role_info = ROLES.get(g.role, ROLES['analyst'])
    g.has_permission = has_permission


@app.context_processor
def inject_globals():
    """Inject global variables into templates."""
    return {
        'current_role': get_current_role(),
        'role_info': ROLES.get(get_current_role(), ROLES['analyst']),
        'roles': ROLES,
        'has_permission': has_permission
    }


# =============================================================================
# Data Loading Functions
# =============================================================================

def get_clients_data():
    """Load all client data from extraction files."""
    clients = {}

    if not EXTRACTED_JSON_DIR.exists():
        return clients

    for file in EXTRACTED_JSON_DIR.glob("*_extraction_ai.json"):
        try:
            with open(file, 'r') as f:
                data = json.load(f)

            # Extract client name
            client_name = data.get('client')
            if not client_name or client_name == 'Unknown':
                parts = file.stem.replace('_extraction_ai', '').split('_')
                vendors_list = ['fis', 'jh', 'csi', 'fiserv', 'finastra', 'jack_henry']
                found_vendor = False
                for v in vendors_list:
                    if len(parts) > 1 and (v in parts[-1].lower() or v in parts[-2].lower()):
                        client_name = '_'.join(parts[:-1]).replace('_', ' ').title()
                        found_vendor = True
                        break
                if not found_vendor:
                    client_name = file.stem.replace('_extraction_ai', '').replace('_', ' ').title()

            if not client_name:
                client_name = f"Unknown ({file.stem})"

            # Get vendor
            vendor_raw = data.get('vendor', 'Unknown')
            vendor = vendor_raw.upper()
            for v in ['FIS', 'JACK_HENRY', 'JH', 'CSI', 'FISERV', 'FINASTRA']:
                if v in vendor:
                    vendor = v.replace('JH', 'JACK_HENRY')
                    break

            # Add to clients dict
            if client_name not in clients:
                clients[client_name] = {
                    'name': client_name,
                    'vendors': {},
                    'total_proposals': 0
                }

            if vendor not in clients[client_name]['vendors']:
                clients[client_name]['vendors'][vendor] = []

            # Calculate totals
            line_items = data.get('line_items', [])
            total_monthly = sum(item.get('monthly_fee', 0) or 0 for item in line_items)
            total_onetime = sum(item.get('one_time_fee', 0) or 0 for item in line_items)
            contract_term = data.get('contract_term', 7)
            tco_7yr = (total_monthly * 12 * contract_term) + total_onetime

            clients[client_name]['vendors'][vendor].append({
                'file': str(file),
                'filename': file.name,
                'data': data,
                'total_monthly': total_monthly,
                'total_onetime': total_onetime,
                'tco_7yr': tco_7yr,
                'line_items_count': len(line_items),
                'contract_term': contract_term,
                'document_date': data.get('document_date', 'N/A')
            })
            clients[client_name]['total_proposals'] += 1

        except Exception as e:
            app.logger.warning(f"Could not load {file.name}: {e}")

    return clients


def get_dashboard_stats(clients_data):
    """Calculate dashboard statistics."""
    total_clients = len(clients_data)
    total_proposals = sum(c['total_proposals'] for c in clients_data.values())

    # Calculate total TCO across all proposals
    total_tco = 0
    vendors_seen = set()
    for client in clients_data.values():
        for vendor, proposals in client['vendors'].items():
            vendors_seen.add(vendor)
            for p in proposals:
                total_tco += p['tco_7yr']

    # Find lowest TCO vendor per client for savings calculation
    potential_savings = 0
    for client in clients_data.values():
        if len(client['vendors']) >= 2:
            vendor_tcos = []
            for vendor, proposals in client['vendors'].items():
                # Use first proposal per vendor
                if proposals:
                    vendor_tcos.append(proposals[0]['tco_7yr'])
            if len(vendor_tcos) >= 2:
                vendor_tcos.sort()
                # Savings = difference between highest and lowest
                potential_savings += vendor_tcos[-1] - vendor_tcos[0]

    return {
        'total_clients': total_clients,
        'total_proposals': total_proposals,
        'total_vendors': len(vendors_seen),
        'total_tco': total_tco,
        'potential_savings': potential_savings,
        'avg_tco_per_client': total_tco / total_clients if total_clients > 0 else 0
    }


# =============================================================================
# Routes
# =============================================================================

@app.route('/')
def index():
    """Landing page - redirect to dashboard."""
    return redirect(url_for('dashboard'))


@app.route('/dashboard')
def dashboard():
    """Main dashboard with KPIs."""
    clients_data = get_clients_data()
    stats = get_dashboard_stats(clients_data)

    # Get recent activity (most recent files)
    recent_files = []
    if EXTRACTED_JSON_DIR.exists():
        files = list(EXTRACTED_JSON_DIR.glob("*_extraction_ai.json"))
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        for f in files[:5]:
            recent_files.append({
                'name': f.stem.replace('_extraction_ai', '').replace('_', ' ').title(),
                'date': datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
            })

    # Vendor distribution for chart
    vendor_counts = {}
    for client in clients_data.values():
        for vendor in client['vendors'].keys():
            vendor_counts[vendor] = vendor_counts.get(vendor, 0) + 1

    return render_template('dashboard.html',
                         stats=stats,
                         recent_files=recent_files,
                         vendor_counts=vendor_counts,
                         clients_data=clients_data)


@app.route('/clients')
def clients():
    """Client browser page."""
    clients_data = get_clients_data()

    # Sort clients by name
    sorted_clients = sorted(clients_data.values(), key=lambda x: x['name'])

    return render_template('clients.html', clients=sorted_clients)


@app.route('/clients/<client_name>')
def client_detail(client_name):
    """Client detail page with tabs."""
    clients_data = get_clients_data()

    # Find client (case-insensitive match)
    client = None
    for name, data in clients_data.items():
        if name.lower() == client_name.lower():
            client = data
            break

    if not client:
        return render_template('404.html', message=f"Client '{client_name}' not found"), 404

    return render_template('client_detail.html', client=client)


@app.route('/compare')
def compare():
    """Comparison page."""
    clients_data = get_clients_data()
    return render_template('compare.html', clients=clients_data)


@app.route('/compare/<client_name>')
def compare_client(client_name):
    """Run comparison for a specific client."""
    clients_data = get_clients_data()

    client = None
    for name, data in clients_data.items():
        if name.lower() == client_name.lower():
            client = data
            break

    if not client:
        return render_template('404.html', message=f"Client '{client_name}' not found"), 404

    # Calculate comparison data
    comparison = []
    for vendor, proposals in client['vendors'].items():
        if proposals:
            p = proposals[0]  # Use first proposal per vendor
            comparison.append({
                'vendor': vendor,
                'monthly_fees': p['total_monthly'],
                'onetime_fees': p['total_onetime'],
                'tco_7yr': p['tco_7yr'],
                'line_items': p['line_items_count'],
                'contract_term': p['contract_term']
            })

    # Sort by TCO
    comparison.sort(key=lambda x: x['tco_7yr'])

    # Add rank and delta
    if comparison:
        lowest_tco = comparison[0]['tco_7yr']
        for i, c in enumerate(comparison):
            c['rank'] = i + 1
            c['delta'] = c['tco_7yr'] - lowest_tco
            c['delta_pct'] = (c['delta'] / lowest_tco * 100) if lowest_tco > 0 else 0

    return render_template('comparison_result.html', client=client, comparison=comparison)


@app.route('/review')
def review():
    """Product match review queue (Analyst only)."""
    if not has_permission('review'):
        return render_template('403.html', message="Access denied"), 403

    # Load review queue
    review_queue_path = BASE_DIR / "ontology" / "review_queue.json"
    queue_items = []

    if review_queue_path.exists():
        try:
            with open(review_queue_path, 'r') as f:
                queue_data = json.load(f)
                queue_items = queue_data.get('items', [])[:50]  # Limit to 50
        except Exception as e:
            app.logger.warning(f"Could not load review queue: {e}")

    return render_template('review.html', queue_items=queue_items)


@app.route('/reports')
def reports():
    """Export center."""
    # List existing TCO output files
    tco_files = []
    if TCO_OUTPUT_DIR.exists():
        for f in TCO_OUTPUT_DIR.glob("*.xlsx"):
            tco_files.append({
                'name': f.name,
                'path': str(f),
                'size': f.stat().st_size,
                'date': datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
            })
        tco_files.sort(key=lambda x: x['date'], reverse=True)

    return render_template('reports.html', tco_files=tco_files)


@app.route('/ai-assistant')
def ai_assistant():
    """AI Q&A interface."""
    return render_template('ai_assistant.html')


@app.route('/api/ai-query', methods=['POST'])
def api_ai_query():
    """Handle AI Q&A queries."""
    try:
        import anthropic

        data = request.get_json()
        query = data.get('query', '')

        if not query:
            return jsonify({'error': 'No query provided'}), 400

        # Load client data for context
        clients_data = get_clients_data()
        stats = get_dashboard_stats(clients_data)

        # Build context
        context = f"""You are an AI assistant for the TCO Automation Dashboard at Arriba Advisors.

Current data summary:
- Total clients: {stats['total_clients']}
- Total proposals: {stats['total_proposals']}
- Total 7-year TCO across all proposals: ${stats['total_tco']:,.2f}
- Potential savings identified: ${stats['potential_savings']:,.2f}

Available clients and their vendors:
"""
        for client in list(clients_data.values())[:10]:
            vendors = list(client['vendors'].keys())
            context += f"- {client['name']}: {', '.join(vendors)}\n"

        context += "\nAnswer the user's question based on this data. Be concise and helpful."

        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[
                {"role": "user", "content": f"{context}\n\nUser question: {query}"}
            ]
        )

        return jsonify({'response': response.content[0].text})

    except Exception as e:
        app.logger.error(f"AI query error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/switch-role', methods=['POST'])
def switch_role():
    """Switch user role."""
    data = request.get_json()
    role = data.get('role', 'analyst')

    if role in ROLES:
        session['role'] = role
        return jsonify({'success': True, 'role': role})

    return jsonify({'error': 'Invalid role'}), 400


@app.route('/api/export/<client_name>')
def export_client(client_name):
    """Export client data as JSON."""
    clients_data = get_clients_data()

    client = None
    for name, data in clients_data.items():
        if name.lower() == client_name.lower():
            client = data
            break

    if not client:
        return jsonify({'error': 'Client not found'}), 404

    # Prepare export data (remove file paths)
    export_data = {
        'client_name': client['name'],
        'exported_at': datetime.now().isoformat(),
        'vendors': {}
    }

    for vendor, proposals in client['vendors'].items():
        export_data['vendors'][vendor] = []
        for p in proposals:
            export_data['vendors'][vendor].append({
                'total_monthly': p['total_monthly'],
                'total_onetime': p['total_onetime'],
                'tco_7yr': p['tco_7yr'],
                'line_items_count': p['line_items_count'],
                'contract_term': p['contract_term']
            })

    return jsonify(export_data)


# =============================================================================
# Error Handlers
# =============================================================================

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


# =============================================================================
# Run Application
# =============================================================================

if __name__ == '__main__':
    app.run(debug=True, port=5847)
