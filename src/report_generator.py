#!/usr/bin/env python3
"""
Network Configuration Report Generator

Generates comprehensive compliance reports in multiple formats including
text, JSON, HTML, and CSV for network configuration analysis.
"""

import json
import logging
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class ReportGenerator:
    """Generates comprehensive compliance reports in multiple formats."""
    
    def __init__(self, compliance_results: Dict[str, Any]):
        """
        Initialize the report generator.
        
        Args:
            compliance_results: Results from ComplianceChecker
        """
        self.logger = logging.getLogger(__name__)
        self.results = compliance_results
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def generate_text_report(self, output_file: str) -> bool:
        """Generate a human-readable text report."""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(self._generate_text_content())
            
            self.logger.info(f"Text report generated: {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error generating text report: {e}")
            return False
    
    def generate_json_report(self, output_file: str) -> bool:
        """Generate a JSON report for programmatic access."""
        try:
            report_data = {
                'metadata': {
                    'generated_at': self.timestamp,
                    'tool_version': '2.0.0',
                    'report_type': 'compliance_analysis'
                },
                'results': self.results
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"JSON report generated: {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error generating JSON report: {e}")
            return False
    
    def generate_html_report(self, output_file: str) -> bool:
        """Generate an HTML report with styling and interactive elements."""
        try:
            html_content = self._generate_html_content()
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"HTML report generated: {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error generating HTML report: {e}")
            return False
    
    def generate_csv_report(self, output_file: str) -> bool:
        """Generate a CSV report for spreadsheet analysis."""
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write header
                writer.writerow([
                    'Rule Name', 'Status', 'Severity', 'Description',
                    'Non-Compliant Interfaces', 'Total Interfaces'
                ])
                
                # Write data
                for rule_name, rule_result in self.results['detailed_results'].items():
                    writer.writerow([
                        rule_name,
                        rule_result['status'],
                        rule_result.get('severity', 'medium'),
                        rule_result.get('description', ''),
                        len(rule_result.get('non_compliant_interfaces', [])),
                        len(rule_result.get('details', []))
                    ])
            
            self.logger.info(f"CSV report generated: {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error generating CSV report: {e}")
            return False
    
    def _generate_text_content(self) -> str:
        """Generate the content for text report."""
        content = []
        
        # Header
        content.append("=" * 80)
        content.append("NETWORK CONFIGURATION COMPLIANCE REPORT")
        content.append("=" * 80)
        content.append(f"Generated: {self.timestamp}")
        content.append("")
        
        # Summary
        summary = self.results['summary']
        content.append("SUMMARY")
        content.append("-" * 40)
        content.append(f"Total Policies: {summary['total_policies']}")
        content.append(f"Compliant Policies: {summary['compliant_policies']}")
        content.append(f"Non-Compliant Policies: {summary['non_compliant_policies']}")
        content.append(f"Total Interfaces: {summary['total_interfaces']}")
        
        compliance_score = (summary['compliant_policies'] / summary['total_policies'] * 100) if summary['total_policies'] > 0 else 100
        content.append(f"Compliance Score: {compliance_score:.1f}%")
        content.append("")
        
        # Detailed Results
        content.append("DETAILED RESULTS")
        content.append("-" * 40)
        
        for rule_name, rule_result in self.results['detailed_results'].items():
            content.append(f"Rule: {rule_name}")
            content.append(f"  Status: {rule_result['status'].upper()}")
            content.append(f"  Severity: {rule_result.get('severity', 'medium')}")
            content.append(f"  Description: {rule_result.get('description', '')}")
            
            if rule_result['status'] == 'non_compliant':
                non_compliant = rule_result.get('non_compliant_interfaces', [])
                content.append(f"  Non-Compliant Interfaces: {len(non_compliant)}")
                if non_compliant:
                    content.append(f"    {', '.join(non_compliant)}")
            
            content.append("")
        
        # Recommendations
        content.append("RECOMMENDATIONS")
        content.append("-" * 40)
        for recommendation in self.results.get('recommendations', []):
            content.append(f"• {recommendation}")
        content.append("")
        
        # Footer
        content.append("=" * 80)
        content.append("Report generated by Network Configuration Compliance Checker")
        content.append("=" * 80)
        
        return '\n'.join(content)
    
    def _generate_html_content(self) -> str:
        """Generate the content for HTML report."""
        # Prepare data for template
        summary = self.results['summary']
        compliance_score = (summary['compliant_policies'] / summary['total_policies'] * 100) if summary['total_policies'] > 0 else 100
        
        # Generate detailed results HTML
        detailed_results_html = ""
        for rule_name, rule_result in self.results['detailed_results'].items():
            status_class = rule_result['status']
            severity_class = rule_result.get('severity', 'medium')
            
            detailed_results_html += f"""
            <div class="rule">
                <div class="rule-header {status_class} {severity_class}">
                    <h3>{rule_name}</h3>
                    <span class="status {status_class}">{rule_result['status']}</span>
                    <span class="severity">Severity: {rule_result.get('severity', 'medium')}</span>
                </div>
                <div class="rule-content">
                    <p><strong>Description:</strong> {rule_result.get('description', '')}</p>
            """
            
            if rule_result['status'] == 'non_compliant':
                non_compliant = rule_result.get('non_compliant_interfaces', [])
                detailed_results_html += f"""
                    <p><strong>Non-Compliant Interfaces:</strong> {len(non_compliant)}</p>
                    <p><strong>Details:</strong></p>
                    <ul>
                """
                for detail in rule_result.get('details', []):
                    if detail.get('status') == 'non_compliant':
                        detailed_results_html += f"<li>{detail['interface']}: {', '.join(detail.get('issues', []))}</li>"
                detailed_results_html += "</ul>"
            
            detailed_results_html += """
                </div>
            </div>
            """
        
        # Generate recommendations HTML
        recommendations_html = ""
        for recommendation in self.results.get('recommendations', []):
            recommendations_html += f"<li>{recommendation}</li>"
        
        # Simple HTML template
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Network Configuration Compliance Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; border-bottom: 3px solid #007bff; padding-bottom: 20px; margin-bottom: 30px; }}
        .summary {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 30px; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 15px; }}
        .summary-item {{ text-align: center; padding: 15px; background-color: white; border-radius: 5px; border-left: 4px solid #007bff; }}
        .summary-item h3 {{ margin: 0; color: #007bff; font-size: 2em; }}
        .summary-item p {{ margin: 5px 0 0 0; color: #666; }}
        .rule {{ margin-bottom: 25px; border: 1px solid #ddd; border-radius: 5px; overflow: hidden; }}
        .rule-header {{ padding: 15px; background-color: #f8f9fa; border-bottom: 1px solid #ddd; }}
        .rule-header.compliant {{ background-color: #d4edda; border-color: #c3e6cb; }}
        .rule-header.non-compliant {{ background-color: #f8d7da; border-color: #f5c6cb; }}
        .rule-header.critical {{ background-color: #f8d7da; border-color: #dc3545; }}
        .rule-content {{ padding: 15px; }}
        .status {{ display: inline-block; padding: 5px 10px; border-radius: 3px; font-weight: bold; text-transform: uppercase; font-size: 0.8em; }}
        .status.compliant {{ background-color: #28a745; color: white; }}
        .status.non-compliant {{ background-color: #dc3545; color: white; }}
        .status.critical {{ background-color: #dc3545; color: white; }}
        .recommendations {{ background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 20px; margin-top: 30px; }}
        .recommendations h3 {{ color: #856404; margin-top: 0; }}
        .recommendations ul {{ margin: 0; padding-left: 20px; }}
        .recommendations li {{ margin-bottom: 8px; }}
        .footer {{ text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Network Configuration Compliance Report</h1>
            <p>Generated on {self.timestamp}</p>
        </div>
        
        <div class="summary">
            <h2>Summary</h2>
            <div class="summary-grid">
                <div class="summary-item">
                    <h3>{summary['total_policies']}</h3>
                    <p>Total Policies</p>
                </div>
                <div class="summary-item">
                    <h3>{summary['compliant_policies']}</h3>
                    <p>Compliant</p>
                </div>
                <div class="summary-item">
                    <h3>{summary['non_compliant_policies']}</h3>
                    <p>Non-Compliant</p>
                </div>
                <div class="summary-item">
                    <h3>{compliance_score:.1f}%</h3>
                    <p>Compliance Score</p>
                </div>
            </div>
        </div>
        
        <h2>Detailed Results</h2>
        {detailed_results_html}
        
        <div class="recommendations">
            <h3>Recommendations</h3>
            <ul>
                {recommendations_html}
            </ul>
        </div>
        
        <div class="footer">
            <p>Report generated by Network Configuration Compliance Checker v2.0.0</p>
        </div>
    </div>
</body>
</html>"""
        
        return html_content
    
    def generate_all_reports(self, output_dir: str) -> Dict[str, bool]:
        """Generate all report formats in the specified directory."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        results = {}
        
        # Generate all report types
        results['text'] = self.generate_text_report(str(output_path / "compliance_report.txt"))
        results['json'] = self.generate_json_report(str(output_path / "compliance_report.json"))
        results['html'] = self.generate_html_report(str(output_path / "compliance_report.html"))
        results['csv'] = self.generate_csv_report(str(output_path / "compliance_report.csv"))
        
        self.logger.info(f"Generated all reports in: {output_dir}")
        return results
