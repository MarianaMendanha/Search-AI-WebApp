from celery import shared_task
from celery.contrib.abortable import AbortableTask
from requests.exceptions import ConnectionError, Timeout

from time import sleep
import time

from .extensions import db
import requests

@shared_task(bind=True, base=AbortableTask)
def add_user(self, form_data):
    # db.session.add(User(name=form_data['name']))
    db.session.commit()
    
    for i in range(10):
        print(i)
        sleep(1)
        if self.is_aborted():
            return 'TASK STOPPED!'
    return 'DONE!'


import os
import json
from .routes import config_video_indexer_client
from .routes import manager

@shared_task(bind=True)
def process_video(self, video_name, description, language, newfilepath, content_path, partition):
    doc_id=None
    client = config_video_indexer_client()
    
    max_retries = 3  # Número máximo de tentativas de reconexão
    retry_count = 0
    wait_time = 10  # Tempo de espera entre tentativas, em segundos
    
    # Realiza o upload do vídeo e a geração do prompt
    # video_name, _ = filename.split(".")
    # video_id = client.upload_video(video_name, newfilepath, video_description=description, language=language, wait_for_index=True)
    try:
        video_id = client.upload_video(video_name=video_name, video_path_or_url=newfilepath, video_description=description, partition=partition, language=language)
        # print(f"ID DO VIDEO --->{video_id}")
    except Exception as e:
        # Outras exceções que não são relacionadas a conexão
        print(f"Erro durante o processamento de upload: {e}")
        res = requests.post("http://127.0.0.1:5000/uploadVideo_status", json={"name": video_name, "progress": "Failed"})
        return f"Video failed to upload!"
            
    while retry_count < max_retries:
        try:
            
            ## Implementar retry a partir daqui
            client.upload_video(video_id=video_id, video_name=video_name, language=language, op="wait")
            
            # requests.post("http://127.0.0.1:5000/uploadVideo_status", json={"videoId": video_id, "name": video_name, "progress": "Generating"})
            content_prompt = client.generate_prompt(video_id, operation='get_prompt_content')

            # Salva o prompt em um arquivo JSON
            with open(content_path, 'w') as file:
                json.dump(content_prompt, file, indent=4)

            # Insere no index
            _, content_file = content_path.rsplit("/", 1)
            if content_file is not None:
                manager.insert_into_index(content_path, doc_id=content_file)
            else:
                manager.insert_into_index(content_path)

            requests.post("http://127.0.0.1:5000/uploadVideo_status", json={"videoId": video_id, "name": video_name, "progress": "Finished"})
            return f"Video {video_id} processed successfully!"
        
        except (ConnectionError, Timeout) as e:
            print(f"Erro de conexão: {e}. Tentando reconectar... ({retry_count+1}/{max_retries})")
            retry_count += 1
            time.sleep(wait_time)  # Espera antes de tentar reconectar
            
        except Exception as e:
            # Outras exceções que não são relacionadas a conexão
            print(f"Erro durante o processamento: {e}")
            requests.post("http://127.0.0.1:5000/uploadVideo_status", json={"name": video_name, "progress": "Failed"})
            break
    
        if retry_count == max_retries:
            raise Exception("Não foi possível restabelecer a conexão após várias tentativas.")
    
    
