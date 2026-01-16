# TCO Dashboard Startup Script
# Run this script to start the dashboard and open it in your browser

Write-Host "Starting TCO Dashboard..." -ForegroundColor Cyan
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

# Start Flask server as a background job
$job = Start-Job -ScriptBlock {
    Set-Location $using:PSScriptRoot
    python web_dashboard\app.py
}

# Wait for server to start
Write-Host "Waiting for server to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

# Open browser
Write-Host "Opening browser..." -ForegroundColor Green
Start-Process "http://127.0.0.1:5847"

Write-Host ""
Write-Host "Dashboard is running at http://127.0.0.1:5847" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server." -ForegroundColor Yellow
Write-Host ""

# Show server output
try {
    while ($true) {
        Receive-Job $job
        Start-Sleep -Milliseconds 500
    }
}
finally {
    Stop-Job $job
    Remove-Job $job
}
