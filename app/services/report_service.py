from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import os

class ReportService:
    @staticmethod
    def generate_pdf(dataset_name, insights, summary_df, health_report, output_path):
        doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
        styles = getSampleStyleSheet()
        
        # Custom Styles
        title_style = styles['Title']
        title_style.textColor = colors.HexColor("#2c3e50")
        title_style.fontSize = 22
        
        h2_style = styles['Heading2']
        h2_style.textColor = colors.HexColor("#34495e")
        h2_style.fontSize = 16
        h2_style.spaceAfter = 10
        
        normal_style = styles['Normal']
        normal_style.fontSize = 11
        normal_style.leading = 14

        elements = []

        # Header - Professional Branding
        elements.append(Paragraph(f"Enterprise Intelligence Audit", title_style))
        elements.append(Paragraph(f"Project: {dataset_name}", styles['Heading3']))
        elements.append(Spacer(1, 24))

        # 1. Data Health Audit Section
        elements.append(Paragraph("I. Data Integrity & Health Audit", h2_style))
        health_data = [
            ["Metric", "Value", "Status"],
            ["Total Observations", str(health_report['total_rows']), "Verified"],
            ["Feature Dimensions", str(health_report['total_cols']), "Verified"],
            ["Duplicate Records", str(health_report['duplicate_rows']), "Critical Case" if health_report['duplicate_rows'] > 0 else "Optimal"],
            ["Missing Values", f"{health_report['missing_percentage']:.2f}%", "Attention Req." if health_report['missing_percentage'] > 5 else "Acceptable"]
        ]
        t_health = Table(health_data, colWidths=[150, 150, 150])
        t_health.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#34495e")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ]))
        elements.append(t_health)
        elements.append(Spacer(1, 20))

        # 2. Executive Summaries
        elements.append(Paragraph("II. Executive AI Insights", h2_style))
        for insight in insights:
            elements.append(Paragraph(f"• {insight}", normal_style))
            elements.append(Spacer(1, 4))
        elements.append(Spacer(1, 15))

        # 3. Statistical Analysis Section
        if summary_df is not None:
            elements.append(Paragraph("III. Preliminary Statistical Profile", h2_style))
            data = [summary_df.columns.tolist()] + summary_df.values.tolist()
            # Truncate strings to fit
            data = [[(str(cell)[:15] + '..') if len(str(cell)) > 15 else str(cell) for cell in row] for row in data]
            
            t = Table(data, hAlign='LEFT')
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#7f8c8d")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#f8f9fa")),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            elements.append(t)
            elements.append(Spacer(1, 20))

        # Footer
        elements.append(Spacer(1, 40))
        elements.append(Paragraph("AI-Generated Strategic Audit - Confidential Content", normal_style))

        doc.build(elements)
        return output_path

    @staticmethod
    def generate_forecast_pdf(dataset_name, model_type, target_col, mape, rmse, output_path):
        doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
        styles = getSampleStyleSheet()
        elements = []

        # Title
        title_style = styles['Title']
        title_style.textColor = colors.HexColor("#2980b9")
        elements.append(Paragraph(f"Predictive Insights Report", title_style))
        elements.append(Paragraph(f"Source: {dataset_name}", styles['Heading3']))
        elements.append(Spacer(1, 24))

        # Model Details
        elements.append(Paragraph("Model Configuration & Performance", styles['Heading2']))
        data = [
            ["Parameter", "Description", "Value"],
            ["Model", "Predictive Algorithm", model_type.upper()],
            ["Target", "Indicator Analyzed", target_col],
            ["MAPE", "Avg. Percentage Error", f"{mape*100:.2f}%"],
            ["RMSE", "Std Dev of Errors", f"{rmse:.2f}"]
        ]
        t = Table(data, colWidths=[120, 180, 150])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2980b9")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 24))

        # Prediction Analysis
        elements.append(Paragraph("Execution Summary", styles['Heading2']))
        reliability = "High" if mape < 0.1 else "Moderate" if mape < 0.3 else "Low"
        summary_text = (
            f"The time-series analysis for {target_col} indicates a {reliability} reliability forecast. "
            f"The {model_type} algorithm has successfully identified historical seasonality patterns "
            "and projected them into the defined business horizon."
        )
        elements.append(Paragraph(summary_text, styles['Normal']))
        
        # Footer
        elements.append(Spacer(1, 60))
        elements.append(Paragraph("Generated by Predictive Intelligence Hub", styles['Normal']))

        doc.build(elements)
        return output_path
