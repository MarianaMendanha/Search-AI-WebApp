Para implementar esse fluxo no seu webapp, onde o upload e indexação do vídeo no **Azure Video Indexer (AVI)** ocorrem em segundo plano enquanto o usuário continua a usar o aplicativo, você precisará de uma arquitetura assíncrona com **backend** e **frontend** interagindo continuamente. Vou detalhar a abordagem dividida em **backend** e **frontend**, com as requisições e mudanças necessárias para cada parte:

### Backend

#### 1. **Requisição para Upload de Vídeo**
   - Assim que o usuário faz o upload do vídeo, o backend envia uma requisição à API do Azure Video Indexer para iniciar o processo de upload.
   - A requisição incluirá o vídeo em questão e parâmetros como o nome do vídeo, descrições e outras informações necessárias para AVI.

   Exemplo de requisição:
   ```python
   def upload_video_to_avi(video_path: str):
       avi_url = "https://api.videoindexer.ai/{location}/Accounts/{accountId}/Videos"
       headers = {"Ocp-Apim-Subscription-Key": "{api_key}"}
       params = {
           "name": video_name,
           "privacy": "private",  # Defina a privacidade conforme sua necessidade
           "description": "Video description",
           "videoUrl": video_url,  # ou forneça o caminho do arquivo se for local
       }
       response = requests.post(avi_url, headers=headers, params=params)
       return response.json()
   ```

#### 2. **Monitoramento do Progresso de Indexação**
   - Assim que o vídeo é enviado, você obterá um **ID do vídeo** no retorno da requisição.
   - Use esse **ID** para monitorar o progresso de indexação enviando requisições periódicas à AVI para checar o status.

   Exemplo de requisição de progresso:
   ```python
   def check_video_index_status(video_id: str):
       avi_url = f"https://api.videoindexer.ai/{location}/Accounts/{accountId}/Videos/{video_id}/Index"
       headers = {"Ocp-Apim-Subscription-Key": "{api_key}"}
       response = requests.get(avi_url, headers=headers)
       return response.json()  # O status retornará informações sobre o progresso
   ```

   - Esse processo de monitoramento pode ser feito através de uma **tarefa assíncrona** no backend (ex: usando **Celery** ou **Django-Q**). O frontend irá requisitar o status dessa tarefa para atualizar a barra de progresso.

#### 3. **Geração do `prompt_content`**
   - Quando o status de indexação for "pronto", faça uma requisição adicional à AVI para obter o **conteúdo processado** (transcrição, insights, etc.).

   Exemplo de requisição para obter transcrição e insights:
   ```python
   def get_video_content(video_id: str):
       avi_url = f"https://api.videoindexer.ai/{location}/Accounts/{accountId}/Videos/{video_id}/Index"
       headers = {"Ocp-Apim-Subscription-Key": "{api_key}"}
       params = {
           "language": "Portuguese",  # Defina o idioma conforme necessário
       }
       response = requests.get(avi_url, headers=headers)
       return response.json()  # Esse JSON conterá os insights e a transcrição
   ```

   - Esse conteúdo será retornado em formato JSON e adicionado ao **índice de pesquisa** do seu sistema de maneira que o vídeo também seja pesquisável.

#### 4. **Comunicação Backend-Frontend (Push Notification)**
   - Para informar ao usuário quando o vídeo estiver indexado e pronto para uso, o backend pode emitir um **websocket** ou usar uma ferramenta como **SSE (Server-Sent Events)** ou **Pusher** para enviar uma notificação em tempo real ao frontend.

   - O backend enviará uma notificação ao frontend assim que o vídeo for processado, permitindo que o frontend mostre um **popup de notificação**.

### Frontend

#### 1. **Upload do Vídeo**
   - Assim que o usuário faz o upload do vídeo, o frontend dispara uma requisição **HTTP** para o backend, enviando o arquivo ou URL do vídeo.
   
   Exemplo de upload:
   ```javascript
   function uploadVideo(videoFile) {
       const formData = new FormData();
       formData.append('video', videoFile);
       fetch('/api/upload_video', {
           method: 'POST',
           body: formData
       })
       .then(response => response.json())
       .then(data => {
           // Recebe o ID do vídeo e inicia a checagem de progresso
           checkVideoProgress(data.video_id);
       });
   }
   ```

#### 2. **Atualização da Barra de Progresso**
   - O frontend continuamente checa o progresso do upload e indexação fazendo chamadas periódicas ao backend (via polling) ou estabelecendo uma conexão websocket para atualizações em tempo real.
   
   Exemplo de polling para verificar progresso:
   ```javascript
   function checkVideoProgress(video_id) {
       setInterval(() => {
           fetch(`/api/check_progress?video_id=${video_id}`)
           .then(response => response.json())
           .then(data => {
               updateProgressBar(data.progress);
               if (data.status === 'completed') {
                   showNotification("O vídeo foi indexado e está pronto para pesquisa.");
               }
           });
       }, 5000);  // Verifica o status a cada 5 segundos
   }

   function updateProgressBar(progress) {
       const progressBar = document.getElementById("progressBar");
       progressBar.style.width = `${progress}%`;
   }
   ```

#### 3. **Notificação de Sucesso**
   - Quando o backend indica que o vídeo foi processado, uma notificação aparece no frontend (pode ser um **popup** ou um **toast**).
   
   Exemplo de popup:
   ```javascript
   function showNotification(message) {
       const notification = document.createElement("div");
       notification.className = "notification";
       notification.innerText = message;
       document.body.appendChild(notification);
       
       // Remover a notificação após um tempo
       setTimeout(() => {
           document.body.removeChild(notification);
       }, 5000);
   }
   ```

   O popup informaria que o vídeo já foi indexado, permitindo ao usuário recarregar a página para ver os novos documentos pesquisáveis.

---

### Plano de Desenvolvimento por Etapas:

#### 1. **Backend**:
   - Criar endpoints para:
     - Fazer o upload de vídeos para o AVI.
     - Verificar o status de indexação de vídeos (polling).
     - Obter o conteúdo indexado (transcrição e insights).
   - Implementar um sistema assíncrono para monitorar o progresso da indexação (usando Celery, Redis ou similar).
   - Implementar websockets ou uma solução de notificação para o frontend.
   
#### 2. **Frontend**:
   - Implementar a funcionalidade de upload de vídeo (envio do arquivo ou URL).
   - Criar uma barra de progresso para monitorar o status do upload e indexação.
   - Implementar um sistema de notificações (popup) para avisar quando o vídeo estiver pronto.
   - Atualizar a interface do usuário para permitir consultas e pesquisas nos documentos indexados.

#### 3. **Integração**:
   - Testar o fluxo completo de upload, indexação e retorno de conteúdo.
   - Testar notificações em tempo real (via websockets ou polling).
   - Validar o comportamento da barra de progresso.
