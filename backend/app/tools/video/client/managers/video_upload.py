from app.tools.video.client.interfaces.video_upload import VideoUploadManagerInterface
from typing import Optional
from urllib.parse import urlparse
import os, time, requests

def get_file_name_no_extension(file_path):
    return os.path.splitext(os.path.basename(file_path))[0]

class VideoUploadManager(VideoUploadManagerInterface):
    def __init__(self, client):
        self.client = client
    
    def upload_by_url(self, video_name:str, video_url:str,
                        wait_for_index:bool=False, video_description:str='', privacy='Private') -> str:
        '''
        Uploads a video and starts the video index.
        Calls the uploadVideo API (https://api-portal.videoindexer.ai/api-details#api=Operations&operation=Upload-Video)

        :param video_name: The name of the video
        :param video_url: Link to publicly accessed video URL
        :param excluded_ai: The ExcludeAI list to run
        :param wait_for_index: Should this method wait for index operation to complete
        :param video_description: The description of the video
        :param privacy: The privacy mode of the video
        :return: Video Id of the video being indexed, otherwise throws exception
        '''

        # check that video_url is valid
        parsed_url = urlparse(video_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise Exception(f'Invalid video URL: {video_url}')

        # self.get_account_async() # if account is not initialized, get it

        url = f'{self.client.consts.ApiEndpoint}/{self.client.account["location"]}/Accounts/{self.client.account["properties"]["accountId"]}/Videos'

        params = {
            'accessToken': self.client.vi_access_token,
            'name': video_name,
            'description': video_description,
            'privacy': privacy,
            'videoUrl': video_url
        }

        response = requests.post(url, params=params)

        response.raise_for_status()

        video_id = response.json().get('id')
        print(f'Video ID {video_id} was uploaded successfully')

        if wait_for_index:
            self._wait_for_index(video_id)

        return video_id

    def upload_by_file(self, media_path:str, video_name:Optional[str]=None,
                        wait_for_index:bool=False, video_description:str='', privacy='Private', partition='', language:str = 'auto') -> str:
        '''
        Uploads a local file and starts the video index.
        Calls the uploadVideo API (https://api-portal.videoindexer.ai/api-details#api=Operations&operation=Upload-Video)

        :param media_path: The path to the local file
        :param video_name: The name of the video, if not provided, the file name will be used
        :param excluded_ai: The ExcludeAI list to run
        :param video_description: The description of the video
        :param privacy: The privacy mode of the video
        :param partition: The partition of the video
        :return: Video Id of the video being indexed, otherwise throws excpetion
        '''
        # if excluded_ai is None:
        #     excluded_ai = []

        if video_name is None:
            video_name = get_file_name_no_extension(media_path)

        if not os.path.exists(media_path):
            raise Exception(f'Could not find the local file {media_path}')


        url = f'{self.client.consts.ApiEndpoint}/{self.client.account["location"]}/Accounts/{self.client.account["properties"]["accountId"]}/Videos'

        params = {
            'name': video_name[:80],  # TODO: Is there a limit on the video name? If so, notice the used and also update `upload_url_async()` accordingly
            'description': video_description,
            'privacy': privacy,
            'partition': partition,
            'language': language,
            'accessToken': self.client.vi_access_token,
        }



        print('Uploading a local file using multipart/form-data post request to this URL:')

        response = requests.post(url, params=params, files={'file': open(media_path,'rb')}, stream=True)

        response.raise_for_status()

        if response.status_code != 200:
            print(f'Request failed with status code: {response.StatusCode}')

        video_id = response.json().get('id')
        
        if wait_for_index:
            self._wait_for_index(video_id, video_name, language)

        return video_id

    def _wait_for_index(self, video_id:str, video_name:str, language:str='auto', timeout_sec:Optional[int]=None) -> None:
        '''
        Calls getVideoIndex API in 10 second intervals until the indexing state is 'processed'
        (https://api-portal.videoindexer.ai/api-details#api=Operations&operation=Get-Video-Index).
        Prints video index when the index is complete, otherwise throws exception.

        :param video_id: The video ID to wait for
        :param language: The language to translate video insights
        :param timeout_sec: The timeout in seconds
        '''
        # self.get_account_async() # if account is not initialized, get it

        url = f'{self.client.consts.ApiEndpoint}/{self.client.account["location"]}/Accounts/{self.client.account["properties"]["accountId"]}/' + \
            f'Videos/{video_id}/Index'

        params = {
            'accessToken': self.client.vi_access_token,
            'language': language
        }

        print(f'Checking if video {video_id} has finished indexing...')
        processing = True
        start_time = time.time()
        while processing:
            response = requests.get(url, params=params)

            response.raise_for_status()

            video_result = response.json()
            video_state = video_result.get('state')
            progress = video_result.get('videos')[0].get('processingProgress')
            # print(progress)
            
            # print(f"Video Name:|{video_name}|")
            response_status = requests.post("http://127.0.0.1:5000/uploadVideo_status", json={"video_name": video_name, "progress": str(progress)})
            # print(f"Resposta JSON::::::{response_status.json()}")

            if video_state == 'Processed':
                processing = False
                print(f'The video index has completed. Here is the full JSON of the index for video ID {video_id}: \n{video_result}')
                break
            elif video_state == 'Failed':
                processing = False
                print(f"The video index failed for video ID {video_id}.")
                break

            print(f'The video index state is {video_state} {progress}')

            if timeout_sec is not None and time.time() - start_time > timeout_sec:
                print(f'Timeout of {timeout_sec} seconds reached. Exiting...')
                break

            time.sleep(5) # wait 10 seconds before checking again

    def is_video_processed(self, video_id:str) -> bool:
        self.get_account_async() # if account is not initialized, get it

        url = f'{self.consts.ApiEndpoint}/{self.account["location"]}/Accounts/{self.account["properties"]["accountId"]}/' + \
                f'Videos/{video_id}/Index'
        params = {
            'accessToken': self.vi_access_token,
        }
        response = requests.get(url, params=params)
        response.raise_for_status()

        video_result = response.json()
        video_state = video_result.get('state')

        return video_state == 'Processed'