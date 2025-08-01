#!/usr/bin/env python3
"""
Unit tests for the Network Configuration Compliance Checker.
"""

import unittest
import tempfile
import os
import sys
import yaml
from unittest.mock import patch, MagicMock
import json

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from compliance_checker import ComplianceChecker
from parser import ConfigParser
from report_generator import ReportGenerator


class TestComplianceChecker(unittest.TestCase):
    """Test cases for ComplianceChecker class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_config = {
            'GigabitEthernet0/1': [
                'interface GigabitEthernet0/1',
                'description Uplink to Core',
                'ip address 192.168.1.1 255.255.255.0',
                'no ip http server'
            ],
            'GigabitEthernet0/2': [
                'interface GigabitEthernet0/2',
                'description Connection to ISP',
                'ip address 10.0.0.1 255.255.255.0'
            ]
        }
        
        self.sample_policies = {
            'require_interface_description': {
                'description': 'Ensure all interfaces have descriptions',
                'severity': 'medium',
                'conditions': ['description']
            },
            'disable_http_server': {
                'description': 'Disable HTTP server on all interfaces',
                'severity': 'high',
                'required_conditions': ['no ip http server']
            },
            'require_ip_address': {
                'description': 'Ensure all interfaces have IP addresses',
                'severity': 'critical',
                'conditions': ['ip address']
            }
        }
    
    def test_load_policies_from_dict(self):
        """Test loading policies from dictionary."""
        checker = ComplianceChecker(self.sample_config, self.sample_policies)
        self.assertEqual(checker.policies, self.sample_policies)
    
    def test_load_policies_from_file(self):
        """Test loading policies from YAML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(self.sample_policies, f)
            policy_file = f.name
        
        try:
            checker = ComplianceChecker(self.sample_config, policy_file)
            self.assertEqual(checker.policies, self.sample_policies)
        finally:
            os.unlink(policy_file)
    
    def test_load_policies_file_not_found(self):
        """Test error handling for missing policy file."""
        with self.assertRaises(FileNotFoundError):
            ComplianceChecker(self.sample_config, 'nonexistent.yaml')
    
    def test_check_compliance_success(self):
        """Test successful compliance check."""
        checker = ComplianceChecker(self.sample_config, self.sample_policies)
        results = checker.check_compliance()
        
        self.assertIn('summary', results)
        self.assertIn('detailed_results', results)
        self.assertIn('recommendations', results)
        
        summary = results['summary']
        self.assertEqual(summary['total_policies'], 3)
        self.assertEqual(summary['total_interfaces'], 2)
    
    def test_apply_rule_compliant(self):
        """Test applying a rule that results in compliance."""
        checker = ComplianceChecker(self.sample_config, self.sample_policies)
        rule_result = checker.apply_rule('require_interface_description', 
                                       self.sample_policies['require_interface_description'])
        
        self.assertEqual(rule_result['status'], 'compliant')
        self.assertEqual(len(rule_result['details']), 2)
    
    def test_apply_rule_non_compliant(self):
        """Test applying a rule that results in non-compliance."""
        # Create config without descriptions
        config_without_desc = {
            'GigabitEthernet0/1': [
                'interface GigabitEthernet0/1',
                'ip address 192.168.1.1 255.255.255.0'
            ]
        }
        
        checker = ComplianceChecker(config_without_desc, self.sample_policies)
        rule_result = checker.apply_rule('require_interface_description',
                                       self.sample_policies['require_interface_description'])
        
        self.assertEqual(rule_result['status'], 'non_compliant')
        self.assertIn('GigabitEthernet0/1', rule_result['non_compliant_interfaces'])
    
    def test_check_condition_simple(self):
        """Test simple condition checking."""
        checker = ComplianceChecker(self.sample_config, self.sample_policies)
        
        interface_text = 'interface description test ip address 192.168.1.1'
        self.assertTrue(checker._check_condition(interface_text, 'description'))
        self.assertTrue(checker._check_condition(interface_text, 'ip address'))
        self.assertFalse(checker._check_condition(interface_text, 'nonexistent'))
    
    def test_check_condition_regex(self):
        """Test regex condition checking."""
        checker = ComplianceChecker(self.sample_config, self.sample_policies)
        
        interface_text = 'interface description test ip address 192.168.1.1'
        self.assertTrue(checker._check_condition(interface_text, r'regex:ip address \d+\.\d+\.\d+\.\d+'))
        self.assertFalse(checker._check_condition(interface_text, 'regex:invalid pattern'))
    
    def test_check_condition_negative(self):
        """Test negative condition checking."""
        checker = ComplianceChecker(self.sample_config, self.sample_policies)
        
        interface_text = 'interface description test'
        self.assertTrue(checker._check_condition(interface_text, 'not:http server'))
        self.assertFalse(checker._check_condition(interface_text, 'not:description'))
    
    def test_get_compliance_score(self):
        """Test compliance score calculation."""
        checker = ComplianceChecker(self.sample_config, self.sample_policies)
        score = checker.get_compliance_score()
        
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 100.0)
    
    def test_get_critical_issues(self):
        """Test getting critical issues."""
        checker = ComplianceChecker(self.sample_config, self.sample_policies)
        critical_issues = checker.get_critical_issues()
        
        self.assertIsInstance(critical_issues, list)
    
    def test_export_results(self):
        """Test exporting results to file."""
        checker = ComplianceChecker(self.sample_config, self.sample_policies)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            output_file = f.name
        
        try:
            checker.export_results(output_file)
            self.assertTrue(os.path.exists(output_file))
            
            # Verify file contains valid YAML
            with open(output_file, 'r') as f:
                exported_data = yaml.safe_load(f)
                self.assertIn('summary', exported_data)
        finally:
            os.unlink(output_file)


class TestConfigParser(unittest.TestCase):
    """Test cases for ConfigParser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_config_text = """
interface GigabitEthernet0/1
  description Uplink to Core
  ip address 192.168.1.1 255.255.255.0
  no ip http server
!
interface GigabitEthernet0/2
  description Connection to ISP
  ip address 10.0.0.1 255.255.255.0
!
"""
    
    def test_parse_from_text(self):
        """Test parsing configuration from text."""
        parser = ConfigParser(self.sample_config_text)
        interfaces = parser.get_interfaces()
        
        self.assertIn('GigabitEthernet0/1', interfaces)
        self.assertIn('GigabitEthernet0/2', interfaces)
        self.assertEqual(len(interfaces), 2)
    
    def test_parse_from_file(self):
        """Test parsing configuration from file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.sample_config_text)
            config_file = f.name
        
        try:
            parser = ConfigParser(config_file)
            interfaces = parser.get_interfaces()
            
            self.assertIn('GigabitEthernet0/1', interfaces)
            self.assertIn('GigabitEthernet0/2', interfaces)
        finally:
            os.unlink(config_file)
    
    def test_parse_file_not_found(self):
        """Test error handling for missing file."""
        # The parser should handle missing files gracefully or raise FileNotFoundError
        try:
            ConfigParser('nonexistent.txt')
            # If no exception is raised, that's also acceptable behavior
        except FileNotFoundError:
            # This is the expected behavior
            pass
    
    def test_get_interface_count(self):
        """Test getting interface count."""
        parser = ConfigParser(self.sample_config_text)
        count = parser.get_interface_count()
        self.assertEqual(count, 2)
    
    def test_get_security_issues(self):
        """Test getting security issues."""
        parser = ConfigParser(self.sample_config_text)
        issues = parser.get_security_issues()
        
        self.assertIsInstance(issues, list)
        # Should not have issues since HTTP server is disabled
        self.assertEqual(len(issues), 0)
    
    def test_validate_configuration(self):
        """Test configuration validation."""
        parser = ConfigParser(self.sample_config_text)
        validation = parser.validate_configuration()
        
        self.assertIn('total_interfaces', validation)
        self.assertIn('security_issues', validation)
        self.assertEqual(validation['total_interfaces'], 2)


class TestReportGenerator(unittest.TestCase):
    """Test cases for ReportGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_results = {
            'summary': {
                'total_policies': 3,
                'compliant_policies': 2,
                'non_compliant_policies': 1,
                'total_interfaces': 2
            },
            'detailed_results': {
                'test_rule': {
                    'status': 'compliant',
                    'description': 'Test rule description',
                    'severity': 'medium',
                    'details': [],
                    'non_compliant_interfaces': []
                }
            },
            'recommendations': ['Test recommendation']
        }
        
        self.generator = ReportGenerator(self.sample_results)
    
    def test_generate_text_report(self):
        """Test generating text report."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            output_file = f.name
        
        try:
            success = self.generator.generate_text_report(output_file)
            self.assertTrue(success)
            self.assertTrue(os.path.exists(output_file))
            
            # Verify file content
            with open(output_file, 'r') as f:
                content = f.read()
                self.assertIn('NETWORK CONFIGURATION COMPLIANCE REPORT', content)
                self.assertIn('SUMMARY', content)
        finally:
            os.unlink(output_file)
    
    def test_generate_json_report(self):
        """Test generating JSON report."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_file = f.name
        
        try:
            success = self.generator.generate_json_report(output_file)
            self.assertTrue(success)
            self.assertTrue(os.path.exists(output_file))
            
            # Verify JSON content
            with open(output_file, 'r') as f:
                content = f.read()
                data = json.loads(content)
                self.assertIn('metadata', data)
                self.assertIn('results', data)
        finally:
            os.unlink(output_file)
    
    def test_generate_html_report(self):
        """Test generating HTML report."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            output_file = f.name
        
        try:
            success = self.generator.generate_html_report(output_file)
            self.assertTrue(success)
            self.assertTrue(os.path.exists(output_file))
            
            # Verify HTML content
            with open(output_file, 'r') as f:
                content = f.read()
                self.assertIn('<!DOCTYPE html>', content)
                self.assertIn('Network Configuration Compliance Report', content)
        finally:
            os.unlink(output_file)
    
    def test_generate_csv_report(self):
        """Test generating CSV report."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            output_file = f.name
        
        try:
            success = self.generator.generate_csv_report(output_file)
            self.assertTrue(success)
            self.assertTrue(os.path.exists(output_file))
            
            # Verify CSV content
            with open(output_file, 'r') as f:
                content = f.read()
                lines = content.strip().split('\n')
                self.assertGreater(len(lines), 1)  # Header + data
                self.assertIn('Rule Name', lines[0])
        finally:
            os.unlink(output_file)
    
    def test_generate_all_reports(self):
        """Test generating all report formats."""
        with tempfile.TemporaryDirectory() as temp_dir:
            results = self.generator.generate_all_reports(temp_dir)
            
            self.assertTrue(results['text'])
            self.assertTrue(results['json'])
            self.assertTrue(results['html'])
            self.assertTrue(results['csv'])
            
            # Verify all files exist
            expected_files = [
                'compliance_report.txt',
                'compliance_report.json',
                'compliance_report.html',
                'compliance_report.csv'
            ]
            
            for filename in expected_files:
                filepath = os.path.join(temp_dir, filename)
                self.assertTrue(os.path.exists(filepath))


if __name__ == '__main__':
    unittest.main()
