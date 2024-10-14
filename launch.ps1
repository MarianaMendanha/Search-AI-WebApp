# Navegar para a pasta 'app'
cd backend/app

# Iniciar o index_server.py e exibir mensagem
Write-Host "[PROCESS] Iniciando o index_server.py..." -ForegroundColor Blue
Start-Process -NoNewWindow python ./index_server.py
Start-Sleep -Seconds 10
# Voltar para o diretório anterior
cd ..

# Esperar 20 segundos
# Write-Host "[PROCESS] Aguardando 20 segundos para iniciar o proximo processo..." -ForegroundColor Blue
# Start-Sleep -Seconds 20


# Esperar até o servidor estar ativo
$port = 5002
Write-Host "[WAITING] Aguardando o index_server.py iniciar (porta $port)..." -ForegroundColor Yellow
$timeout = 20
$interval = 1
$timePassed = 0


$OriginalProgressPreference = $Global:ProgressPreference
$Global:ProgressPreference = 'SilentlyContinue'
while ($timePassed -lt $timeout) {
    # Testar se a porta está aberta
    $tcpConnection = Test-NetConnection -ComputerName 127.0.0.1 -Port $port -WarningAction SilentlyContinue
    if ($tcpConnection.TcpTestSucceeded) {
        Write-Host "[SUCCESS] index_server.py rodando na porta $port!" -ForegroundColor Green
        break
    } else {
        Write-Host "[WAITING] Esperando o servidor iniciar... ($timePassed segundos passados)" -ForegroundColor Yellow
        Start-Sleep -Seconds $interval
        $timePassed += $interval
    }
}
$Global:ProgressPreference = $OriginalProgressPreference

if ($timePassed -ge $timeout) {
    Write-Host "[ERROR] Timeout: O servidor não iniciou dentro do tempo limite de $timeout segundos." -ForegroundColor Red
    exit 1
}

Write-Host "[PROCESS] Iniciando o Redis server..." -ForegroundColor Blue
Start-Process -NoNewWindow redis-server .\redis.conf
Start-Sleep -Seconds 3

# Iniciar o Celery worker e exibir mensagem
Write-Host "[PROCESS] Iniciando Celery worker..." -ForegroundColor Blue
Start-Process -NoNewWindow -FilePath "celery" -ArgumentList "-A run.celery worker --pool=solo -l info"
Start-Sleep -Seconds 5

# Iniciar run.py e exibir mensagem
Write-Host "[PROCESS] Iniciando run.py..." -ForegroundColor Blue
Start-Process -NoNewWindow python ./run.py
Write-Host "[SUCCESS] run.py esta rodando..." -ForegroundColor Green

# Voltar para o diretório raiz e iniciar o frontend
cd ../frontend

# Iniciar o frontend
Write-Host "[PROCESS] Iniciando frontend com npm..." -ForegroundColor Blue
npm run dev

# Write-Host "[SUCCESS] Frontend esta rodando. Tudo esta pronto!" -ForegroundColor Green
# && serve -s build
cd ..