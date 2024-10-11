from flask import Blueprint, render_template
import os
from flask import request, jsonify, make_response
from werkzeug.utils import secure_filename
from multiprocessing.managers import BaseManager


# initialize manager connection
# NOTE: you might want to handle the password in a less hardcoded way
manager = BaseManager(address=('127.0.0.1', 5002), authkey=b'password')
manager.register('query_index')
manager.register('insert_into_index')
manager.register('get_documents_list')
manager.connect()

from app.tools.video.client.video_indexer_client import VideoIndexerClient
from app.tools.video.client.Consts import Consts
import json
from dotenv import dotenv_values
from pprint import pprint
import sys

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

main = Blueprint('main', __name__)

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
        filepath = os.path.join(diretorio_atual, 'documents', os.path.basename(filename))
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
        print(video_name)
        video_id = client.upload_video(video_name, newfilepath, video_description=description, language=language, wait_for_index=True)
        content_prompt = client.generate_prompt(video_id, operation='get_prompt_content')
        
        # adicionar content_prompt em um json e adicionar ele no index com o manager
        url, _ = newfilepath.split(".")
        content_path = url + "_Video.json"
        print(content_path)
        with open(content_path, 'w') as file:
            json.dump(content_prompt, file, indent=4)
        
        uploaded_file.save(newfilepath)
        print(f"Chegamos aqui no vídeo: {video_id}")

        _, content_file = content_path.rsplit("/", 1)
        print(content_file)
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
