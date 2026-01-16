"""
TCO Automation Dashboard - Flask Application
Arriba Advisors branded client-ready dashboard
"""

import json
import os
from datetime import datetime
from functools import wraps
from pathlib import Path
from uuid import uuid4

from flask import Flask, render_template, request, session, redirect, url_for, jsonify, g, Response, send_file

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload

# Import AI Assistant
from ai_assistant import TCOAIAssistant, create_assistant

# Import Bulk Upload Manager
from bulk_upload import get_upload_manager, BulkUploadManager

# Import Report Generator (lazy load to handle missing reportlab)
report_generator = None
def get_report_generator():
    global report_generator
    if report_generator is None:
        try:
            from report_generator import TCOReportGenerator
            report_generator = TCOReportGenerator()
        except ImportError:
            return None
    return report_generator

# Store conversation contexts per session (in production, use Redis or database)
conversation_sessions = {}

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


def get_or_create_session_id():
    """Get or create a unique session ID for conversation tracking."""
    if 'conversation_id' not in session:
        session['conversation_id'] = str(uuid4())
    return session['conversation_id']


def get_ai_assistant():
    """Get or create AI assistant for current session."""
    session_id = get_or_create_session_id()
    role = get_current_role()

    # Create new assistant if not exists or role changed
    if session_id not in conversation_sessions:
        clients_data = get_clients_data()
        conversation_sessions[session_id] = {
            'assistant': create_assistant(clients_data, role),
            'role': role,
            'created_at': datetime.now()
        }
    elif conversation_sessions[session_id]['role'] != role:
        # Role changed, update assistant
        clients_data = get_clients_data()
        conversation_sessions[session_id]['assistant'].user_role = role

    return conversation_sessions[session_id]['assistant']


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

    # Get AI insights for dashboard
    ai_insights = []
    try:
        assistant = get_ai_assistant()
        ai_insights = assistant.get_quick_insights()
    except Exception as e:
        app.logger.warning(f"Could not get AI insights: {e}")

    return render_template('dashboard.html',
                         stats=stats,
                         recent_files=recent_files,
                         vendor_counts=vendor_counts,
                         clients_data=clients_data,
                         ai_insights=ai_insights)


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
    # Get AI insights for sidebar
    ai_insights = []
    try:
        assistant = get_ai_assistant()
        ai_insights = assistant.get_quick_insights()
    except Exception as e:
        app.logger.warning(f"Could not get AI insights: {e}")

    # Get client list for context
    clients_data = get_clients_data()
    client_names = list(clients_data.keys())

    return render_template('ai_assistant.html',
                         ai_insights=ai_insights,
                         client_names=client_names)


# =============================================================================
# AI Assistant API Endpoints
# =============================================================================

@app.route('/api/ai-query', methods=['POST'])
def api_ai_query():
    """Handle AI Q&A queries with comprehensive analysis."""
    try:
        import anthropic

        data = request.get_json()
        query = data.get('query', '')

        if not query:
            return jsonify({'error': 'No query provided'}), 400

        # Get AI assistant with conversation context
        assistant = get_ai_assistant()

        # Process query to get intent and context data
        query_result = assistant.process_query(query)

        # Call Claude with the enriched prompt
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[
                {"role": "user", "content": query_result['prompt']}
            ]
        )

        response_text = response.content[0].text

        # Store response in conversation context
        assistant.add_response(response_text)

        return jsonify({
            'response': response_text,
            'intent': query_result['intent']['type'],
            'suggested_followups': query_result['suggested_followups'],
            'entities': query_result['intent']['entities']
        })

    except ImportError:
        return jsonify({
            'error': 'Anthropic library not installed. Please run: pip install anthropic'
        }), 500
    except Exception as e:
        app.logger.error(f"AI query error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai-insights', methods=['GET'])
def api_ai_insights():
    """Get AI-generated insights for the dashboard."""
    try:
        assistant = get_ai_assistant()
        insights = assistant.get_quick_insights()
        return jsonify({'insights': insights})
    except Exception as e:
        app.logger.error(f"AI insights error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai-analyze-client/<client_name>', methods=['GET'])
def api_ai_analyze_client(client_name):
    """Get AI analysis for a specific client."""
    try:
        assistant = get_ai_assistant()

        # Get client details
        client_details = assistant.tools.get_client_details(client_name)
        if 'error' in client_details:
            return jsonify(client_details), 404

        # Get comparison if multiple vendors
        comparison = None
        if len(client_details.get('vendors', {})) >= 2:
            comparison = assistant.tools.compare_vendors_for_client(client_name)

        # Get category breakdown
        category_breakdown = assistant.tools.get_category_breakdown(client=client_name)

        return jsonify({
            'client': client_details,
            'comparison': comparison,
            'categories': category_breakdown
        })
    except Exception as e:
        app.logger.error(f"AI client analysis error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai-search', methods=['POST'])
def api_ai_search():
    """Search line items with filters."""
    try:
        data = request.get_json()
        assistant = get_ai_assistant()

        results = assistant.tools.search_line_items(
            query=data.get('query'),
            client=data.get('client'),
            vendor=data.get('vendor'),
            category=data.get('category'),
            min_monthly=data.get('min_monthly'),
            max_monthly=data.get('max_monthly'),
            limit=data.get('limit', 20)
        )

        return jsonify({'results': results, 'count': len(results)})
    except Exception as e:
        app.logger.error(f"AI search error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai-compare-vendors', methods=['GET'])
def api_ai_compare_vendors():
    """Get overall vendor comparison."""
    try:
        assistant = get_ai_assistant()
        comparison = assistant.tools.compare_vendors_overall()
        return jsonify(comparison)
    except Exception as e:
        app.logger.error(f"AI vendor comparison error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai-savings', methods=['GET'])
def api_ai_savings():
    """Get savings opportunities."""
    try:
        assistant = get_ai_assistant()
        opportunities = assistant.tools.get_savings_opportunities()
        return jsonify({'opportunities': opportunities})
    except Exception as e:
        app.logger.error(f"AI savings error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai-anomalies', methods=['GET'])
def api_ai_anomalies():
    """Get cost anomalies."""
    try:
        assistant = get_ai_assistant()
        anomalies = assistant.tools.find_anomalies()
        return jsonify({'anomalies': anomalies})
    except Exception as e:
        app.logger.error(f"AI anomalies error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai-clear-conversation', methods=['POST'])
def api_ai_clear_conversation():
    """Clear conversation history for current session."""
    try:
        session_id = get_or_create_session_id()
        if session_id in conversation_sessions:
            del conversation_sessions[session_id]
        return jsonify({'success': True, 'message': 'Conversation cleared'})
    except Exception as e:
        app.logger.error(f"Clear conversation error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/switch-role', methods=['POST'])
def switch_role():
    """Switch user role."""
    data = request.get_json()
    role = data.get('role', 'analyst')

    if role in ROLES:
        session['role'] = role
        # Clear conversation when role changes for fresh context
        session_id = get_or_create_session_id()
        if session_id in conversation_sessions:
            del conversation_sessions[session_id]
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
# Negotiation API Endpoints
# =============================================================================

@app.route('/api/negotiation/<client_name>')
def api_negotiation_insights(client_name):
    """Get negotiation insights for a client."""
    try:
        assistant = get_ai_assistant()
        insights = assistant.tools.get_negotiation_insights(client_name)
        return jsonify(insights)
    except Exception as e:
        app.logger.error(f"Negotiation insights error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/negotiation/<client_name>/playbook')
def api_negotiation_playbook(client_name):
    """Get full negotiation playbook for a client."""
    try:
        assistant = get_ai_assistant()
        playbook = assistant.tools.get_negotiation_playbook(client_name)
        return jsonify(playbook)
    except Exception as e:
        app.logger.error(f"Negotiation playbook error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/benchmark/<client_name>')
def api_benchmark_comparison(client_name):
    """Get benchmark comparison for a client."""
    try:
        vendor = request.args.get('vendor')
        assistant = get_ai_assistant()
        benchmark = assistant.tools.get_benchmark_comparison(client_name, vendor)
        return jsonify(benchmark)
    except Exception as e:
        app.logger.error(f"Benchmark comparison error: {e}")
        return jsonify({'error': str(e)}), 500


# =============================================================================
# PDF Report Generation
# =============================================================================

@app.route('/api/generate-report/<client_name>')
def api_generate_report(client_name):
    """Generate PDF report for a client."""
    try:
        generator = get_report_generator()
        if not generator:
            return jsonify({'error': 'PDF generation not available. Install reportlab: pip install reportlab'}), 500

        clients_data = get_clients_data()

        # Find client
        client = None
        actual_name = None
        for name, data in clients_data.items():
            if name.lower() == client_name.lower():
                client = data
                actual_name = name
                break

        if not client:
            return jsonify({'error': f"Client '{client_name}' not found"}), 404

        # Get AI insights
        assistant = get_ai_assistant()
        comparison = None
        if len(client.get('vendors', {})) >= 2:
            comparison = assistant.tools.compare_vendors_for_client(actual_name)

        ai_insights = assistant.get_quick_insights()

        # Generate PDF
        pdf_bytes = generator.generate_executive_summary(
            client_name=actual_name,
            client_data=client,
            comparison_data=comparison,
            ai_insights=ai_insights
        )

        # Create filename
        safe_name = actual_name.lower().replace(' ', '_')
        filename = f"{safe_name}_tco_report_{datetime.now().strftime('%Y%m%d')}.pdf"

        return Response(
            pdf_bytes,
            mimetype='application/pdf',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )

    except Exception as e:
        app.logger.error(f"Report generation error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-comparison-report', methods=['POST'])
def api_generate_comparison_report():
    """Generate comparison report for multiple clients."""
    try:
        generator = get_report_generator()
        if not generator:
            return jsonify({'error': 'PDF generation not available. Install reportlab: pip install reportlab'}), 500

        data = request.get_json()
        selected_clients = data.get('clients', [])

        if not selected_clients:
            return jsonify({'error': 'No clients selected'}), 400

        clients_data = get_clients_data()

        # Generate PDF
        pdf_bytes = generator.generate_comparison_report(
            clients_data=clients_data,
            selected_clients=selected_clients
        )

        filename = f"multi_client_comparison_{datetime.now().strftime('%Y%m%d')}.pdf"

        return Response(
            pdf_bytes,
            mimetype='application/pdf',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )

    except Exception as e:
        app.logger.error(f"Comparison report error: {e}")
        return jsonify({'error': str(e)}), 500


# =============================================================================
# Bulk Upload Routes
# =============================================================================

@app.route('/upload')
def upload_page():
    """Bulk upload page."""
    if not has_permission('edit'):
        return render_template('403.html', message="Access denied"), 403

    manager = get_upload_manager()
    jobs = manager.get_all_jobs()

    return render_template('upload.html', jobs=jobs)


@app.route('/api/upload/create-job', methods=['POST'])
def api_create_upload_job():
    """Create a new upload job."""
    try:
        manager = get_upload_manager()
        job = manager.create_job()
        return jsonify({'job_id': job.id, 'status': 'created'})
    except Exception as e:
        app.logger.error(f"Create job error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload/<job_id>/add-file', methods=['POST'])
def api_add_file_to_job(job_id):
    """Add a file to an upload job."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if not file.filename:
            return jsonify({'error': 'No file selected'}), 400

        manager = get_upload_manager()
        upload_file = manager.add_file_to_job(
            job_id=job_id,
            file_data=file.read(),
            filename=file.filename
        )

        if not upload_file:
            return jsonify({'error': 'Invalid file or job not found'}), 400

        return jsonify({
            'file_id': upload_file.id,
            'filename': upload_file.original_filename,
            'vendor': upload_file.vendor,
            'status': upload_file.status.value
        })

    except Exception as e:
        app.logger.error(f"Add file error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload/<job_id>/start', methods=['POST'])
def api_start_upload_job(job_id):
    """Start processing an upload job."""
    try:
        manager = get_upload_manager()
        success = manager.start_processing(job_id)

        if not success:
            return jsonify({'error': 'Could not start job'}), 400

        return jsonify({'status': 'started', 'job_id': job_id})

    except Exception as e:
        app.logger.error(f"Start job error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload/<job_id>/status')
def api_upload_job_status(job_id):
    """Get status of an upload job."""
    try:
        manager = get_upload_manager()
        status = manager.get_job_status(job_id)

        if not status:
            return jsonify({'error': 'Job not found'}), 404

        return jsonify(status)

    except Exception as e:
        app.logger.error(f"Job status error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload/<job_id>/cancel', methods=['POST'])
def api_cancel_upload_job(job_id):
    """Cancel an upload job."""
    try:
        manager = get_upload_manager()
        success = manager.cancel_job(job_id)

        if not success:
            return jsonify({'error': 'Could not cancel job'}), 400

        return jsonify({'status': 'cancelled', 'job_id': job_id})

    except Exception as e:
        app.logger.error(f"Cancel job error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload/<job_id>/cleanup', methods=['POST'])
def api_cleanup_upload_job(job_id):
    """Clean up a completed job."""
    try:
        manager = get_upload_manager()
        success = manager.cleanup_job(job_id)

        if not success:
            return jsonify({'error': 'Could not cleanup job'}), 400

        return jsonify({'status': 'cleaned', 'job_id': job_id})

    except Exception as e:
        app.logger.error(f"Cleanup job error: {e}")
        return jsonify({'error': str(e)}), 500


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
