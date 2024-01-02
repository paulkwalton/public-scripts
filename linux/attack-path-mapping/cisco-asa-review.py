import re

def parse_object_groups(file_path):
    object_groups = {}
    current_group = None

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith("object-group network"):
                current_group = line.split()[2]
                object_groups[current_group] = []
            elif line.startswith("network-object") and current_group:
                _, network = line.split(maxsplit=1)
                object_groups[current_group].append(network)
            elif line == "!":  # End of current object group
                current_group = None

    return object_groups

def parse_cisco_asa_config(file_path, object_groups):
    remote_mgmt_rules = []
    mgmt_protocols = {
        'RDP': ['3389', 'rdp'],
        'HTTP': ['80', 'http'],
        'HTTPS': ['443', 'https'],
        'VNC': ['5900', 'vnc'],
        'PCAnywhere': ['5631', 'pcanywhere'],
        'SSH': ['22', 'ssh'],
        'Telnet': ['23', 'telnet'],
        'Login': ['513', 'login']
    }

    with open(file_path, 'r') as file:
        for line in file:
            line_lower = line.lower()
            if 'extended' in line_lower:
                for protocol, patterns in mgmt_protocols.items():
                    for pattern in patterns:
                        if re.search(r'\b' + pattern + r'\b', line_lower):
                            source, destination = extract_source_destination(line)
                            source_details = object_groups.get(source, [source])
                            destination_details = object_groups.get(destination, [destination])
                            attack_path = check_attack_path(source_details)
                            remote_mgmt_rules.append((protocol, line.strip(), source_details, destination_details, attack_path))
                            break

    return remote_mgmt_rules

def extract_source_destination(rule):
    # Updated regex to match both direct object and object-group references
    match = re.search(r'extended (permit|deny) (tcp|udp) (object-group (\S+)|object (\S+)|(\S+)) (object-group (\S+)|object (\S+)|(\S+))', rule)
    if match:
        source = match.group(4) or match.group(5) or match.group(6)
        destination = match.group(8) or match.group(9) or match.group(10)
        return source, destination
    return '', ''

def check_attack_path(source_details):
    for detail in source_details:
        if "blan" in detail or "enterprise" in detail:
            return "Yes"
    return "No"

def generate_html_table(remote_mgmt_rules):
    html = '''
    <html>
    <head>
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
        }
        th {
            background-color: #f2f2f2;
        }
        tr:nth-child(even) {background-color: #f2f2f2;}
    </style>
    </head>
    <body>
        <table>
            <tr>
                <th>Protocol</th>
                <th>Action</th>
                <th>Source</th>
                <th>Destination</th>
                <th>Rule</th>
                <th>Attack Path from enterprise</th>
            </tr>
    '''

    for protocol, rule, source_details, destination_details, attack_path in remote_mgmt_rules:
        html += f'''
            <tr>
                <td>{protocol}</td>
                <td>{rule.split()[2]}</td>
                <td>{"<br>".join(source_details)}</td>
                <td>{"<br>".join(destination_details)}</td>
                <td>{rule}</td>
                <td>{attack_path}</td>
            </tr>
        '''

    html += '''
        </table>
    </body>
    </html>
    '''

    return html

# Main script execution
asa_config_path = input("Enter the path to your ASA config file: ")
object_groups = parse_object_groups(asa_config_path)
remote_mgmt_rules = parse_cisco_asa_config(asa_config_path, object_groups)
html_output = generate_html_table(remote_mgmt_rules)

# Write the HTML output to a file
output_file = 'asa_rules_output.html'
with open(output_file, 'w') as file:
    file.write(html_output)

print(f"Output written to {output_file}")
