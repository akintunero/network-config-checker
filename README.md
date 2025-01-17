# Network Configuration Compliance Checker

_A tool to analyze router and switch configurations for compliance with security policies and best practices._

---

##  Features

- Parse network device configurations  
- Validate configurations against security policies  
- Generate compliance reports (Text & JSON)  
- Support for multi-vendor devices (Cisco, Juniper, etc.)  
- CLI tool for ease of use  
- Future enhancements: Real-time monitoring, Web UI  

---

##  Installation

###  Clone the Repository

```
git clone https://github.com/akintunero/network-config-checker.git
cd network-config-checker
```

###  Create a Virtual Environment (Recommended)

```
python -m venv venv

source venv/bin/activate  # For macOS/Linux

venv\Scripts\activate     # For Windows
```

###  Install Dependencies

```
pip install -r requirements.txt
```

---

##  Usage

###  Running the Compliance Checker

```
python src/main.py --config config_samples/sample_config.txt --policy policies/security_policies.yaml
```

###  Example Configuration File (config_samples/sample_config.txt)

```
interface GigabitEthernet0/1
  description Uplink to Core
  ip address 192.168.1.1 255.255.255.0
  no shutdown
```

###  Example Policy File (policies/security_policies.yaml)

```
interface_security:
  conditions:
    - "no shutdown"
    - "description"
```

###  Running Tests

```
pytest tests/
```

---

##  Using with Network Devices

###  Fetch Configuration from a Cisco Router

```
python src/live_monitor.py --device cisco_router --ip 192.168.1.1 --username admin --password secret
```

###  Fetch Configuration from a Juniper Switch

```
python src/live_monitor.py --device juniper_switch --ip 192.168.2.1 --username admin --password secret
```

---

##  License

This project is licensed under the MIT License. 

---

##  Contributing

Contributions are welcome! Please open an issue or submit a pull request.
