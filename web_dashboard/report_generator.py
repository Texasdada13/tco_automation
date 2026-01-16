"""
PDF Report Generator for TCO Analysis
Generates professional, branded PDF reports for client delivery.
"""

import io
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# PDF generation using reportlab
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, Image, HRFlowable
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


# Arriba Advisors brand colors
BRAND_COLORS = {
    'primary': colors.HexColor('#1e3a5f'),      # Deep blue
    'secondary': colors.HexColor('#2d5a87'),    # Medium blue
    'accent': colors.HexColor('#3182ce'),       # Bright blue
    'gold': colors.HexColor('#d4a84b'),         # Gold accent
    'light_gray': colors.HexColor('#f3f4f6'),
    'dark_gray': colors.HexColor('#374151'),
    'success': colors.HexColor('#10b981'),      # Green
    'warning': colors.HexColor('#f59e0b'),      # Yellow
    'danger': colors.HexColor('#ef4444'),       # Red
}


class TCOReportGenerator:
    """Generates professional PDF reports for TCO analysis."""

    def __init__(self):
        if not REPORTLAB_AVAILABLE:
            raise ImportError(
                "reportlab package not installed. "
                "Install with: pip install reportlab"
            )
        self.styles = self._create_styles()

    def _create_styles(self) -> Dict[str, ParagraphStyle]:
        """Create custom paragraph styles."""
        base_styles = getSampleStyleSheet()

        custom_styles = {
            'Title': ParagraphStyle(
                'CustomTitle',
                parent=base_styles['Title'],
                fontSize=28,
                textColor=BRAND_COLORS['primary'],
                spaceAfter=30,
                alignment=TA_CENTER,
            ),
            'Subtitle': ParagraphStyle(
                'CustomSubtitle',
                parent=base_styles['Normal'],
                fontSize=14,
                textColor=BRAND_COLORS['secondary'],
                spaceAfter=20,
                alignment=TA_CENTER,
            ),
            'Heading1': ParagraphStyle(
                'CustomH1',
                parent=base_styles['Heading1'],
                fontSize=18,
                textColor=BRAND_COLORS['primary'],
                spaceBefore=20,
                spaceAfter=12,
                borderPadding=5,
            ),
            'Heading2': ParagraphStyle(
                'CustomH2',
                parent=base_styles['Heading2'],
                fontSize=14,
                textColor=BRAND_COLORS['secondary'],
                spaceBefore=15,
                spaceAfter=8,
            ),
            'Body': ParagraphStyle(
                'CustomBody',
                parent=base_styles['Normal'],
                fontSize=10,
                textColor=BRAND_COLORS['dark_gray'],
                spaceAfter=8,
                leading=14,
            ),
            'BodyBold': ParagraphStyle(
                'CustomBodyBold',
                parent=base_styles['Normal'],
                fontSize=10,
                textColor=BRAND_COLORS['dark_gray'],
                spaceAfter=8,
                leading=14,
                fontName='Helvetica-Bold',
            ),
            'KPIValue': ParagraphStyle(
                'KPIValue',
                parent=base_styles['Normal'],
                fontSize=24,
                textColor=BRAND_COLORS['primary'],
                alignment=TA_CENTER,
                fontName='Helvetica-Bold',
            ),
            'KPILabel': ParagraphStyle(
                'KPILabel',
                parent=base_styles['Normal'],
                fontSize=10,
                textColor=BRAND_COLORS['dark_gray'],
                alignment=TA_CENTER,
            ),
            'Footer': ParagraphStyle(
                'Footer',
                parent=base_styles['Normal'],
                fontSize=8,
                textColor=colors.gray,
                alignment=TA_CENTER,
            ),
            'Recommendation': ParagraphStyle(
                'Recommendation',
                parent=base_styles['Normal'],
                fontSize=11,
                textColor=BRAND_COLORS['primary'],
                spaceAfter=10,
                leftIndent=20,
                bulletIndent=10,
            ),
        }

        return custom_styles

    def generate_executive_summary(
        self,
        client_name: str,
        client_data: Dict[str, Any],
        comparison_data: Optional[Dict] = None,
        ai_insights: Optional[List[Dict]] = None
    ) -> bytes:
        """Generate executive summary PDF for a client."""

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )

        story = []

        # Title Page
        story.extend(self._create_title_page(client_name))
        story.append(PageBreak())

        # Executive Summary Section
        story.extend(self._create_executive_summary_section(client_name, client_data, comparison_data))

        # KPI Dashboard
        story.extend(self._create_kpi_section(client_data, comparison_data))

        # Vendor Comparison (if available)
        if comparison_data and len(comparison_data.get('vendors', {})) >= 2:
            story.append(PageBreak())
            story.extend(self._create_comparison_section(client_name, comparison_data))

        # AI Insights & Recommendations
        if ai_insights:
            story.extend(self._create_insights_section(ai_insights))

        # Recommendations
        story.extend(self._create_recommendations_section(client_data, comparison_data))

        # Build PDF
        doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)

        buffer.seek(0)
        return buffer.getvalue()

    def _create_title_page(self, client_name: str) -> List:
        """Create the title page."""
        elements = []

        # Spacer to center content
        elements.append(Spacer(1, 2*inch))

        # Company branding
        elements.append(Paragraph(
            "ARRIBA ADVISORS",
            ParagraphStyle(
                'Brand',
                fontSize=16,
                textColor=BRAND_COLORS['accent'],
                alignment=TA_CENTER,
                spaceAfter=10,
                fontName='Helvetica',
                letterSpacing=3,
            )
        ))

        # Main title
        elements.append(Paragraph(
            "Total Cost of Ownership Analysis",
            self.styles['Title']
        ))

        # Client name
        elements.append(Paragraph(
            f"<b>{client_name}</b>",
            ParagraphStyle(
                'ClientName',
                fontSize=20,
                textColor=BRAND_COLORS['secondary'],
                alignment=TA_CENTER,
                spaceAfter=30,
            )
        ))

        # Divider
        elements.append(HRFlowable(
            width="50%",
            thickness=2,
            color=BRAND_COLORS['gold'],
            spaceBefore=20,
            spaceAfter=20,
            hAlign='CENTER'
        ))

        # Date
        elements.append(Paragraph(
            f"Report Generated: {datetime.now().strftime('%B %d, %Y')}",
            self.styles['Subtitle']
        ))

        # Confidentiality notice
        elements.append(Spacer(1, 2*inch))
        elements.append(Paragraph(
            "<i>CONFIDENTIAL - For Internal Use Only</i>",
            ParagraphStyle(
                'Confidential',
                fontSize=10,
                textColor=colors.gray,
                alignment=TA_CENTER,
            )
        ))

        return elements

    def _create_executive_summary_section(
        self,
        client_name: str,
        client_data: Dict,
        comparison_data: Optional[Dict]
    ) -> List:
        """Create executive summary text section."""
        elements = []

        elements.append(Paragraph("Executive Summary", self.styles['Heading1']))

        # Calculate summary stats
        vendors = list(client_data.get('vendors', {}).keys())
        total_proposals = client_data.get('total_proposals', 0)

        # Get TCO values
        tco_values = {}
        for vendor, proposals in client_data.get('vendors', {}).items():
            if proposals:
                tco_values[vendor] = proposals[0].get('tco_7yr', 0)

        # Summary paragraph
        if len(vendors) >= 2:
            lowest_vendor = min(tco_values, key=tco_values.get) if tco_values else vendors[0]
            highest_vendor = max(tco_values, key=tco_values.get) if tco_values else vendors[-1]
            savings = tco_values.get(highest_vendor, 0) - tco_values.get(lowest_vendor, 0)

            summary_text = f"""
            This analysis compares <b>{len(vendors)} vendor proposals</b> for {client_name}'s
            core banking technology requirements. After comprehensive evaluation of
            {total_proposals} proposal document(s), our analysis reveals significant
            cost differences between vendors.
            <br/><br/>
            <b>Key Finding:</b> {lowest_vendor} offers the lowest 7-year Total Cost of Ownership
            at <b>${tco_values.get(lowest_vendor, 0):,.0f}</b>, representing potential savings of
            <b>${savings:,.0f}</b> compared to {highest_vendor}.
            """
        else:
            vendor = vendors[0] if vendors else "Unknown"
            tco = tco_values.get(vendor, 0)
            summary_text = f"""
            This analysis evaluates the <b>{vendor}</b> proposal for {client_name}'s
            core banking technology requirements. The 7-year Total Cost of Ownership
            is estimated at <b>${tco:,.0f}</b>.
            <br/><br/>
            Additional vendor proposals are recommended to enable comparative analysis
            and identify potential cost optimization opportunities.
            """

        elements.append(Paragraph(summary_text, self.styles['Body']))
        elements.append(Spacer(1, 0.25*inch))

        return elements

    def _create_kpi_section(self, client_data: Dict, comparison_data: Optional[Dict]) -> List:
        """Create KPI dashboard section."""
        elements = []

        elements.append(Paragraph("Key Metrics", self.styles['Heading2']))

        # Calculate KPIs
        vendors = client_data.get('vendors', {})
        tco_values = []
        monthly_totals = []
        line_item_counts = []

        for vendor, proposals in vendors.items():
            if proposals:
                p = proposals[0]
                tco_values.append(p.get('tco_7yr', 0))
                monthly_totals.append(p.get('total_monthly', 0))
                line_item_counts.append(p.get('line_items_count', 0))

        total_tco = sum(tco_values) / len(tco_values) if tco_values else 0
        avg_monthly = sum(monthly_totals) / len(monthly_totals) if monthly_totals else 0
        total_items = sum(line_item_counts)

        # Calculate potential savings
        savings = 0
        if len(tco_values) >= 2:
            savings = max(tco_values) - min(tco_values)

        # Create KPI table
        kpi_data = [
            [
                self._create_kpi_cell("Vendors Analyzed", str(len(vendors))),
                self._create_kpi_cell("7-Year TCO", f"${total_tco:,.0f}"),
                self._create_kpi_cell("Monthly Fees", f"${avg_monthly:,.0f}"),
                self._create_kpi_cell("Potential Savings", f"${savings:,.0f}"),
            ]
        ]

        kpi_table = Table(kpi_data, colWidths=[1.7*inch]*4)
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), BRAND_COLORS['light_gray']),
            ('BOX', (0, 0), (-1, -1), 1, BRAND_COLORS['primary']),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.white),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ]))

        elements.append(kpi_table)
        elements.append(Spacer(1, 0.3*inch))

        return elements

    def _create_kpi_cell(self, label: str, value: str) -> List:
        """Create a KPI cell with value and label."""
        return [
            Paragraph(value, self.styles['KPIValue']),
            Paragraph(label, self.styles['KPILabel']),
        ]

    def _create_comparison_section(self, client_name: str, comparison_data: Dict) -> List:
        """Create vendor comparison table section."""
        elements = []

        elements.append(Paragraph("Vendor Comparison", self.styles['Heading1']))
        elements.append(Paragraph(
            f"Side-by-side analysis of vendor proposals for {client_name}",
            self.styles['Body']
        ))

        # Build comparison table
        vendors = comparison_data.get('vendors', {})

        # Header row
        headers = ['Metric'] + list(vendors.keys())

        # Data rows
        rows = [headers]

        # Monthly Fees row
        monthly_row = ['Monthly Fees']
        for vendor, data in vendors.items():
            monthly_row.append(f"${data.get('monthly_fees', 0):,.0f}")
        rows.append(monthly_row)

        # One-Time Fees row
        onetime_row = ['One-Time Fees']
        for vendor, data in vendors.items():
            onetime_row.append(f"${data.get('onetime_fees', 0):,.0f}")
        rows.append(onetime_row)

        # 7-Year TCO row
        tco_row = ['7-Year TCO']
        tco_values = {}
        for vendor, data in vendors.items():
            tco = data.get('tco_7yr', 0)
            tco_values[vendor] = tco
            tco_row.append(f"${tco:,.0f}")
        rows.append(tco_row)

        # Line Items row
        items_row = ['Line Items']
        for vendor, data in vendors.items():
            items_row.append(str(data.get('line_items_count', 0)))
        rows.append(items_row)

        # Delta row (vs lowest)
        if tco_values:
            lowest_tco = min(tco_values.values())
            delta_row = ['Delta vs. Lowest']
            for vendor, data in vendors.items():
                delta = tco_values[vendor] - lowest_tco
                if delta == 0:
                    delta_row.append("LOWEST")
                else:
                    delta_row.append(f"+${delta:,.0f}")
            rows.append(delta_row)

        # Create table
        col_widths = [1.5*inch] + [1.3*inch] * len(vendors)
        comparison_table = Table(rows, colWidths=col_widths)

        # Style the table
        style = [
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), BRAND_COLORS['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),

            # First column styling
            ('BACKGROUND', (0, 1), (0, -1), BRAND_COLORS['light_gray']),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),

            # General styling
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('BOX', (0, 0), (-1, -1), 1, BRAND_COLORS['primary']),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]

        # Highlight lowest TCO column
        if tco_values:
            lowest_vendor = min(tco_values, key=tco_values.get)
            vendor_list = list(vendors.keys())
            if lowest_vendor in vendor_list:
                col_idx = vendor_list.index(lowest_vendor) + 1
                style.append(('BACKGROUND', (col_idx, 1), (col_idx, -1), colors.HexColor('#dcfce7')))

        comparison_table.setStyle(TableStyle(style))

        elements.append(comparison_table)
        elements.append(Spacer(1, 0.3*inch))

        return elements

    def _create_insights_section(self, ai_insights: List[Dict]) -> List:
        """Create AI insights section."""
        elements = []

        elements.append(Paragraph("AI-Generated Insights", self.styles['Heading2']))

        for insight in ai_insights[:5]:  # Limit to 5 insights
            insight_type = insight.get('type', 'insight')
            title = insight.get('title', '')
            message = insight.get('message', '')

            # Color based on type
            if insight_type == 'savings':
                bullet_color = BRAND_COLORS['success']
            elif insight_type == 'anomaly':
                bullet_color = BRAND_COLORS['warning']
            else:
                bullet_color = BRAND_COLORS['accent']

            elements.append(Paragraph(
                f"<b>{title}:</b> {message}",
                ParagraphStyle(
                    'Insight',
                    parent=self.styles['Body'],
                    leftIndent=15,
                    bulletIndent=5,
                    spaceBefore=5,
                )
            ))

        elements.append(Spacer(1, 0.2*inch))

        return elements

    def _create_recommendations_section(
        self,
        client_data: Dict,
        comparison_data: Optional[Dict]
    ) -> List:
        """Create recommendations section."""
        elements = []

        elements.append(Paragraph("Recommendations", self.styles['Heading1']))

        vendors = client_data.get('vendors', {})
        tco_values = {}
        for vendor, proposals in vendors.items():
            if proposals:
                tco_values[vendor] = proposals[0].get('tco_7yr', 0)

        recommendations = []

        if len(tco_values) >= 2:
            lowest_vendor = min(tco_values, key=tco_values.get)
            highest_vendor = max(tco_values, key=tco_values.get)
            savings = tco_values[highest_vendor] - tco_values[lowest_vendor]
            savings_pct = (savings / tco_values[highest_vendor] * 100) if tco_values[highest_vendor] > 0 else 0

            recommendations.append(
                f"<b>Primary Recommendation:</b> Based on TCO analysis, {lowest_vendor} "
                f"offers the most cost-effective solution with potential savings of "
                f"${savings:,.0f} ({savings_pct:.1f}%) over the contract term."
            )

            recommendations.append(
                f"<b>Negotiation Opportunity:</b> Use the {lowest_vendor} pricing as "
                f"leverage to negotiate better terms with {highest_vendor} if their "
                f"solution better meets functional requirements."
            )

        recommendations.append(
            "<b>Next Steps:</b> Schedule vendor presentations to evaluate functional "
            "capabilities alongside cost analysis. Request detailed implementation "
            "timelines and references from comparable institutions."
        )

        recommendations.append(
            "<b>Due Diligence:</b> Verify all pricing assumptions including volume "
            "projections, growth rates, and CPI escalation clauses. Confirm "
            "implementation fees are comprehensive and include all required services."
        )

        for rec in recommendations:
            elements.append(Paragraph(f"• {rec}", self.styles['Recommendation']))

        return elements

    def _add_header_footer(self, canvas, doc):
        """Add header and footer to each page."""
        canvas.saveState()

        # Header
        canvas.setStrokeColor(BRAND_COLORS['primary'])
        canvas.setLineWidth(2)
        canvas.line(0.75*inch, 10.25*inch, 7.75*inch, 10.25*inch)

        # Footer
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.gray)

        # Left footer - company name
        canvas.drawString(0.75*inch, 0.5*inch, "Arriba Advisors | TCO Analysis")

        # Right footer - page number
        page_num = canvas.getPageNumber()
        canvas.drawRightString(7.75*inch, 0.5*inch, f"Page {page_num}")

        # Center footer - confidential
        canvas.drawCentredString(4.25*inch, 0.5*inch, "CONFIDENTIAL")

        canvas.restoreState()

    def generate_comparison_report(
        self,
        clients_data: Dict[str, Any],
        selected_clients: List[str] = None
    ) -> bytes:
        """Generate a multi-client comparison report."""

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )

        story = []

        # Title
        story.append(Paragraph("ARRIBA ADVISORS", ParagraphStyle(
            'Brand', fontSize=14, textColor=BRAND_COLORS['accent'],
            alignment=TA_CENTER, spaceAfter=5, letterSpacing=2
        )))
        story.append(Paragraph("Multi-Client TCO Analysis", self.styles['Title']))
        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%B %d, %Y')}",
            self.styles['Subtitle']
        ))
        story.append(Spacer(1, 0.3*inch))

        # Filter clients if specified
        if selected_clients:
            filtered_data = {k: v for k, v in clients_data.items() if k in selected_clients}
        else:
            filtered_data = clients_data

        # Summary table
        story.append(Paragraph("Client Summary", self.styles['Heading1']))

        # Build summary table
        headers = ['Client', 'Vendors', 'TCO Range', 'Potential Savings']
        rows = [headers]

        for client_name, client in filtered_data.items():
            vendors = list(client.get('vendors', {}).keys())
            tco_values = []
            for v, proposals in client.get('vendors', {}).items():
                if proposals:
                    tco_values.append(proposals[0].get('tco_7yr', 0))

            if tco_values:
                tco_range = f"${min(tco_values):,.0f} - ${max(tco_values):,.0f}"
                savings = max(tco_values) - min(tco_values) if len(tco_values) > 1 else 0
            else:
                tco_range = "N/A"
                savings = 0

            rows.append([
                client_name,
                ", ".join(vendors),
                tco_range,
                f"${savings:,.0f}"
            ])

        summary_table = Table(rows, colWidths=[2*inch, 1.5*inch, 2*inch, 1.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BRAND_COLORS['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('BOX', (0, 0), (-1, -1), 1, BRAND_COLORS['primary']),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BRAND_COLORS['light_gray']]),
        ]))

        story.append(summary_table)

        # Build PDF
        doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)

        buffer.seek(0)
        return buffer.getvalue()


def generate_client_report(client_name: str, client_data: Dict, comparison_data: Dict = None, ai_insights: List = None) -> bytes:
    """Convenience function to generate a client report."""
    generator = TCOReportGenerator()
    return generator.generate_executive_summary(client_name, client_data, comparison_data, ai_insights)
