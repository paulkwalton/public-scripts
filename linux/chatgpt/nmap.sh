import os
import openai
import subprocess
import requests

def nmap_scan(target_ip, extensions):
    command = ['nmap'] + extensions.split() + [target_ip]
    scan_result = subprocess.check_output(command, text=True)
    return scan_result

def send_to_chatgpt(scan_data):
    openai.api_key = '<ENTER KEY>'
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a helpful assistant."}, 
                  {"role": "user", "content": f"Analyse the scan data from a pentester perspective, provide a detailed commentary on each port and how they could be exploited, highlight specific tools which can be used and the appropriate syntax to run them i.e crackmapexec, hydra, kerbrute etc. List hostname, IP address and criticality (i.e Critical if anonymous FTP is enabled, low if no exploitable ports are exposed) at top of the report.:\n{scan_data}"}],
        max_tokens=1024
    )
    
    analysis = response.choices[0].message['content']
    return analysis

def post_to_discord(content):
    DISCORD_WEBHOOK_URL = '<ENTER WEBHOOK>'
    
    # Split content into chunks of 2000 characters
    chunk_size = 2000
    content_chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
    
    for chunk in content_chunks:
        data = {
            "content": chunk
        }
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)
        if response.status_code != 204:
            raise ValueError(f"Request to Discord returned an error {response.status_code}, the response is:\n{response.text}")

if __name__ == "__main__":
    target = input("Enter target IP to scan: ")
    extensions = input("Enter nmap extensions (e.g. -sS -sV -sC): ")
    scan_data = nmap_scan(target, extensions)
    analysis = send_to_chatgpt(scan_data)
    post_to_discord(analysis)
