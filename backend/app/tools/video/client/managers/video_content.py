from app.tools.video.client.interfaces.video_content import VideoContentManagerInterface
from typing import Optional
import time, requests

class VideoContentManager(VideoContentManagerInterface):
    def __init__(self, client):
        self.client = client
        
    def get_raw_insight(self, video_id: str) -> dict:
        '''
        Gets the video index. Calls the index API
        (https://api-portal.videoindexer.ai/api-details#api=Operations&operation=Search-Videos)
        Prints the video metadata, otherwise throws an exception

        :param video_id: The video ID
        '''
        print(f"Getting Raw insights for video with ID {video_id}")

        url =   f'{self.client.consts.ApiEndpoint}/{self.client.account["location"]}/Accounts/{self.client.account["properties"]["accountId"]}/' + \
                f'Videos/{video_id}/Index'

        params = {
            'accessToken': self.client.vi_access_token
        }

        response = requests.get(url, params=params)

        response.raise_for_status()

        search_result = response.json()
        print(f'Here are the search results: \n{search_result}')
        return search_result
    
    def get_prompt(self, video_id: str, promptStyle: str = 'Full', timeout_sec:Optional[int]=None, check_alreay_exists=True) -> Optional[dict]:
        '''
        Gets the prompt content for the video, waits until the prompt content is ready.
        If the prompt content is not ready within the timeout, it will return None.

        :param video_id: The video ID
        :param timeout_sec: The timeout in seconds
        :param check_alreay_exists: If True, checks if the prompt content already exists
        :return: The prompt content for the video, otherwise None
        '''

        if check_alreay_exists:
            prompt_content = self.__get_prompt_content(video_id, raise_on_not_found=False)
            if prompt_content is not None:
                print(f'Prompt content already exists for video ID {video_id}.')
                return prompt_content

        """ modelName Allowed values: Llama2 / Phi2 / GPT3_5Turbo / GPT4 """
        url =   f'{self.client.consts.ApiEndpoint}/{self.client.account["location"]}/Accounts/{self.client.account["properties"]["accountId"]}/' + \
                f'Videos/{video_id}/PromptContent?modelName=GPT3_5Turbo&promptStyle=Full'

        headers = {
            "Content-Type": "application/json"
            }

        """ promptStyle Allowed values: Full / Summarized """
        params = {
            'accessToken': self.client.vi_access_token,
            'promptStyle': promptStyle
        }

        print(f"Prompt content generation for {video_id=} started...")
        response = requests.post(url, headers=headers, params=params)

        response.raise_for_status()

        start_time = time.time()
        prompt_content = None
        while prompt_content is None:
            prompt_content = self.__get_prompt_content(video_id, raise_on_not_found=False)

            if timeout_sec is not None and time.time() - start_time > timeout_sec:
                print(f'Timeout of {timeout_sec} seconds reached. Exiting...')
                break

            print('Prompt content is not ready yet. Waiting 10 seconds before checking again...')
            time.sleep(10)

        return prompt_content
    
    def __get_prompt_content(self, video_id:str, raise_on_not_found:bool=True) -> Optional[dict]:
        '''
        Calls the promptContent API
        Get the prompt content for the video.
        Raises an exception or returns None if the prompt content is not found according to the `raise_on_not_found`.

        :param video_id: The video ID
        :param raise_on_not_found: If True, raises an exception if the prompt content is not found.
        :return: The prompt content for the video, otherwise None
        '''

        url =   f'{self.client.consts.ApiEndpoint}/{self.client.account["location"]}/Accounts/{self.client.account["properties"]["accountId"]}/' + \
                f'Videos/{video_id}/PromptContent'

        headers = {
            "Content-Type": "application/json"
            }

        params = {
            'accessToken': self.client.vi_access_token
        }

        response = requests.get(url, params=params)
        if not raise_on_not_found and response.status_code == 404:
            return None

        response.raise_for_status()

        return response.json()