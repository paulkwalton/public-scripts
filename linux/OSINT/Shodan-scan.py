import shodan

def search_shodan(api_key, keywords):
    api = shodan.Shodan(api_key)

    for keyword in keywords:
        print(f"\nSearching for {keyword}...\n")

        try:
            results = api.search(keyword)
            print(f"Results found for {keyword}: {results['total']}\n")

            # Print table header
            print(f"{ 'IP Address':<20} {'Hostname':<50} {'Port':<10} {'Shodan URL':<50}")
            print("=" * 120)

            # Collect and sort the results
            sorted_results = sorted(results['matches'], key=lambda k: k.get('ip_str', ''))

            for result in sorted_results:
                ip = result.get('ip_str', 'N/A')
                hostname_list = result.get('hostnames', ['N/A'])
                hostname = hostname_list[0] if hostname_list else 'N/A'
                ports = result.get('port', 'N/A')
                shodan_url = f"https://www.shodan.io/host/{ip}"

                # Print table row
                print(f"{ip:<20} {hostname:<50} {ports:<10} {shodan_url:<50}")

        except shodan.APIError as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    API_KEY = "<ENTER HERE>"  # Replace with your Shodan API key
    
    # Collect keywords from the user
    KEYWORDS = []
    while True:
        keyword = input("Enter a keyword to search for (or 'q' to quit): ")
        if keyword.lower() == 'q':
            break
        KEYWORDS.append(keyword)

    if KEYWORDS:
        search_shodan(API_KEY, KEYWORDS)
    else:
        print("No keywords entered. Exiting.")
