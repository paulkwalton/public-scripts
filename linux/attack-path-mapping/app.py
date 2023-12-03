import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Function to add nodes and edges to the graph
def add_nodes_and_edges(G, source, targets, firewall_present, attacker=None):
    G.add_node(source['hostname'], environment='Enterprise', ip=source['ip'])
    
    for target in targets:
        G.add_node(target['hostname'], environment='Layer 3', ip=target['ip'])
        edge_label = f"Ports: {', '.join(target['ports'])}"
        if target['exploits']:
            edge_label += f"\nExploits: {', '.join(target['exploits'])}"
        if firewall_present:
            G.add_node('Firewall', environment='DMZ')
            G.add_edge(source['hostname'], 'Firewall', label='Firewall to DMZ')
            G.add_edge('Firewall', target['hostname'], label=edge_label)
        else:
            G.add_edge(source['hostname'], target['hostname'], label=edge_label)

    if attacker:
        G.add_node(attacker['hostname'], environment='Enterprise', ip=attacker['ip'])
        attack_label = f"Ports: {', '.join(attacker['ports'])}\nExploits: {', '.join(attacker['exploits'])}"
        G.add_edge(attacker['hostname'], source['hostname'], label=attack_label)

# Function to draw the graph with color coding and key
def draw_graph(G):
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G)

    node_color = [get_node_color(G.nodes[node]['environment']) for node in G.nodes]
    nx.draw_networkx_nodes(G, pos, node_color=node_color)
    nx.draw_networkx_edges(G, pos)
    node_labels = {node: f"{node}\n({G.nodes[node].get('ip', 'N/A')})" for node in G.nodes}
    nx.draw_networkx_labels(G, pos, labels=node_labels)
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    create_legend()

    plt.title("Attack Path Mapping Diagram")
    plt.axis('off')
    plt.show()

# Helper function to determine node color based on environment
def get_node_color(environment):
    colors = {'Enterprise': 'skyblue', 'Layer 3': 'salmon', 'DMZ': 'gold'}
    return colors.get(environment, 'grey')

# Function to create legend for environments
def create_legend():
    legend_patches = [mpatches.Patch(color='skyblue', label='Enterprise'),
                      mpatches.Patch(color='salmon', label='Layer 3'),
                      mpatches.Patch(color='gold', label='DMZ')]
    plt.legend(handles=legend_patches, loc='upper left', bbox_to_anchor=(1, 1))

# Main program
def main():
    G = nx.DiGraph()

    source_ip = input("Enter the source IP: ")
    source_hostname = input("Enter the source Hostname: ")
    source = {'ip': source_ip, 'hostname': source_hostname}

    targets = []
    while True:
        target_ip = input("Enter a target IP (or leave blank to finish): ")
        if not target_ip: break
        target_hostname = input(f"Enter the hostname for {target_ip}: ")
        ports = input("Enter TCP/UDP ports (comma-separated): ").split(',')
        exploits = input("Enter CVEs or Exploits used (comma-separated, leave blank if none): ").split(',')
        targets.append({'ip': target_ip, 'hostname': target_hostname, 'ports': ports, 'exploits': exploits})

    firewall_present = input("Is there a firewall in front of the targets? (yes/no): ").lower() == 'yes'

    attacker = None
    if input("Do you want to add an attacker machine? (yes/no): ").lower() == 'yes':
        attacker_ip = input("Enter the attacker IP: ")
        attacker_hostname = input("Enter the attacker Hostname: ")
        attacker_ports = input("Enter the attacker TCP/UDP ports (comma-separated): ").split(',')
        attacker_exploits = input("Enter the attacker CVEs or Exploits used (comma-separated): ").split(',')
        attacker = {'ip': attacker_ip, 'hostname': attacker_hostname, 'ports': attacker_ports, 'exploits': attacker_exploits}

    add_nodes_and_edges(G, source, targets, firewall_present, attacker)
    draw_graph(G)

if __name__ == "__main__":
    main()
