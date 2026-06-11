$ErrorActionPreference = "Stop"

$candidates = @(
    "$env:LOCALAPPDATA\Programs\Python\Python312",
    "$env:LOCALAPPDATA\Programs\Python\Python312\Scripts",
    "$env:LOCALAPPDATA\Programs\Python\Python311",
    "$env:LOCALAPPDATA\Programs\Python\Python311\Scripts",
    "$env:LOCALAPPDATA\Programs\Python\Launcher",
    "$env:ProgramFiles\Git\cmd",
    "$env:ProgramFiles\Git\bin",
    "${env:ProgramFiles(x86)}\Git\cmd"
)

$existing = $candidates | Where-Object { $_ -and (Test-Path $_) } | Select-Object -Unique
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if (-not $userPath) { $userPath = "" }

$parts = $userPath -split ";" | Where-Object { $_ }
$added = @()

foreach ($path in $existing) {
    $alreadyThere = $parts | Where-Object { $_.TrimEnd("\") -ieq $path.TrimEnd("\") }
    if (-not $alreadyThere) {
        $parts += $path
        $added += $path
    }
}

if ($added.Count -gt 0) {
    [Environment]::SetEnvironmentVariable("Path", ($parts -join ";"), "User")
    $env:Path = ($parts -join ";") + ";" + [Environment]::GetEnvironmentVariable("Path", "Machine")
    Write-Host "PATH atualizado para o usuario atual:"
    $added | ForEach-Object { Write-Host " - $_" }
} else {
    Write-Host "Nenhum caminho novo encontrado para adicionar ao PATH."
}

if (-not ($existing | Where-Object { $_ -like "*Git*" })) {
    Write-Host "Git nao foi encontrado nos caminhos padrao. Instale o Git for Windows e rode este script novamente."
}
