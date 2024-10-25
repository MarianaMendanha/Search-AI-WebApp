from flask import Blueprint, render_template, request, jsonify, make_response, redirect
import os
from werkzeug.utils import secure_filename
from multiprocessing.managers import BaseManager

main = Blueprint('main', __name__)

# initialize manager connection
# NOTE: you might want to handle the password in a less hardcoded way
manager = BaseManager(address=('127.0.0.1', 5002), authkey=b'password')
manager.register('query_index')
manager.register('insert_into_index')
manager.register('get_documents_list')
manager.connect()

from app.tools.video.client.video_indexer_client import VideoIndexerClient
from app.tools.video.client.Consts import Consts
import json, sys
from dotenv import dotenv_values
from pprint import pprint
import redis
import threading
import time


def config_video_indexer_client():
    config = dotenv_values(".env")
    
    AccountName = config.get('AccountName')
    ResourceGroup = config.get('ResourceGroup')
    SubscriptionId = config.get('SubscriptionId')
    ApiVersion = '2024-01-01'
    ApiEndpoint = 'https://api.videoindexer.ai'
    AzureResourceManager = 'https://management.azure.com'
    consts = Consts(ApiVersion, ApiEndpoint, AzureResourceManager, AccountName, ResourceGroup, SubscriptionId)

    client = VideoIndexerClient()
    client.authenticate_async(consts)
    client.get_account_async()
    
    return client


@main.route('/')
def index_home():
    return render_template('index.html', title='Bem-vindos', message='Esta é a minha aplicação Flask!')

@main.route("/query", methods=["GET"])
def query_index():
    global manager
    query_text = request.args.get("text", None)
    if query_text is None:
        return "No text found, please include a ?text=blah parameter in the URL", 400
    
    response = manager.query_index(query_text)._getvalue()
    print("MARI AQUI-------------->",response)
    response_json = {
        "text": str(response),
        "sources":[""" {"text": str(x.text), 
                    "similarity": round(x.score, 2),
                    "doc_id": str(x.id_),
                    "start": x.node_info['start'],
                    "end": x.node_info['end'],
                    } for x in response.source_nodes """]
    }
    return make_response(jsonify(response_json)), 200

@main.route("/uploadFile", methods=["POST"])
def upload_file():
    global manager
    if 'file' not in request.files:
        return "Please send a POST request with a file", 400
    
    filepath = None
    try:
        uploaded_file = request.files["file"]
        filename = secure_filename(uploaded_file.filename)
        print(filename)
        diretorio_atual = os.getcwd()
        upload_folder = 'uploads/'
        os.makedirs(upload_folder, exist_ok=True)
        # filepath = os.path.join(diretorio_atual, 'documents', os.path.basename(filename))
        filepath = os.path.join(diretorio_atual, upload_folder, uploaded_file.filename)
        print(filepath)

        uploaded_file.save(filepath)

        if request.form.get("filename_as_doc_id", None) is not None:
            manager.insert_into_index(filepath, doc_id=filename)
        else:
            manager.insert_into_index(filepath)
    except Exception as e:
        # cleanup temp file
        if filepath is not None and os.path.exists(filepath):
            os.remove(filepath)
        return "Error: {}".format(str(e)), 500

    # cleanup temp file
    if filepath is not None and os.path.exists(filepath):
        os.remove(filepath)

    return "File inserted!", 200

@main.route("/getDocuments", methods=["GET"])
def get_documents():
    document_list = manager.get_documents_list()._getvalue()

    return make_response(jsonify(document_list)), 200

@main.route("/uploadVideo", methods=["POST"])
def upload_video():
    client = config_video_indexer_client()
    
    args = request.args
    description = args.get('description')
    language = args.get('language')
    
    global manager
    if 'file' not in request.files:
        return "Please send a POST request with a file", 400
    
    newfilepath = None
    try:
        uploaded_file = request.files["file"]
        filename = secure_filename(uploaded_file.filename)
        diretorio_atual = os.getcwd()
        newfilepath = os.path.join(diretorio_atual, 'documents', os.path.basename(filename)).replace("\\", "/")
        oldfilepath = os.path.join(diretorio_atual, 'documents', os.path.basename(uploaded_file.filename)).replace("\\", "/")
        print("OLD FILE NAME: ", oldfilepath, "\nNEW FILE NAME: ", newfilepath)
        
        os.rename(oldfilepath, newfilepath)
        video_name, _ = uploaded_file.filename.split(".")
        print(f"video name :{video_name}")
        video_id = client.upload_video(video_name, newfilepath, video_description=description, language=language, wait_for_index=True)
        content_prompt = client.generate_prompt(video_id, operation='get_prompt_content')
        
        # adicionar content_prompt em um json e adicionar ele no index com o manager
        url, _ = newfilepath.split(".")
        content_path = url + "_Video.json"
        # print(content_path)
        with open(content_path, 'w') as file:
            json.dump(content_prompt, file, indent=4)
        
        uploaded_file.save(newfilepath)
        # print(f"Chegamos aqui no vídeo: {video_id}")

        _, content_file = content_path.rsplit("/", 1)
        # print(content_file)
        if request.form.get("filename_as_doc_id", None) is not None:
            manager.insert_into_index(content_path, doc_id=content_file)
        else:
            manager.insert_into_index(content_path)
    except Exception as e:
        # cleanup temp file
        if newfilepath is not None and os.path.exists(newfilepath):
            # os.remove(filepath)
            pass
        return "Error: {}".format(str(e)), 500

    # cleanup temp file
    if newfilepath is not None and os.path.exists(newfilepath):
        # os.remove(filepath)
        pass

    return "File inserted!", 200

from .tasks import process_video
@main.route("/uploadVideoAsync", methods=["POST"])
def upload_video_async():
    args = request.args
    description = args.get('description')
    language = args.get('language')
    partition = args.get('partition')

    if 'file' not in request.files:
        return jsonify({"error": "Please send a POST request with a file"}), 400

    try:
        # Processa o arquivo
        uploaded_file = request.files["file"]
        filename = secure_filename(uploaded_file.filename)
        
        diretorio_atual = os.getcwd()
        newfilepath = os.path.join(diretorio_atual, 'documents', os.path.basename(filename)).replace("\\", "/")
        content_path = newfilepath.rsplit(".", 1)[0] + "_Video.json"
        # Salva o arquivo temporariamente
        uploaded_file.save(newfilepath)
        
        # client = config_video_indexer_client()
        video_name, _ = filename.split(".")
        
        # Chama a task Celery para processar o vídeo em background
        task = process_video.delay(video_name, description, language, newfilepath, content_path, partition)

        return jsonify({"message": "File is being processed", "task_id": task.id}), 202

    except Exception as e:
        return jsonify({"error": str(e)}), 500

redis_client = redis.StrictRedis(host='127.0.0.1', port=6380, db=0)
def delete_key_after_delay(key, delay):
    time.sleep(delay)
    redis_client.delete(key)
@main.route("/uploadVideo_status", methods=["GET","POST"])
def upload_video_status():
    if request.method == "POST":
        data = request.get_json()
        # videoId = data.get("videoId")
        video_name = data.get("name")
        progress = data.get("progress")
        # print(f"No endpoint:{(video_name)}|{type(video_name)}:{progress}|{type(video_name)}")

        if video_name and progress:
            # Armazena ou atualiza o progresso no Redis
            redis_client.set(f"video:{video_name}", progress)
            
            # if progress == "Generating":
            #     return jsonify({"message": f"Generating prompt content for video {video_name}"}), 200

            # Verifica se o progresso é 100% e apaga o registro se for o caso
            if progress == "Exclude":
                print("Upload Concluído")
                thread = threading.Thread(target=delete_key_after_delay, args=(f"video:{video_name}", 2))
                thread.start()
                return jsonify({"message": "Progress Completed and deleted!"}), 200

            return jsonify({"message": "Progress updated successfully!"}), 200
        else:
            return jsonify({"error": "Invalid data!"}), 400

    elif request.method == "GET":
        # Recupera o progresso de todos os vídeos, ignorando chaves irrelevantes
        all_progress = {}
        for key in redis_client.keys():
            key_name = key.decode("utf-8")
            if key_name.startswith("video:"):  # Supondo que você use um prefixo para as chaves de vídeo
                value_type = redis_client.type(key).decode("utf-8")
                if value_type == 'string':
                    all_progress[key_name] = redis_client.get(key).decode("utf-8")
                else:
                    all_progress[key_name] = f"Value type is {value_type}, cannot decode."
        return jsonify(all_progress), 200


@main.route('/task_status/<task_id>', methods=["GET"])
def get_task_status(task_id):
    task = process_video.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'progress': 0
        }
    elif task.state == 'PROGRESS':
        response = {
            'state': task.state,
            'progress': task.info.get('current', 0) / task.info.get('total', 1) * 100
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'progress': 100,
            'result': task.info
        }
    else:
        response = {
            'state': task.state,
            'progress': 0,
            'result': str(task.info)  # traceback
        }
    return jsonify(response)





@main.route("/cancel/<task_id>")
def cancel(task_id):
    task = process_video.AsyncResult(task_id)
    task.abort()
    return "CANCELED!"

from .forms import MyForm
from .tasks import add_user
@main.route('/create_user', methods=['GET', 'POST'])
def create_user():
    form = MyForm()

    if form.validate_on_submit():
        task = add_user.delay(form.data)
        return render_template("cancel.html", task=task)

    return render_template('form.html', form=form)

