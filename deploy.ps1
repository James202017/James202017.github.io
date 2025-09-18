# Скрипт автоматизации развертывания ботов на удаленном сервере (Windows PowerShell)
# Использование: .\deploy.ps1 [-Mode production|development|optimized]

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("production", "development", "optimized")]
    [string]$Mode = "optimized"
)

# Функции логирования
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Level) {
        "SUCCESS" { "Green" }
        "WARNING" { "Yellow" }
        "ERROR" { "Red" }
        default { "Cyan" }
    }
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color
}

function Write-Success { param([string]$Message) Write-Log $Message "SUCCESS" }
function Write-Warning { param([string]$Message) Write-Log $Message "WARNING" }
function Write-Error { param([string]$Message) Write-Log $Message "ERROR" }

# Определение файла docker-compose
$ComposeFile = switch ($Mode) {
    "production" { "docker-compose.production.yml" }
    "development" { "docker-compose.yml" }
    "optimized" { "docker-compose.optimized.yml" }
}

Write-Log "Запуск развертывания в режиме: $Mode"
Write-Log "Используется файл: $ComposeFile"

# Проверка наличия файлов
if (-not (Test-Path $ComposeFile)) {
    Write-Error "Файл $ComposeFile не найден!"
    exit 1
}

if (-not (Test-Path ".env")) {
    Write-Warning "Файл .env не найден. Проверьте конфигурацию."
}

# Функция очистки
function Invoke-Cleanup {
    Write-Log "Остановка и удаление контейнеров..."
    try {
        docker-compose -f $ComposeFile down --remove-orphans
        docker system prune -f
    } catch {
        Write-Warning "Ошибка при очистке: $($_.Exception.Message)"
    }
}

# Функция проверки здоровья
function Test-ServiceHealth {
    Write-Log "Проверка состояния сервисов..."
    
    # Ждем 30 секунд для инициализации
    Start-Sleep -Seconds 30
    
    try {
        $containers = docker-compose -f $ComposeFile ps -q
        
        foreach ($container in $containers) {
            if ($container) {
                $status = docker inspect --format='{{.State.Health.Status}}' $container 2>$null
                $name = docker inspect --format='{{.Name}}' $container | ForEach-Object { $_.TrimStart('/') }
                
                if ($status -eq "healthy" -or $status -eq "" -or $null -eq $status) {
                    Write-Success "Контейнер $name: OK"
                } else {
                    Write-Error "Контейнер $name: $status"
                }
            }
        }
    } catch {
        Write-Warning "Ошибка при проверке здоровья: $($_.Exception.Message)"
    }
}

# Функция мониторинга ресурсов
function Show-ResourceMonitoring {
    Write-Log "Мониторинг использования ресурсов..."
    try {
        docker stats --no-stream --format "table {{.Container}}`t{{.CPUPerc}}`t{{.MemUsage}}`t{{.NetIO}}"
    } catch {
        Write-Warning "Ошибка при получении статистики: $($_.Exception.Message)"
    }
}

# Основной процесс развертывания
function Start-Deployment {
    Write-Log "Начало развертывания..."
    
    # Проверка Docker
    try {
        docker --version | Out-Null
    } catch {
        Write-Error "Docker не установлен или недоступен!"
        exit 1
    }
    
    try {
        docker-compose --version | Out-Null
    } catch {
        Write-Error "Docker Compose не установлен или недоступен!"
        exit 1
    }
    
    # Создание необходимых директорий
    Write-Log "Создание директорий..."
    if (-not (Test-Path "logs")) { New-Item -ItemType Directory -Path "logs" -Force | Out-Null }
    if (-not (Test-Path "web")) { New-Item -ItemType Directory -Path "web" -Force | Out-Null }
    
    # Остановка существующих контейнеров
    Write-Log "Остановка существующих контейнеров..."
    try {
        docker-compose -f $ComposeFile down --remove-orphans 2>$null
    } catch {
        Write-Warning "Контейнеры уже остановлены или отсутствуют"
    }
    
    # Сборка образов (только для development и optimized)
    if ($Mode -ne "production") {
        Write-Log "Сборка Docker образов..."
        try {
            docker-compose -f $ComposeFile build --no-cache
        } catch {
            Write-Error "Ошибка при сборке образов: $($_.Exception.Message)"
            exit 1
        }
    }
    
    # Запуск сервисов
    Write-Log "Запуск сервисов..."
    try {
        docker-compose -f $ComposeFile up -d
    } catch {
        Write-Error "Ошибка при запуске сервисов: $($_.Exception.Message)"
        exit 1
    }
    
    # Проверка здоровья
    Test-ServiceHealth
    
    # Показать логи
    Write-Log "Последние логи сервисов:"
    try {
        docker-compose -f $ComposeFile logs --tail=10
    } catch {
        Write-Warning "Ошибка при получении логов: $($_.Exception.Message)"
    }
    
    # Мониторинг ресурсов
    Show-ResourceMonitoring
    
    Write-Success "Развертывание завершено!"
    Write-Log "Для просмотра логов: docker-compose -f $ComposeFile logs -f"
    Write-Log "Для остановки: docker-compose -f $ComposeFile down"
}

# Обработка ошибок
trap {
    Write-Error "Критическая ошибка: $($_.Exception.Message)"
    Invoke-Cleanup
    exit 1
}

# Запуск основной функции
try {
    Start-Deployment
    Write-Success "Все сервисы запущены успешно!"
} catch {
    Write-Error "Ошибка развертывания: $($_.Exception.Message)"
    exit 1
}