from celery import shared_task
from celery.contrib.abortable import AbortableTask

from time import sleep

from .extensions import db
from .db_models import User

@shared_task(bind=True, base=AbortableTask)
def add_user(self, form_data):
    db.session.add(User(name=form_data['name']))
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

@shared_task(bind=True, base=AbortableTask)
def process_video(self, filename, description, language, newfilepath, content_path, doc_id=None):
    client = config_video_indexer_client()
    try:
        # Realiza o upload do vídeo e a geração do prompt
        video_name, _ = filename.split(".")
        video_id = client.upload_video(video_name, newfilepath, video_description=description, language=language, wait_for_index=True)
        content_prompt = client.generate_prompt(video_id, operation='get_prompt_content')

        # Salva o prompt em um arquivo JSON
        with open(content_path, 'w') as file:
            json.dump(content_prompt, file, indent=4)

        # Insere no index
        _, content_file = content_path.rsplit("/", 1)
        if doc_id is not None:
            manager.insert_into_index(content_path, doc_id=content_file)
        else:
            manager.insert_into_index(content_path)

        return f"Video {video_id} processed successfully!"
    except Exception as e:
        raise self.retry(exc=e, countdown=10, max_retries=3)  # Retenta até 3 vezes se houver falha