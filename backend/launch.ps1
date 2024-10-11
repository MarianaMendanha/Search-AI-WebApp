# Navegar para a pasta 'app'
Write-Host "Indo para a pasta app..."
cd app

# Iniciar o index_server.py e exibir mensagem
Write-Host "Iniciando index_server.py..."
Start-Process -NoNewWindow python ./index_server.py
Write-Host "index_server está rodando..."

# Voltar para o diretório anterior
cd ..

# Esperar 10 segundos
Write-Host "Aguardando 20 segundos para iniciar o próximo processo..."
Start-Sleep -Seconds 20
# for ($i = 20; $i -ge 0; $i--) {
#     Write-Host "$i segundos restantes..."
#     Start-Sleep -Seconds 1
# }


# Iniciar run.py e exibir mensagem
Write-Host "Iniciando run.py..."
Start-Process -NoNewWindow python ./run.py
Write-Host "run.py está rodando..."

# Voltar para o diretório raiz e iniciar o frontend
Write-Host "Indo para o diretório frontend..."
cd ../frontend

# Iniciar o frontend
Write-Host "Iniciando frontend com npm..."
npm run dev

Write-Host "Frontend está rodando. Tudo está pronto!"

# && serve -s build

cd ../backend