#!/usr/bin/env python3
"""
Network Configuration Parser

Parses network device configurations from various vendors and extracts
interface configurations, security settings, and other relevant information.
"""

import os
import re
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path


class ConfigParser:
    """Parser for network device configurations from multiple vendors."""
    
    def __init__(self, config_source: str):
        """
        Initialize the configuration parser.
        
        Args:
            config_source: Path to configuration file or configuration text
        """
        self.logger = logging.getLogger(__name__)
        self.config_text = self._load_config(config_source)
        self.interfaces = {}
        self.security_settings = {}
        self.vlan_configs = {}
        self.routing_configs = {}
        
        # Parse the configuration
        self._parse_configuration()
    
    def _load_config(self, config_source: str) -> str:
        """Load configuration from file or text."""
        try:
            if os.path.isfile(config_source):
                with open(config_source, 'r', encoding='utf-8') as file:
                    content = file.read()
                self.logger.info(f"Loaded configuration from file: {config_source}")
            else:
                content = config_source
                self.logger.info("Loaded configuration from text input")
            
            return content
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_source}")
        except Exception as e:
            raise ValueError(f"Error loading configuration: {e}")
    
    def _parse_configuration(self):
        """Parse the complete configuration."""
        lines = self.config_text.splitlines()
        
        # Parse different sections
        self._parse_interfaces(lines)
        self._parse_security_settings(lines)
        self._parse_vlan_configurations(lines)
        self._parse_routing_configurations(lines)
        
        self.logger.info(f"Parsed configuration: {len(self.interfaces)} interfaces, "
                        f"{len(self.security_settings)} security settings")
    
    def _parse_interfaces(self, lines: List[str]):
        """Parse interface configurations."""
        current_interface = None
        current_interface_config = []
        
        for line in lines:
            line = line.strip()
            
            # Detect interface start
            if self._is_interface_start(line):
                # Save previous interface if exists
                if current_interface:
                    self.interfaces[current_interface] = current_interface_config
                
                # Start new interface
                current_interface = self._extract_interface_name(line)
                current_interface_config = [line]
                
            # Detect interface end
            elif self._is_interface_end(line):
                if current_interface:
                    current_interface_config.append(line)
                    self.interfaces[current_interface] = current_interface_config
                    current_interface = None
                    current_interface_config = []
                    
            # Add line to current interface
            elif current_interface and line:
                current_interface_config.append(line)
        
        # Save last interface if exists
        if current_interface:
            self.interfaces[current_interface] = current_interface_config
    
    def _parse_security_settings(self, lines: List[str]):
        """Parse security-related configurations."""
        security_patterns = [
            r'no\s+ip\s+http\s+server',
            r'no\s+ip\s+http\s+secure-server',
            r'service\s+password-encryption',
            r'enable\s+secret',
            r'username\s+\w+\s+privilege',
            r'access-list',
            r'ip\s+access-group',
            r'crypto\s+key',
            r'ssh\s+version',
            r'line\s+vty',
            r'login\s+local',
            r'no\s+service\s+pad',
            r'no\s+service\s+tcp-small-servers',
            r'no\s+service\s+udp-small-servers'
        ]
        
        for line in lines:
            line = line.strip()
            for pattern in security_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    setting_type = self._categorize_security_setting(line)
                    if setting_type not in self.security_settings:
                        self.security_settings[setting_type] = []
                    self.security_settings[setting_type].append(line)
                    break
    
    def _parse_vlan_configurations(self, lines: List[str]):
        """Parse VLAN configurations."""
        vlan_pattern = r'vlan\s+(\d+)'
        vlan_name_pattern = r'name\s+(.+)'
        
        current_vlan = None
        
        for line in lines:
            line = line.strip()
            
            # Detect VLAN start
            vlan_match = re.search(vlan_pattern, line, re.IGNORECASE)
            if vlan_match:
                current_vlan = vlan_match.group(1)
                self.vlan_configs[current_vlan] = {'config': [line]}
                
            # Detect VLAN name
            elif current_vlan and re.search(vlan_name_pattern, line, re.IGNORECASE):
                name_match = re.search(vlan_name_pattern, line, re.IGNORECASE)
                if name_match:
                    self.vlan_configs[current_vlan]['name'] = name_match.group(1)
                self.vlan_configs[current_vlan]['config'].append(line)
                
            # Add other VLAN config lines
            elif current_vlan and line and not line.startswith('!'):
                self.vlan_configs[current_vlan]['config'].append(line)
                
            # End VLAN section
            elif line == '!' and current_vlan:
                current_vlan = None
    
    def _parse_routing_configurations(self, lines: List[str]):
        """Parse routing configurations."""
        routing_patterns = [
            r'router\s+(\w+)',
            r'ip\s+route',
            r'network\s+\d+\.\d+\.\d+\.\d+',
            r'default-information\s+originate',
            r'redistribute\s+\w+'
        ]
        
        current_routing_protocol = None
        
        for line in lines:
            line = line.strip()
            
            # Detect routing protocol start
            router_match = re.search(r'router\s+(\w+)', line, re.IGNORECASE)
            if router_match:
                current_routing_protocol = router_match.group(1)
                self.routing_configs[current_routing_protocol] = [line]
                
            # Add routing config lines
            elif current_routing_protocol and line and not line.startswith('!'):
                self.routing_configs[current_routing_protocol].append(line)
                
            # End routing section
            elif line == '!' and current_routing_protocol:
                current_routing_protocol = None
    
    def _is_interface_start(self, line: str) -> bool:
        """Check if line indicates interface start."""
        interface_patterns = [
            r'^interface\s+',
            r'^interface-port\s+',
            r'^interface\s+ethernet\s+',
            r'^interface\s+fastethernet\s+',
            r'^interface\s+gigabitethernet\s+',
            r'^interface\s+serial\s+',
            r'^interface\s+loopback\s+',
            r'^interface\s+port-channel\s+',
            r'^interface\s+vlan\s+'
        ]
        
        return any(re.search(pattern, line, re.IGNORECASE) for pattern in interface_patterns)
    
    def _is_interface_end(self, line: str) -> bool:
        """Check if line indicates interface end."""
        return line == '!' or line.startswith('exit')
    
    def _extract_interface_name(self, line: str) -> str:
        """Extract interface name from interface line."""
        # Remove 'interface' keyword and get the interface name
        interface_name = line.replace('interface', '').strip()
        return interface_name
    
    def _categorize_security_setting(self, line: str) -> str:
        """Categorize security settings."""
        line_lower = line.lower()
        
        if 'http' in line_lower:
            return 'http_security'
        elif 'password' in line_lower or 'secret' in line_lower:
            return 'password_security'
        elif 'access-list' in line_lower:
            return 'access_control'
        elif 'crypto' in line_lower or 'ssh' in line_lower:
            return 'encryption'
        elif 'service' in line_lower:
            return 'service_security'
        elif 'line' in line_lower:
            return 'line_security'
        else:
            return 'other_security'
    
    def get_interfaces(self) -> Dict[str, List[str]]:
        """Get parsed interface configurations."""
        return self.interfaces
    
    def get_security_settings(self) -> Dict[str, List[str]]:
        """Get parsed security settings."""
        return self.security_settings
    
    def get_vlan_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get parsed VLAN configurations."""
        return self.vlan_configs
    
    def get_routing_configs(self) -> Dict[str, List[str]]:
        """Get parsed routing configurations."""
        return self.routing_configs
    
    def get_interface_count(self) -> int:
        """Get the number of interfaces found."""
        return len(self.interfaces)
    
    def get_security_issues(self) -> List[str]:
        """Identify potential security issues in the configuration."""
        issues = []
        
        # Check for common security misconfigurations
        for interface, config in self.interfaces.items():
            config_text = ' '.join(config).lower()
            
            # Check for missing descriptions
            if 'description' not in config_text:
                issues.append(f"Interface {interface}: Missing description")
            
            # Check for HTTP server enabled
            if 'ip http server' in config_text and 'no ip http server' not in config_text:
                issues.append(f"Interface {interface}: HTTP server enabled")
            
            # Check for telnet enabled
            if 'transport input telnet' in config_text:
                issues.append(f"Interface {interface}: Telnet enabled (use SSH instead)")
        
        return issues
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate the configuration for common issues."""
        validation_results = {
            'total_interfaces': len(self.interfaces),
            'total_vlans': len(self.vlan_configs),
            'total_routing_protocols': len(self.routing_configs),
            'security_issues': self.get_security_issues(),
            'has_security_settings': len(self.security_settings) > 0,
            'has_vlan_configs': len(self.vlan_configs) > 0,
            'has_routing_configs': len(self.routing_configs) > 0
        }
        
        return validation_results
