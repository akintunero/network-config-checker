#!/usr/bin/env python3
"""
Network Configuration Compliance Checker

Checks network device configurations against predefined security policies
and best practices.
"""

import yaml
import logging
import re
from typing import Dict, List, Any, Optional
from pathlib import Path


class ComplianceChecker:
    """Checks network configurations against compliance policies."""
    
    def __init__(self, parsed_config: Dict[str, List[str]], policies: str):
        """
        Initialize the compliance checker.
        
        Args:
            parsed_config: Parsed configuration from ConfigParser
            policies: Path to policy file or policy dictionary
        """
        self.logger = logging.getLogger(__name__)
        self.parsed_config = parsed_config
        self.policies = self.load_policies(policies)
        self.results = {}
        
    def load_policies(self, policies) -> Dict[str, Any]:
        """Load compliance policies from a YAML file or dictionary."""
        if isinstance(policies, dict):
            return policies
        elif isinstance(policies, str):
            try:
                with open(policies, "r", encoding='utf-8') as file:
                    loaded_policies = yaml.safe_load(file)
                self.logger.info(f"Loaded policies from file: {policies}")
                return loaded_policies
            except FileNotFoundError:
                raise FileNotFoundError(f"Policy file not found: {policies}")
            except yaml.YAMLError as e:
                raise ValueError(f"Error parsing YAML file: {e}")
        else:
            raise ValueError("Policies must be either a dictionary or a file path string.")
    
    def check_compliance(self) -> Dict[str, Any]:
        """Check configuration against all security policies."""
        self.logger.info(f"Starting compliance check with {len(self.policies)} policies")
        
        results = {
            'summary': {
                'total_policies': len(self.policies),
                'compliant_policies': 0,
                'non_compliant_policies': 0,
                'total_interfaces': len(self.parsed_config)
            },
            'detailed_results': {},
            'recommendations': []
        }
        
        for rule_name, rule_details in self.policies.items():
            try:
                rule_result = self.apply_rule(rule_name, rule_details)
                results['detailed_results'][rule_name] = rule_result
                
                if rule_result['status'] == 'compliant':
                    results['summary']['compliant_policies'] += 1
                else:
                    results['summary']['non_compliant_policies'] += 1
                    
            except Exception as e:
                self.logger.error(f"Error applying rule {rule_name}: {e}")
                results['detailed_results'][rule_name] = {
                    'status': 'error',
                    'message': f"Error applying rule: {e}",
                    'details': []
                }
        
        # Generate recommendations
        results['recommendations'] = self._generate_recommendations(results['detailed_results'])
        
        self.logger.info(f"Compliance check completed: {results['summary']['compliant_policies']} compliant, "
                        f"{results['summary']['non_compliant_policies']} non-compliant")
        
        return results
    
    def apply_rule(self, rule_name: str, rule_details: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a compliance rule to the parsed configuration."""
        rule_result = {
            'status': 'compliant',
            'description': rule_details.get('description', ''),
            'severity': rule_details.get('severity', 'medium'),
            'details': [],
            'non_compliant_interfaces': []
        }
        
        conditions = rule_details.get('conditions', [])
        required_conditions = rule_details.get('required_conditions', [])
        forbidden_conditions = rule_details.get('forbidden_conditions', [])
        
        for interface_name, config_lines in self.parsed_config.items():
            interface_text = ' '.join(config_lines).lower()
            interface_result = {
                'interface': interface_name,
                'status': 'compliant',
                'issues': []
            }
            
            # Check required conditions
            for condition in required_conditions:
                if not self._check_condition(interface_text, condition):
                    interface_result['status'] = 'non_compliant'
                    interface_result['issues'].append(f"Missing required condition: {condition}")
            
            # Check forbidden conditions
            for condition in forbidden_conditions:
                if self._check_condition(interface_text, condition):
                    interface_result['status'] = 'non_compliant'
                    interface_result['issues'].append(f"Forbidden condition found: {condition}")
            
            # Check general conditions
            for condition in conditions:
                if not self._check_condition(interface_text, condition):
                    interface_result['status'] = 'non_compliant'
                    interface_result['issues'].append(f"Missing condition: {condition}")
            
            # Update rule result
            if interface_result['status'] == 'non_compliant':
                rule_result['status'] = 'non_compliant'
                rule_result['non_compliant_interfaces'].append(interface_name)
            
            rule_result['details'].append(interface_result)
        
        return rule_result
    
    def _check_condition(self, interface_text: str, condition: str) -> bool:
        """Check if a condition is met in the interface configuration."""
        # Handle different types of conditions
        if condition.startswith('regex:'):
            # Regular expression condition
            pattern = condition[6:]  # Remove 'regex:' prefix
            return bool(re.search(pattern, interface_text, re.IGNORECASE))
        elif condition.startswith('not:'):
            # Negative condition
            pattern = condition[4:]  # Remove 'not:' prefix
            return not bool(re.search(pattern, interface_text, re.IGNORECASE))
        else:
            # Simple text condition
            return condition.lower() in interface_text
    
    def _generate_recommendations(self, detailed_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on compliance results."""
        recommendations = []
        
        for rule_name, result in detailed_results.items():
            if result['status'] == 'non_compliant':
                non_compliant_count = len(result.get('non_compliant_interfaces', []))
                if non_compliant_count > 0:
                    recommendations.append(
                        f"Fix {rule_name}: {non_compliant_count} interfaces are non-compliant"
                    )
        
        # Add general recommendations
        if not recommendations:
            recommendations.append("All policies are compliant - good job!")
        
        return recommendations
    
    def get_compliance_score(self) -> float:
        """Calculate overall compliance score (0-100)."""
        if not self.results:
            self.results = self.check_compliance()
        
        summary = self.results['summary']
        total_policies = summary['total_policies']
        
        if total_policies == 0:
            return 100.0
        
        compliant_policies = summary['compliant_policies']
        return (compliant_policies / total_policies) * 100
    
    def get_critical_issues(self) -> List[str]:
        """Get list of critical compliance issues."""
        critical_issues = []
        
        if not self.results:
            self.results = self.check_compliance()
        
        for rule_name, result in self.results['detailed_results'].items():
            if result.get('severity') == 'critical' and result['status'] == 'non_compliant':
                critical_issues.append(f"Critical: {rule_name} - {result.get('description', '')}")
        
        return critical_issues
    
    def export_results(self, output_file: str):
        """Export compliance results to a file."""
        if not self.results:
            self.results = self.check_compliance()
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.results, f, default_flow_style=False, indent=2)
            self.logger.info(f"Results exported to: {output_file}")
        except Exception as e:
            self.logger.error(f"Error exporting results: {e}")
            raise
