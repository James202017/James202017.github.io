# PowerShell script for running all bots without Docker
# Usage: .\start_bots.ps1 [-Mode development|production] [-WebServer] [-Monitor]

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("development", "production")]
    [string]$Mode = "development",
    
    [Parameter(Mandatory=$false)]
    [switch]$WebServer = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$Monitor = $false
)

# Global variables
$global:LogFile = "logs\bot_startup_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
$global:ProcessIds = @()
$global:BotStatuses = @{}

# Logging functions
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    Write-Host $logMessage
    Add-Content -Path $global:LogFile -Value $logMessage -Encoding UTF8
}

function Write-Success {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Green
    Write-Log $Message "SUCCESS"
}

function Write-Warning {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Yellow
    Write-Log $Message "WARNING"
}

function Write-Error {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Red
    Write-Log $Message "ERROR"
}

# Check prerequisites
function Test-Prerequisites {
    Write-Log "Checking prerequisites..."
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Python found: $pythonVersion"
        } else {
            throw "Python not found"
        }
    } catch {
        Write-Error "Python is not installed or not in PATH"
        return $false
    }
    
    # Check pip
    try {
        $pipVersion = pip --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Pip found: $pipVersion"
        } else {
            throw "Pip not found"
        }
    } catch {
        Write-Error "Pip is not installed or not in PATH"
        return $false
    }
    
    return $true
}

# Install dependencies
function Install-Dependencies {
    Write-Log "Installing Python dependencies..."
    
    if (Test-Path "requirements.txt") {
        try {
            pip install -r requirements.txt
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Dependencies installed successfully"
                return $true
            } else {
                throw "Pip install failed"
            }
        } catch {
            Write-Error "Failed to install dependencies: $($_.Exception.Message)"
            return $false
        }
    } else {
        Write-Warning "requirements.txt not found, skipping dependency installation"
        return $true
    }
}

# Create necessary directories
function Initialize-Directories {
    Write-Log "Creating necessary directories..."
    
    $directories = @("logs", "data", "temp")
    
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            try {
                New-Item -ItemType Directory -Path $dir -Force | Out-Null
                Write-Success "Created directory: $dir"
            } catch {
                Write-Error "Failed to create directory ${dir}: $($_.Exception.Message)"
                return $false
            }
        } else {
            Write-Log "Directory already exists: $dir"
        }
    }
    
    return $true
}

# Stop existing processes
function Stop-ExistingProcesses {
    Write-Log "Stopping existing bot processes..."
    
    try {
        $pythonProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue
        if ($pythonProcesses) {
            $pythonProcesses | Where-Object { $_.CommandLine -like "*BOT_*.py*" } | Stop-Process -Force
            Write-Success "Stopped existing bot processes"
        } else {
            Write-Log "No existing Python processes found"
        }
    } catch {
        Write-Warning "Error stopping processes: $($_.Exception.Message)"
    }
    
    Start-Sleep -Seconds 2
}

# Start individual bot
function Start-Bot {
    param(
        [string]$BotScript,
        [string]$BotName
    )
    
    Write-Log "Starting bot: $BotName ($BotScript)"
    
    if (-not (Test-Path $BotScript)) {
        Write-Error "Bot script not found: $BotScript"
        $global:BotStatuses[$BotName] = "FAILED - Script not found"
        return $false
    }
    
    try {
        if ($Mode -eq "development") {
            # Development mode - start in new window
            $process = Start-Process -FilePath "python" -ArgumentList $BotScript -WindowStyle Normal -PassThru
        } else {
            # Production mode - start hidden
            $process = Start-Process -FilePath "python" -ArgumentList $BotScript -WindowStyle Hidden -PassThru
        }
        
        if ($process) {
            $global:ProcessIds += $process.Id
            $global:BotStatuses[$BotName] = "RUNNING (PID: $($process.Id))"
            Write-Success "Bot $BotName started successfully (PID: $($process.Id))"
            return $true
        } else {
            $global:BotStatuses[$BotName] = "FAILED - Process not created"
            Write-Error "Failed to start bot: $BotName"
            return $false
        }
    } catch {
        $global:BotStatuses[$BotName] = "FAILED - $($_.Exception.Message)"
        Write-Error "Error starting bot ${BotName}: $($_.Exception.Message)"
        return $false
    }
}

# Start web server
function Start-WebServer {
    if (-not $WebServer) {
        return $true
    }
    
    Write-Log "Starting web server..."
    
    if (-not (Test-Path "web\index.html")) {
        Write-Warning "Web interface not found, skipping web server"
        return $true
    }
    
    try {
        # Simple HTTP server using Python
        if ($Mode -eq "development") {
            $webProcess = Start-Process -FilePath "python" -ArgumentList "-m", "http.server", "8080", "--directory", "web" -WindowStyle Normal -PassThru
        } else {
            $webProcess = Start-Process -FilePath "python" -ArgumentList "-m", "http.server", "8080", "--directory", "web" -WindowStyle Hidden -PassThru
        }
        
        if ($webProcess) {
            $global:ProcessIds += $webProcess.Id
            Write-Success "Web server started on http://localhost:8080 (PID: $($webProcess.Id))"
            return $true
        } else {
            Write-Error "Failed to start web server"
            return $false
        }
    } catch {
        Write-Error "Error starting web server: $($_.Exception.Message)"
        return $false
    }
}

# Monitor bot processes
function Start-Monitoring {
    if (-not $Monitor) {
        return
    }
    
    Write-Log "Starting monitoring..."
    
    # Create monitoring script
    $monitorScript = @"
# Bot monitoring script
while (`$true) {
    Clear-Host
    Write-Host "=== Bot Status Monitor ===" -ForegroundColor Cyan
    Write-Host "Time: `$(Get-Date)" -ForegroundColor Gray
    Write-Host ""
    
    foreach (`$processId in @($($global:ProcessIds -join ', '))) {
         try {
             `$process = Get-Process -Id `$processId -ErrorAction Stop
             Write-Host "PID `$processId : RUNNING - `$(`$process.ProcessName)" -ForegroundColor Green
         } catch {
             Write-Host "PID `$processId : STOPPED" -ForegroundColor Red
         }
     }
    
    Write-Host ""
    Write-Host "Press Ctrl+C to stop monitoring" -ForegroundColor Yellow
    Start-Sleep -Seconds 5
}
"@
    
    $monitorScript | Out-File -FilePath "temp\monitor.ps1" -Encoding UTF8
    
    if ($Mode -eq "development") {
        Start-Process -FilePath "powershell" -ArgumentList "-ExecutionPolicy", "Bypass", "-File", "temp\monitor.ps1" -WindowStyle Normal
    }
}

# Test bot status
function Test-BotsStatus {
    Write-Log "Testing bot status..."
    
    Start-Sleep -Seconds 3  # Wait for bots to initialize
    
    foreach ($processId in $global:ProcessIds) {
         try {
             $process = Get-Process -Id $processId -ErrorAction Stop
             Write-Success "Process $processId is running: $($process.ProcessName)"
         } catch {
             Write-Warning "Process $processId is not running"
         }
     }
}

# Main function
function Start-AllBots {
    Write-Log "Starting bot deployment in $Mode mode..."
    Write-Log "Web Server: $WebServer, Monitor: $Monitor"
    
    # Prerequisites check
    if (-not (Test-Prerequisites)) {
        Write-Error "Prerequisites check failed"
        exit 1
    }
    
    # Install dependencies
    if (-not (Install-Dependencies)) {
        Write-Error "Dependency installation failed"
        exit 1
    }
    
    # Initialize directories
    if (-not (Initialize-Directories)) {
        Write-Error "Directory initialization failed"
        exit 1
    }
    
    # Stop existing processes
    Stop-ExistingProcesses
    
    # Bot list
    $bots = @(
        @{ Script = "bots\BOT_P.py"; Name = "BOT_P" },
        @{ Script = "bots\BOT_PR.py"; Name = "BOT_PR" },
        @{ Script = "bots\BOT_Inv.py"; Name = "BOT_Inv" },
        @{ Script = "bots\BOT_Str.py"; Name = "BOT_Str" },
        @{ Script = "bots\BOT_Ocenka.py"; Name = "BOT_Ocenka" }
    )
    
    # Start bots
    $successCount = 0
    foreach ($bot in $bots) {
        if (Start-Bot -BotScript $bot.Script -BotName $bot.Name) {
            $successCount++
        }
        Start-Sleep -Seconds 1  # Small delay between starts
    }
    
    # Start web server
    Start-WebServer
    
    # Start monitoring
    Start-Monitoring
    
    # Check status
    Test-BotsStatus
    
    Write-Success "Startup completed. Successfully started bots: $successCount of $($bots.Count)"
    
    if ($Mode -eq "development") {
        Write-Log "In development mode, bots are running in separate windows"
    } else {
        Write-Log "In production mode, bots are running in background"
    }
    
    Write-Log "Logs are saved to 'logs' folder"
    Write-Log "To stop all bots use: Stop-Process -Name python -Force"
    
    # Display status summary
    Write-Host ""
    Write-Host "=== Bot Status Summary ===" -ForegroundColor Cyan
    foreach ($botName in $global:BotStatuses.Keys) {
        $status = $global:BotStatuses[$botName]
        if ($status -like "*RUNNING*") {
            Write-Host "$botName : $status" -ForegroundColor Green
        } else {
            Write-Host "$botName : $status" -ForegroundColor Red
        }
    }
    Write-Host ""
}

# Error handling
trap {
    Write-Error "Critical error: $($_.Exception.Message)"
    exit 1
}

# Main execution
try {
    Start-AllBots
} catch {
    Write-Error "Error during bot startup: $($_.Exception.Message)"
    exit 1
}