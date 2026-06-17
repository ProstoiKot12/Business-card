param(
    [switch]$Migrate,
    [switch]$SkipInfra
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$venvPath = Join-Path $root ".venv"
$pythonPath = Join-Path $venvPath "Scripts\\python.exe"
$stateDir = Join-Path $root ".dev-state"
$migrationsStampPath = Join-Path $stateDir "migrations.txt"
$alembicConfigPath = Join-Path $root "alembic.ini"
$migrationsPath = Join-Path $root "app\\migrations"

function Invoke-Native {
    param(
        [string]$FilePath,
        [string[]]$Arguments
    )

    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $FilePath $($Arguments -join ' ')"
    }
}

function Wait-TcpPort {
    param(
        [string]$HostName,
        [int]$Port,
        [int]$TimeoutSeconds = 30
    )

    Write-Host "Waiting for ${HostName}:${Port}..."
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    do {
        $client = [System.Net.Sockets.TcpClient]::new()
        try {
            $connect = $client.BeginConnect($HostName, $Port, $null, $null)
            if ($connect.AsyncWaitHandle.WaitOne(1000, $false)) {
                $client.EndConnect($connect)
                return
            }
        } catch {
        } finally {
            $client.Close()
        }

        Start-Sleep -Milliseconds 500
    } while ((Get-Date) -lt $deadline)

    throw "${HostName}:${Port} did not become reachable within $TimeoutSeconds seconds."
}

function Get-FileFingerprint([string[]]$Paths) {
    $parts = foreach ($path in $Paths) {
        if (Test-Path $path) {
            $item = Get-Item $path
            "{0}|{1}|{2}" -f $item.FullName, $item.LastWriteTimeUtc.Ticks, $item.Length
        }
    }
    return ($parts -join "`n")
}

function Get-MigrationsFingerprint {
    $paths = @($alembicConfigPath)
    if (Test-Path $migrationsPath) {
        $paths += Get-ChildItem -Path $migrationsPath -Recurse -File | Select-Object -ExpandProperty FullName
    }

    return Get-FileFingerprint -Paths $paths
}

function Wait-Postgres {
    param([int]$TimeoutSeconds = 30)

    Write-Host "Waiting for PostgreSQL..."
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    do {
        docker compose exec -T postgres pg_isready -U bot -d business_card_bot | Out-Null
        if ($LASTEXITCODE -eq 0) {
            return
        }
        Start-Sleep -Seconds 1
    } while ((Get-Date) -lt $deadline)

    throw "PostgreSQL did not become ready within $TimeoutSeconds seconds."
}

if (-not (Test-Path $pythonPath)) {
    $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if (-not $pyLauncher) {
        throw "Python launcher 'py' не найден. Установите Python 3.11+ или создайте .venv вручную."
    }

    Write-Host "Creating virtual environment..."
    Invoke-Native $pyLauncher.Path @("-3.11", "-m", "venv", $venvPath)
}

if (-not (Test-Path $stateDir)) {
    New-Item -ItemType Directory -Path $stateDir | Out-Null
}



if (-not $SkipInfra) {
    Write-Host "Starting PostgreSQL and Redis in Docker..."
    Invoke-Native "docker" @("compose", "up", "-d", "--remove-orphans", "postgres", "redis")
    Wait-Postgres
    Wait-TcpPort -HostName "127.0.0.1" -Port 5432
    Wait-TcpPort -HostName "127.0.0.1" -Port 6379
}

$migrationsFingerprint = Get-MigrationsFingerprint
$savedMigrationsFingerprint = if (Test-Path $migrationsStampPath) { Get-Content $migrationsStampPath -Raw } else { "" }
$shouldMigrate = $Migrate -or -not (Test-Path $migrationsStampPath) -or ($migrationsFingerprint -ne $savedMigrationsFingerprint)

if ($shouldMigrate) {
    Write-Host "Applying database migrations..."
    Invoke-Native $pythonPath @("-m", "alembic", "upgrade", "head")
    Set-Content -Path $migrationsStampPath -Value $migrationsFingerprint
}

Write-Host "Starting bot from local virtual environment..."
Invoke-Native $pythonPath @("-m", "app.main")
