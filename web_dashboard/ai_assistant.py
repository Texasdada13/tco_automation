"""
TCO Automation - Comprehensive AI Assistant
A robust AI-powered assistant for TCO analysis with deep data access,
analytical capabilities, and role-aware responses.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, field

# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class ConversationMessage:
    """A single message in the conversation."""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)


@dataclass
class ConversationContext:
    """Maintains conversation state and memory."""
    messages: list = field(default_factory=list)
    current_client: Optional[str] = None
    current_vendor: Optional[str] = None
    last_query_type: Optional[str] = None
    session_insights: list = field(default_factory=list)

    def add_message(self, role: str, content: str, metadata: dict = None):
        self.messages.append(ConversationMessage(
            role=role,
            content=content,
            metadata=metadata or {}
        ))
        # Keep last 20 messages for context
        if len(self.messages) > 20:
            self.messages = self.messages[-20:]

    def get_history_for_prompt(self, max_messages: int = 10) -> str:
        """Format recent conversation history for the AI prompt."""
        recent = self.messages[-max_messages:]
        history = []
        for msg in recent:
            prefix = "User" if msg.role == "user" else "Assistant"
            history.append(f"{prefix}: {msg.content}")
        return "\n".join(history)

    def to_dict(self) -> dict:
        return {
            'messages': [{'role': m.role, 'content': m.content} for m in self.messages],
            'current_client': self.current_client,
            'current_vendor': self.current_vendor,
            'session_insights': self.session_insights
        }


# =============================================================================
# AI Tools - Functions the AI can call
# =============================================================================

class TCOAnalysisTools:
    """Tools for deep TCO data analysis."""

    def __init__(self, clients_data: dict):
        self.clients_data = clients_data
        self._build_indexes()

    def _build_indexes(self):
        """Build searchable indexes for fast queries."""
        self.all_line_items = []
        self.categories = {}
        self.vendors_data = {}
        self.client_summaries = {}

        for client_name, client in self.clients_data.items():
            client_total_tco = 0
            client_vendors = []

            for vendor, proposals in client.get('vendors', {}).items():
                if vendor not in self.vendors_data:
                    self.vendors_data[vendor] = {
                        'clients': [],
                        'total_tco': 0,
                        'total_monthly': 0,
                        'proposal_count': 0,
                        'all_line_items': []
                    }

                self.vendors_data[vendor]['clients'].append(client_name)
                client_vendors.append(vendor)

                for proposal in proposals:
                    self.vendors_data[vendor]['total_tco'] += proposal.get('tco_7yr', 0)
                    self.vendors_data[vendor]['total_monthly'] += proposal.get('total_monthly', 0)
                    self.vendors_data[vendor]['proposal_count'] += 1
                    client_total_tco += proposal.get('tco_7yr', 0)

                    # Index all line items
                    for item in proposal.get('data', {}).get('line_items', []):
                        item_data = {
                            'client': client_name,
                            'vendor': vendor,
                            'product_name': item.get('product_name', 'Unknown'),
                            'category': item.get('category', 'Uncategorized'),
                            'monthly_fee': item.get('monthly_fee', 0) or 0,
                            'one_time_fee': item.get('one_time_fee', 0) or 0,
                            'quantity': item.get('quantity', 1) or 1,
                            'unit_price': item.get('unit_price', 0) or 0
                        }
                        self.all_line_items.append(item_data)
                        self.vendors_data[vendor]['all_line_items'].append(item_data)

                        # Index by category
                        cat = item_data['category']
                        if cat not in self.categories:
                            self.categories[cat] = []
                        self.categories[cat].append(item_data)

            self.client_summaries[client_name] = {
                'total_tco': client_total_tco,
                'vendors': client_vendors,
                'proposal_count': client.get('total_proposals', 0)
            }

    # -------------------------------------------------------------------------
    # Search Tools
    # -------------------------------------------------------------------------

    def search_line_items(self,
                          query: str = None,
                          client: str = None,
                          vendor: str = None,
                          category: str = None,
                          min_monthly: float = None,
                          max_monthly: float = None,
                          limit: int = 20) -> list:
        """Search line items with various filters."""
        results = self.all_line_items.copy()

        if client:
            results = [i for i in results if client.lower() in i['client'].lower()]

        if vendor:
            results = [i for i in results if vendor.lower() in i['vendor'].lower()]

        if category:
            results = [i for i in results if category.lower() in i['category'].lower()]

        if query:
            results = [i for i in results if query.lower() in i['product_name'].lower()]

        if min_monthly is not None:
            results = [i for i in results if i['monthly_fee'] >= min_monthly]

        if max_monthly is not None:
            results = [i for i in results if i['monthly_fee'] <= max_monthly]

        # Sort by monthly fee descending
        results.sort(key=lambda x: x['monthly_fee'], reverse=True)

        return results[:limit]

    def get_client_details(self, client_name: str) -> dict:
        """Get comprehensive details for a client."""
        # Find client (case-insensitive)
        client = None
        actual_name = None
        for name, data in self.clients_data.items():
            if client_name.lower() in name.lower():
                client = data
                actual_name = name
                break

        if not client:
            return {'error': f"Client '{client_name}' not found"}

        result = {
            'name': actual_name,
            'vendors': {},
            'total_proposals': client.get('total_proposals', 0),
            'comparison_ready': len(client.get('vendors', {})) >= 2
        }

        for vendor, proposals in client.get('vendors', {}).items():
            if proposals:
                p = proposals[0]
                result['vendors'][vendor] = {
                    'monthly_fees': p.get('total_monthly', 0),
                    'onetime_fees': p.get('total_onetime', 0),
                    'tco_7yr': p.get('tco_7yr', 0),
                    'line_items_count': p.get('line_items_count', 0),
                    'contract_term': p.get('contract_term', 7),
                    'top_costs': self._get_top_costs(actual_name, vendor, 5)
                }

        return result

    def _get_top_costs(self, client: str, vendor: str, limit: int = 5) -> list:
        """Get top cost line items for a client-vendor combination."""
        items = [i for i in self.all_line_items
                 if i['client'] == client and i['vendor'] == vendor]
        items.sort(key=lambda x: x['monthly_fee'], reverse=True)
        return items[:limit]

    # -------------------------------------------------------------------------
    # Comparison Tools
    # -------------------------------------------------------------------------

    def compare_vendors_for_client(self, client_name: str) -> dict:
        """Generate detailed vendor comparison for a client."""
        client_details = self.get_client_details(client_name)

        if 'error' in client_details:
            return client_details

        if len(client_details['vendors']) < 2:
            return {
                'error': f"Client {client_details['name']} only has {len(client_details['vendors'])} vendor(s). Need at least 2 for comparison."
            }

        comparison = {
            'client': client_details['name'],
            'vendors': client_details['vendors'],
            'analysis': {}
        }

        # Sort vendors by TCO
        sorted_vendors = sorted(
            client_details['vendors'].items(),
            key=lambda x: x[1]['tco_7yr']
        )

        lowest = sorted_vendors[0]
        highest = sorted_vendors[-1]

        comparison['analysis'] = {
            'lowest_tco_vendor': lowest[0],
            'lowest_tco_amount': lowest[1]['tco_7yr'],
            'highest_tco_vendor': highest[0],
            'highest_tco_amount': highest[1]['tco_7yr'],
            'potential_savings': highest[1]['tco_7yr'] - lowest[1]['tco_7yr'],
            'savings_percentage': ((highest[1]['tco_7yr'] - lowest[1]['tco_7yr']) / highest[1]['tco_7yr'] * 100) if highest[1]['tco_7yr'] > 0 else 0,
            'recommendation': f"{lowest[0]} offers the lowest 7-year TCO, saving ${highest[1]['tco_7yr'] - lowest[1]['tco_7yr']:,.2f} compared to {highest[0]}"
        }

        return comparison

    def compare_vendors_overall(self) -> dict:
        """Compare vendors across all clients."""
        if not self.vendors_data:
            return {'error': 'No vendor data available'}

        vendor_stats = []
        for vendor, data in self.vendors_data.items():
            avg_tco = data['total_tco'] / data['proposal_count'] if data['proposal_count'] > 0 else 0
            vendor_stats.append({
                'vendor': vendor,
                'client_count': len(set(data['clients'])),
                'proposal_count': data['proposal_count'],
                'total_tco': data['total_tco'],
                'avg_tco': avg_tco,
                'avg_monthly': data['total_monthly'] / data['proposal_count'] if data['proposal_count'] > 0 else 0
            })

        vendor_stats.sort(key=lambda x: x['avg_tco'])

        return {
            'vendors': vendor_stats,
            'lowest_avg_tco': vendor_stats[0] if vendor_stats else None,
            'highest_avg_tco': vendor_stats[-1] if vendor_stats else None
        }

    # -------------------------------------------------------------------------
    # Analytics Tools
    # -------------------------------------------------------------------------

    def get_category_breakdown(self, client: str = None, vendor: str = None) -> dict:
        """Analyze costs by category."""
        items = self.all_line_items

        if client:
            items = [i for i in items if client.lower() in i['client'].lower()]
        if vendor:
            items = [i for i in items if vendor.lower() in i['vendor'].lower()]

        breakdown = {}
        for item in items:
            cat = item['category']
            if cat not in breakdown:
                breakdown[cat] = {
                    'total_monthly': 0,
                    'total_onetime': 0,
                    'item_count': 0,
                    'items': []
                }
            breakdown[cat]['total_monthly'] += item['monthly_fee']
            breakdown[cat]['total_onetime'] += item['one_time_fee']
            breakdown[cat]['item_count'] += 1
            breakdown[cat]['items'].append(item['product_name'])

        # Sort by total monthly cost
        sorted_breakdown = sorted(
            breakdown.items(),
            key=lambda x: x[1]['total_monthly'],
            reverse=True
        )

        return {
            'categories': dict(sorted_breakdown),
            'total_categories': len(breakdown),
            'top_category': sorted_breakdown[0] if sorted_breakdown else None
        }

    def find_anomalies(self, threshold_multiplier: float = 2.0) -> list:
        """Find unusually high-cost items compared to category averages."""
        anomalies = []

        for category, items in self.categories.items():
            if len(items) < 3:
                continue

            monthly_fees = [i['monthly_fee'] for i in items if i['monthly_fee'] > 0]
            if not monthly_fees:
                continue

            avg = sum(monthly_fees) / len(monthly_fees)
            threshold = avg * threshold_multiplier

            for item in items:
                if item['monthly_fee'] > threshold:
                    anomalies.append({
                        'item': item,
                        'category_avg': avg,
                        'deviation': item['monthly_fee'] / avg if avg > 0 else 0,
                        'reason': f"Monthly fee ${item['monthly_fee']:,.2f} is {item['monthly_fee']/avg:.1f}x the category average of ${avg:,.2f}"
                    })

        anomalies.sort(key=lambda x: x['deviation'], reverse=True)
        return anomalies[:10]

    def get_savings_opportunities(self) -> list:
        """Identify top savings opportunities across all clients."""
        opportunities = []

        for client_name, summary in self.client_summaries.items():
            if len(summary['vendors']) >= 2:
                comparison = self.compare_vendors_for_client(client_name)
                if 'analysis' in comparison:
                    savings = comparison['analysis']['potential_savings']
                    if savings > 0:
                        opportunities.append({
                            'client': client_name,
                            'current_high': comparison['analysis']['highest_tco_vendor'],
                            'recommended': comparison['analysis']['lowest_tco_vendor'],
                            'savings': savings,
                            'savings_pct': comparison['analysis']['savings_percentage']
                        })

        opportunities.sort(key=lambda x: x['savings'], reverse=True)
        return opportunities

    # -------------------------------------------------------------------------
    # Summary Tools
    # -------------------------------------------------------------------------

    def get_executive_summary(self) -> dict:
        """Generate high-level executive summary."""
        total_clients = len(self.clients_data)
        total_line_items = len(self.all_line_items)

        # Calculate totals
        total_monthly = sum(i['monthly_fee'] for i in self.all_line_items)
        total_onetime = sum(i['one_time_fee'] for i in self.all_line_items)

        # Get savings opportunities
        opportunities = self.get_savings_opportunities()
        total_potential_savings = sum(o['savings'] for o in opportunities)

        # Vendor comparison
        vendor_comparison = self.compare_vendors_overall()

        return {
            'overview': {
                'total_clients': total_clients,
                'total_vendors': len(self.vendors_data),
                'total_line_items': total_line_items,
                'total_monthly_fees': total_monthly,
                'total_onetime_fees': total_onetime,
                'estimated_annual_spend': total_monthly * 12
            },
            'savings': {
                'total_potential_savings': total_potential_savings,
                'clients_with_savings': len(opportunities),
                'top_opportunity': opportunities[0] if opportunities else None
            },
            'vendor_insights': {
                'lowest_cost_vendor': vendor_comparison.get('lowest_avg_tco', {}).get('vendor'),
                'highest_cost_vendor': vendor_comparison.get('highest_avg_tco', {}).get('vendor')
            }
        }

    def get_analyst_deep_dive(self, client: str = None) -> dict:
        """Generate detailed analysis for analysts."""
        if client:
            client_details = self.get_client_details(client)
            if 'error' in client_details:
                return client_details

            # Add category breakdown
            category_breakdown = self.get_category_breakdown(client=client)

            # Add anomalies for this client
            client_items = [i for i in self.all_line_items
                          if client.lower() in i['client'].lower()]

            return {
                'client_details': client_details,
                'category_breakdown': category_breakdown,
                'line_item_count': len(client_items),
                'top_10_costs': sorted(client_items, key=lambda x: x['monthly_fee'], reverse=True)[:10]
            }

        # Global deep dive
        return {
            'total_line_items': len(self.all_line_items),
            'categories': self.get_category_breakdown(),
            'anomalies': self.find_anomalies(),
            'savings_opportunities': self.get_savings_opportunities()
        }


# =============================================================================
# AI Assistant Engine
# =============================================================================

class TCOAIAssistant:
    """Main AI Assistant with tool calling and context awareness."""

    SYSTEM_PROMPT = """You are an expert TCO (Total Cost of Ownership) Analysis Assistant for Arriba Advisors.
You help users understand, compare, and optimize their core banking technology costs.

Your capabilities:
1. SEARCH: Find specific line items, fees, products across all clients and vendors
2. COMPARE: Compare vendors for a client, or compare vendors across all clients
3. ANALYZE: Break down costs by category, find anomalies, identify savings
4. SUMMARIZE: Provide executive summaries or detailed analyst reports

Guidelines:
- Be concise but thorough
- Always provide specific numbers when available
- Format currency as $X,XXX.XX
- When comparing, always mention potential savings
- Proactively suggest follow-up questions
- Adjust detail level based on user role (Executive=high-level, Analyst=detailed)

When you need data, I will provide it from my tool calls. Base your answers ONLY on the data provided.
If asked about something not in the data, say so clearly."""

    def __init__(self, clients_data: dict, user_role: str = 'analyst'):
        self.tools = TCOAnalysisTools(clients_data)
        self.user_role = user_role
        self.context = ConversationContext()

    def _detect_intent(self, query: str) -> dict:
        """Detect user intent from query."""
        query_lower = query.lower()

        intent = {
            'type': 'general',
            'entities': {
                'clients': [],
                'vendors': [],
                'categories': []
            },
            'actions': []
        }

        # Detect client mentions
        for client_name in self.tools.client_summaries.keys():
            if client_name.lower() in query_lower:
                intent['entities']['clients'].append(client_name)

        # Detect vendor mentions
        vendor_patterns = ['fis', 'jack henry', 'jackhenry', 'jh', 'fiserv', 'finastra', 'csi']
        for v in vendor_patterns:
            if v in query_lower:
                vendor = v.upper().replace('JACKHENRY', 'JACK_HENRY').replace('JH', 'JACK_HENRY')
                if vendor not in intent['entities']['vendors']:
                    intent['entities']['vendors'].append(vendor)

        # Detect intent type
        if any(w in query_lower for w in ['compare', 'versus', 'vs', 'difference', 'better']):
            intent['type'] = 'comparison'
            intent['actions'].append('compare')

        elif any(w in query_lower for w in ['search', 'find', 'show', 'list', 'what']):
            intent['type'] = 'search'
            intent['actions'].append('search')

        elif any(w in query_lower for w in ['anomal', 'unusual', 'outlier', 'high cost', 'expensive']):
            intent['type'] = 'analysis'
            intent['actions'].append('find_anomalies')

        elif any(w in query_lower for w in ['sav', 'opportunity', 'reduce', 'optimize', 'lower']):
            intent['type'] = 'savings'
            intent['actions'].append('savings_analysis')

        elif any(w in query_lower for w in ['summary', 'overview', 'total', 'overall']):
            intent['type'] = 'summary'
            intent['actions'].append('summarize')

        elif any(w in query_lower for w in ['category', 'breakdown', 'by type']):
            intent['type'] = 'category_analysis'
            intent['actions'].append('category_breakdown')

        elif any(w in query_lower for w in ['detail', 'deep dive', 'all about']):
            intent['type'] = 'deep_dive'
            intent['actions'].append('deep_dive')

        # Check for price thresholds
        price_match = re.search(r'\$?([\d,]+(?:\.\d{2})?)', query)
        if price_match:
            intent['price_threshold'] = float(price_match.group(1).replace(',', ''))

        return intent

    def _gather_context_data(self, intent: dict) -> dict:
        """Gather relevant data based on detected intent."""
        data = {}

        # Always include basic stats
        data['summary'] = self.tools.get_executive_summary()

        if intent['type'] == 'comparison':
            if intent['entities']['clients']:
                for client in intent['entities']['clients']:
                    data[f'comparison_{client}'] = self.tools.compare_vendors_for_client(client)
            else:
                data['vendor_comparison'] = self.tools.compare_vendors_overall()

        elif intent['type'] == 'search':
            search_params = {}
            if intent['entities']['clients']:
                search_params['client'] = intent['entities']['clients'][0]
            if intent['entities']['vendors']:
                search_params['vendor'] = intent['entities']['vendors'][0]
            if 'price_threshold' in intent:
                search_params['min_monthly'] = intent['price_threshold']

            data['search_results'] = self.tools.search_line_items(**search_params, limit=15)

        elif intent['type'] == 'analysis':
            data['anomalies'] = self.tools.find_anomalies()

        elif intent['type'] == 'savings':
            data['savings_opportunities'] = self.tools.get_savings_opportunities()

        elif intent['type'] == 'category_analysis':
            params = {}
            if intent['entities']['clients']:
                params['client'] = intent['entities']['clients'][0]
            if intent['entities']['vendors']:
                params['vendor'] = intent['entities']['vendors'][0]
            data['category_breakdown'] = self.tools.get_category_breakdown(**params)

        elif intent['type'] == 'deep_dive':
            client = intent['entities']['clients'][0] if intent['entities']['clients'] else None
            if self.user_role == 'executive':
                data['executive_summary'] = self.tools.get_executive_summary()
            else:
                data['deep_dive'] = self.tools.get_analyst_deep_dive(client)

        elif intent['type'] == 'summary':
            data['executive_summary'] = self.tools.get_executive_summary()
            if self.user_role != 'executive':
                data['savings'] = self.tools.get_savings_opportunities()[:5]

        # Add client-specific data if clients mentioned
        for client in intent['entities']['clients'][:2]:  # Limit to 2 clients
            if f'client_{client}' not in data:
                data[f'client_{client}'] = self.tools.get_client_details(client)

        return data

    def _build_prompt(self, query: str, intent: dict, context_data: dict) -> str:
        """Build the full prompt for Claude."""
        prompt_parts = [self.SYSTEM_PROMPT]

        # Add role context
        role_context = {
            'executive': "The user is an Executive who needs high-level summaries and key insights. Avoid granular details.",
            'manager': "The user is a Manager who needs to review and approve comparisons. Focus on actionable insights.",
            'analyst': "The user is an Analyst who needs detailed information. Provide specific line items and numbers."
        }
        prompt_parts.append(f"\nUser Role: {self.user_role}")
        prompt_parts.append(role_context.get(self.user_role, role_context['analyst']))

        # Add conversation history
        if self.context.messages:
            prompt_parts.append("\n--- Recent Conversation ---")
            prompt_parts.append(self.context.get_history_for_prompt(6))

        # Add gathered data
        prompt_parts.append("\n--- Available Data ---")
        prompt_parts.append(json.dumps(context_data, indent=2, default=str))

        # Add the current query
        prompt_parts.append(f"\n--- Current Question ---\n{query}")

        # Add guidance based on intent
        prompt_parts.append("\n--- Response Guidance ---")
        if intent['type'] == 'comparison':
            prompt_parts.append("Provide a clear comparison with specific numbers. Highlight the recommended vendor and potential savings.")
        elif intent['type'] == 'savings':
            prompt_parts.append("Focus on actionable savings opportunities. Rank them by potential impact.")
        elif intent['type'] == 'summary':
            prompt_parts.append("Provide a concise summary with key metrics. Include the most important insight or recommendation.")

        prompt_parts.append("\nProvide a helpful, data-driven response:")

        return "\n".join(prompt_parts)

    def process_query(self, query: str) -> dict:
        """Process a user query and return response with metadata."""
        # Add user message to context
        self.context.add_message('user', query)

        # Detect intent
        intent = self._detect_intent(query)

        # Update context based on intent
        if intent['entities']['clients']:
            self.context.current_client = intent['entities']['clients'][0]
        if intent['entities']['vendors']:
            self.context.current_vendor = intent['entities']['vendors'][0]
        self.context.last_query_type = intent['type']

        # Gather relevant data
        context_data = self._gather_context_data(intent)

        # Build prompt
        prompt = self._build_prompt(query, intent, context_data)

        return {
            'prompt': prompt,
            'intent': intent,
            'context_data': context_data,
            'suggested_followups': self._get_suggested_followups(intent)
        }

    def add_response(self, response: str):
        """Add assistant response to conversation context."""
        self.context.add_message('assistant', response)

    def _get_suggested_followups(self, intent: dict) -> list:
        """Generate suggested follow-up questions based on context."""
        followups = []

        if intent['type'] == 'comparison' and intent['entities']['clients']:
            client = intent['entities']['clients'][0]
            followups.append(f"Show me the top cost items for {client}")
            followups.append(f"What categories have the biggest cost differences?")

        elif intent['type'] == 'summary':
            followups.append("Which clients have the highest savings potential?")
            followups.append("Show me cost anomalies across all clients")

        elif intent['type'] == 'savings':
            followups.append("Break down costs by category")
            followups.append("Which vendor is most cost-effective overall?")

        elif intent['type'] == 'search':
            followups.append("Find items over $1,000/month")
            followups.append("Show category breakdown for these results")

        # Default followups
        if not followups:
            followups = [
                "Show me a summary of all clients",
                "What are the biggest savings opportunities?",
                "Compare vendors overall"
            ]

        return followups[:3]

    def get_quick_insights(self) -> list:
        """Get quick insights for the dashboard."""
        insights = []

        # Top savings opportunity
        savings = self.tools.get_savings_opportunities()
        if savings:
            top = savings[0]
            insights.append({
                'type': 'savings',
                'title': 'Top Savings Opportunity',
                'message': f"{top['client']} could save ${top['savings']:,.0f} ({top['savings_pct']:.1f}%) by switching from {top['current_high']} to {top['recommended']}",
                'action': f"Compare vendors for {top['client']}"
            })

        # Anomaly alert
        anomalies = self.tools.find_anomalies()
        if anomalies:
            top = anomalies[0]
            insights.append({
                'type': 'anomaly',
                'title': 'Cost Anomaly Detected',
                'message': f"{top['item']['product_name']} at {top['item']['client']} is {top['deviation']:.1f}x the category average",
                'action': f"Review {top['item']['client']} line items"
            })

        # Vendor insight
        vendor_comparison = self.tools.compare_vendors_overall()
        if vendor_comparison.get('lowest_avg_tco'):
            lowest = vendor_comparison['lowest_avg_tco']
            insights.append({
                'type': 'insight',
                'title': 'Vendor Analysis',
                'message': f"{lowest['vendor']} has the lowest average TCO at ${lowest['avg_tco']:,.0f} across {lowest['client_count']} clients",
                'action': "Compare all vendors"
            })

        return insights


# =============================================================================
# Helper function for Flask integration
# =============================================================================

def create_assistant(clients_data: dict, user_role: str = 'analyst') -> TCOAIAssistant:
    """Factory function to create an AI assistant instance."""
    return TCOAIAssistant(clients_data, user_role)
