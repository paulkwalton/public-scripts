import os
import openai
import subprocess
import requests

def run_program(command_line):
    command = command_line.split()
    result = subprocess.check_output(command, text=True)
    return result

def send_to_chatgpt(program_output):
    openai.api_key = 'ENTER KEY'
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a helpful assistant."}, 
                  {"role": "user", "content": f"Analyse the output data and provide a commentary. This is for a security team, view through the eyes of an adversary looking for a weakness.:\n{program_output}"}],
        max_tokens=1024
    )
    
    analysis = response.choices[0].message['content']
    return analysis

def post_to_discord(content):
    DISCORD_WEBHOOK_URL = 'ENTER WEBHOOK'
    
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
    command_line = input("Enter the full command to run (e.g. 'nmap -sS -sV -sC 192.168.1.1'): ")
    program_output = run_program(command_line)
    print("Command output:", program_output)
    analysis = send_to_chatgpt(program_output)
    print("Analysis from OpenAI:", analysis)
    post_to_discord(analysis)
