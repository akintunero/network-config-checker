class ConfigParser:
    def __init__(self, config_text):
        self.config_text = config_text
        self.interfaces = self.parse_interfaces()

    def parse_interfaces(self):
        """Parses interfaces from the configuration text."""
        interfaces = {}
        current_interface = None

        for line in self.config_text.splitlines():
            line = line.strip()
            if line.startswith("interface"):
                current_interface = line.split()[1]
                interfaces[current_interface] = []
            elif current_interface:
                interfaces[current_interface].append(line)

        return interfaces

    def get_interfaces(self):
        """Returns the parsed interface configurations."""
        return self.interfaces
