#!/usr/bin/env python3
"""
Network Configuration Compliance Checker - Main Entry Point

A tool that checks router/switch configurations against predefined security policies
and best practices.
"""

import argparse
import logging
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any

from parser import ConfigParser
from compliance_checker import ComplianceChecker
from report_generator import ReportGenerator


class NetworkConfigChecker:
    """Main application class for network configuration compliance checking."""
    
    def __init__(self, config_file: str, policy_file: str, output_dir: str = "reports"):
        """
        Initialize the network configuration checker.
        
        Args:
            config_file: Path to the configuration file
            policy_file: Path to the policy file
            output_dir: Directory for output reports
        """
        self.config_file = config_file
        self.policy_file = policy_file
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Initialize components
        self.parser = None
        self.checker = None
        self.report_generator = None
        
    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.output_dir / 'checker.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def validate_files(self) -> bool:
        """Validate that input files exist and are readable."""
        try:
            if not os.path.exists(self.config_file):
                self.logger.error(f"Configuration file not found: {self.config_file}")
                return False
                
            if not os.path.exists(self.policy_file):
                self.logger.error(f"Policy file not found: {self.policy_file}")
                return False
                
            self.logger.info(f"Validated input files: {self.config_file}, {self.policy_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating files: {e}")
            return False
    
    def parse_configuration(self) -> bool:
        """Parse the network configuration file."""
        try:
            self.logger.info(f"Parsing configuration file: {self.config_file}")
            self.parser = ConfigParser(self.config_file)
            interfaces = self.parser.get_interfaces()
            self.logger.info(f"Parsed {len(interfaces)} interfaces")
            return True
            
        except Exception as e:
            self.logger.error(f"Error parsing configuration: {e}")
            return False
    
    def check_compliance(self) -> Optional[Dict[str, Any]]:
        """Check compliance against policies."""
        try:
            self.logger.info(f"Checking compliance against policies: {self.policy_file}")
            self.checker = ComplianceChecker(self.parser.get_interfaces(), self.policy_file)
            results = self.checker.check_compliance()
            self.logger.info(f"Compliance check completed with {len(results)} rules")
            return results
            
        except Exception as e:
            self.logger.error(f"Error checking compliance: {e}")
            return None
    
    def generate_reports(self, compliance_results: Dict[str, Any]) -> bool:
        """Generate compliance reports."""
        try:
            self.logger.info("Generating compliance reports")
            self.report_generator = ReportGenerator(compliance_results)
            
            # Generate text report
            text_report_path = self.output_dir / "compliance_report.txt"
            self.report_generator.generate_text_report(str(text_report_path))
            self.logger.info(f"Text report generated: {text_report_path}")
            
            # Generate JSON report
            json_report_path = self.output_dir / "compliance_report.json"
            self.report_generator.generate_json_report(str(json_report_path))
            self.logger.info(f"JSON report generated: {json_report_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error generating reports: {e}")
            return False
    
    def run(self) -> bool:
        """Run the complete compliance checking workflow."""
        self.logger.info("Starting network configuration compliance check")
        
        # Validate input files
        if not self.validate_files():
            return False
        
        # Parse configuration
        if not self.parse_configuration():
            return False
        
        # Check compliance
        compliance_results = self.check_compliance()
        if compliance_results is None:
            return False
        
        # Generate reports
        if not self.generate_reports(compliance_results):
            return False
        
        self.logger.info("Compliance check completed successfully")
        return True


def main():
    """Main entry point with CLI interface."""
    parser = argparse.ArgumentParser(
        description="Network Configuration Compliance Checker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -c config.txt -p policies.yaml
  %(prog)s -c config.txt -p policies.yaml -o custom_reports
  %(prog)s -c config.txt -p policies.yaml --verbose
        """
    )
    
    parser.add_argument(
        "-c", "--config",
        required=True,
        help="Path to network configuration file"
    )
    
    parser.add_argument(
        "-p", "--policy",
        required=True,
        help="Path to policy file (YAML format)"
    )
    
    parser.add_argument(
        "-o", "--output",
        default="reports",
        help="Output directory for reports (default: reports)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Setup logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create and run checker
    checker = NetworkConfigChecker(args.config, args.policy, args.output)
    
    try:
        success = checker.run()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
