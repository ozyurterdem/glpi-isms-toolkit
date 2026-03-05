<#
.SYNOPSIS
    Configure GLPI Agent server URL via Group Policy.

.DESCRIPTION
    Sets the GLPI Agent configuration to report to a specified GLPI server.
    Deploy via GPO as a startup/logon script for automated agent enrollment.

.PARAMETER ServerUrl
    The GLPI server URL (e.g., http://glpi.example.com)

.PARAMETER AgentTag
    Optional tag for agent identification

.EXAMPLE
    .\Set-GLPIAgentServer.ps1 -ServerUrl "http://glpi.example.com"

.NOTES
    Requires GLPI Agent to be installed on the target machine.
    Run as Administrator or via GPO.
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$ServerUrl,

    [Parameter(Mandatory = $false)]
    [string]$AgentTag = ""
)

$ErrorActionPreference = "Stop"

# ── Configuration ─────────────────────────────────────────────
$AgentConfigPath = "C:\Program Files\GLPI-Agent\etc\agent.cfg"
$AgentService = "GlpiAgent"
$LogFile = "C:\Windows\Temp\glpi-agent-setup.log"

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $Message" | Out-File -Append -FilePath $LogFile
    Write-Host $Message
}

# ── Verify agent is installed ─────────────────────────────────
if (-not (Test-Path $AgentConfigPath)) {
    Write-Log "ERROR: GLPI Agent not found at $AgentConfigPath"
    Write-Log "Install GLPI Agent first: https://glpi-agent.readthedocs.io/"
    exit 1
}

# ── Update configuration ─────────────────────────────────────
try {
    Write-Log "Configuring GLPI Agent to report to: $ServerUrl"

    $config = Get-Content $AgentConfigPath -Raw

    # Update or add server URL
    if ($config -match "server\s*=") {
        $config = $config -replace "server\s*=\s*.*", "server = $ServerUrl"
    } else {
        $config += "`nserver = $ServerUrl"
    }

    # Update or add tag if provided
    if ($AgentTag -ne "") {
        if ($config -match "tag\s*=") {
            $config = $config -replace "tag\s*=\s*.*", "tag = $AgentTag"
        } else {
            $config += "`ntag = $AgentTag"
        }
        Write-Log "Agent tag set to: $AgentTag"
    }

    $config | Set-Content -Path $AgentConfigPath -Force
    Write-Log "Configuration updated successfully."

    # ── Restart agent service ─────────────────────────────────
    $service = Get-Service -Name $AgentService -ErrorAction SilentlyContinue
    if ($service) {
        Restart-Service -Name $AgentService -Force
        Write-Log "GLPI Agent service restarted."
    } else {
        Write-Log "WARNING: Service '$AgentService' not found. Manual restart may be needed."
    }

    Write-Log "GLPI Agent configuration complete."
}
catch {
    Write-Log "ERROR: $($_.Exception.Message)"
    exit 1
}
