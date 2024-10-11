import requests
from typing import Optional
from pprint import pprint

from app.tools.video.client.Consts import Consts
from app.tools.video.client.account_token_provider import get_arm_access_token, get_account_access_token_async

from app.tools.video.client.managers.video_upload import VideoUploadManager
from app.tools.video.client.managers.video_content import VideoContentManager
from app.tools.video.client.managers.video_summary import VideoSummaryManager


class VideoIndexerClient:
    def __init__(self):
        self.arm_access_token = ''
        self.vi_access_token = ''
        self.account = None
        self.consts = None
        
        self.upload_manager = VideoUploadManager(self)
        self.content_manager = VideoContentManager(self)
        self.summary_manager = VideoSummaryManager(self)
    
    # Authentication
    def authenticate_async(self, consts:Consts) -> None:
        self.consts = consts
        # Get access tokens
        self.arm_access_token = get_arm_access_token(self.consts)
        self.vi_access_token = get_account_access_token_async(self.consts, self.arm_access_token)

    def get_account_async(self) -> None:
        '''
        Get information about the account
        '''
        if self.account is not None:
            return self.account

        headers = {
            'Authorization': 'Bearer ' + self.arm_access_token,
            'Content-Type': 'application/json'
        }

        url =   f'{self.consts.AzureResourceManager}/subscriptions/{self.consts.SubscriptionId}/resourcegroups/' + \
                f'{self.consts.ResourceGroup}/providers/Microsoft.VideoIndexer/accounts/{self.consts.AccountName}' + \
                f'?api-version={self.consts.ApiVersion}'

        response = requests.get(url, headers=headers)

        response.raise_for_status()

        self.account = response.json()
        print(f'[Account Details] Id:{self.account["properties"]["accountId"]}, Location: {self.account["location"]}')

    def upload_video(   self, video_name: Optional[str] = None, video_path_or_url: str = '', wait_for_index: bool = False, video_description: str = '',
                        privacy: str = 'Private', partition='', language: str = 'auto' ) -> str:
        """
        Uploads a video, automatically detecting if it's a URL or a file path.
        
        :param video_name: The name of the video (optional for files, required for URLs).
        :param video_path_or_url: The URL or file path of the video to upload.
        :param excluded_ai: A list of AI models to exclude during processing.
        :param wait_for_index: If True, waits for the indexing process to complete before returning.
        :param video_description: A description of the video.
        :param privacy: The privacy setting of the video.
        
        :return: The ID of the uploaded video.
        """
        # excluded_ai = excluded_ai or []

        if video_path_or_url.startswith("http") or video_path_or_url.startswith("https"):  # Assume it's a URL
            print("É uma URL!")
            # Call upload_by_url if the input is a URL
            return self.upload_manager.upload_by_url(
                video_name=video_name, 
                video_url=video_path_or_url, 
                wait_for_index=wait_for_index, 
                video_description=video_description,
                privacy=privacy,
                language=language
            )
        else:
            print("É um Arquivo!")
            # Call upload_by_file if the input is a local file path
            return self.upload_manager.upload_by_file(
                media_path=video_path_or_url, 
                video_name=video_name, 
                wait_for_index=wait_for_index,
                video_description=video_description, 
                privacy=privacy,
                partition=partition,
                language=language
            )

    def generate_prompt(self, video_id: str, operation:str='', promptStyle: str = 'Full', timeout_sec:Optional[int]=None, check_alreay_exists=True) -> Optional[dict]:
        """
        This Python function generates a prompt based on the provided video ID and operation type.
        
        :param video_id: The `video_id` parameter is a string that represents the unique identifier of a video. It is used to identify the specific video for which you want to generate a prompt or retrieve insights
        :param operation: The `operation` parameter in the `generate_prompt` method is used to specify the type of operation to be performed. It can have two possible values:
        :param promptStyle: The `promptStyle` parameter in the `generate_prompt` method is used to specify the style of the prompt content to be retrieved. It has a default value of 'Full', but you can provide other styles as well based on the available options in your system, defaults to Full
        :param timeout_sec: The `timeout_sec` parameter in the `generate_prompt` method is an optional integer that represents the timeout duration in seconds for the prompt generation process. If a value is provided for `timeout_sec`, the prompt generation process will be limited to that duration, and if the process exceeds the specified timeout,
        :param check_alreay_exists: The `check_alreay_exists` parameter is not used within the `generate_prompt` method. It seems to be a typo or a parameter that is not being utilized in the current implementation of the method. If you intended to use this parameter for some specific functionality, you may need to update the, defaults to True (optional)
        
        :return: The `generate_prompt` method returns a dictionary containing either raw insight data or prompt content based on the specified operation and parameters. If the operation is 'get_insight', it returns raw insight data for the given video_id. If the operation is 'get_prompt_content', it returns prompt content for the given video_id with the specified promptStyle and timeout_sec. If the operation does not match either of
        """
        if operation == 'get_insight':
            return self.content_manager.get_raw_insight(video_id=video_id)
        elif operation == 'get_prompt_content':
            return self.content_manager.get_prompt(video_id=video_id, promptStyle=promptStyle, timeout_sec=timeout_sec)
        else:
            raise ValueError("Operation parameter passed must be 'get_insight' or 'get_prompt_content'")

    def list_videos(self) -> dict:
        """
        The function `list_videos` retrieves a list of videos from a specified account using an API endpoint and access token.
        
        :return: The `list_videos` method returns a dictionary containing the list of videos in the specified account. The method makes a GET request to a specific URL with the necessary parameters, retrieves the response, and returns the JSON data of the listed results.
        """
        """ 
        future params: [?createdAfter][&createdBefore][&pageSize][&skip][&partitions]
        """
        print(f'Listing videos in account {self.account["properties"]["accountId"]}:')
        
        url = f'{self.consts.ApiEndpoint}/{self.account["location"]}/Accounts/{self.account["properties"]["accountId"]}/' + \
                f'Videos'
        
        params = {
                'accessToken': self.vi_access_token
            }           
                
        response = requests.get(url, params=params)
        
        response.raise_for_status()
        
        list_result = response.json()
        print(f'Here are the listed results:')
        pprint(list_result)
        
        return list_result

    def video_summary(self, video_id: str, operation: str = '', summary_id: Optional[str] = None, model_name: Optional[str] = "gpt-35-turbo", sum_len: Optional[str] = "Long", sum_style: Optional[str] = "Neutral") -> Optional[dict]:
        """
        Gera ou lista resumos de vídeos.
        
        :param video_id (str): ID do vídeo.
        :param  operation (str): Operação a ser realizada ('list' ou 'create').
        :param  summary_id (Optional[str]): ID do resumo para listar um resumo específico.
        :param  model_name (str): Nome do modelo a ser usado para criar o resumo.
        :param  sum_len (str): Comprimento do resumo ('Short', 'Medium', 'Long').
        :param  sum_style (str): Estilo do resumo ('Neutral', 'Formal', 'Informal').
        
        :return: Optional[Dict]: Dicionário com os dados do resumo ou None.
        """
        if operation == 'list':
            return self.summary_manager.list_summaries(video_id=video_id, summary_id=summary_id)
        elif operation == 'create':
            return self.summary_manager.create_summary(video_id=video_id, model_name=model_name, sum_len=sum_len, sum_style=sum_style)
        else:
            raise ValueError("Operation parameter passed must be 'list' or 'create'")



