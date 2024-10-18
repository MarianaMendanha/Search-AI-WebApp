from app.tools.video.client.interfaces.video_summary import VideoSummaryManagerInterface
from typing import Optional
import time, requests

class VideoSummaryManager(VideoSummaryManagerInterface):
    def __init__(self, client):
        self.client = client
        
    def list_summaries(self, video_id: str, summary_id: Optional[str] = None) -> Optional[dict]:
        sum_id, params = '', {}
        if summary_id is None:
            sum_id = ''
            params = {
                'pageNumber': "0",
                'pageSize': "20",
                'accessToken': self.client.vi_access_token
            }
        else:
            sum_id = f'/{summary_id}'
            params = {
                'accessToken': self.client.vi_access_token
            }
            
        url = f'{self.client.consts.ApiEndpoint}/{self.client.account["location"]}/Accounts/{self.client.account["properties"]["accountId"]}/Videos/{video_id}/Summaries/Textual{sum_id}'
        
        headers = {
            "Content-Type": "application/json"
            }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {e}")
            raise
        except requests.exceptions.RequestException as e:
            print(f"Error occurred: {e}")
            raise
        
    def create_summary(self, video_id: str, model_name: str = "gpt-35-turbo", sum_len: str = "Long", sum_style: str = "Neutral") -> Optional[dict]:
        """
        Cria um resumo textual para um vídeo com base nos parâmetros de comprimento e estilo especificados.

        :param video_id: Identificador único do vídeo para o qual você deseja criar um resumo textual.
        :type video_id: str
        :param name: Nome da implantação para o resumo do vídeo.
        :type name: str
        :param sum_len: Comprimento do resumo do vídeo. Valores permitidos: "Medium", "Short", "Long".
        :type sum_len: str
        :param sum_style: Estilo do resumo do vídeo. Valores permitidos: "Neutral", "Casual", "Formal". Padrão é "Neutral".
        :type sum_style: str (opcional)
        :return: Dicionário contendo os dados JSON da resposta.
        :rtype: dict
        :raises ValueError: Se os valores de sum_len ou sum_style forem inválidos.
        :raises HTTPError: Se a solicitação HTTP falhar.
        """
        
        url = f'{self.client.consts.ApiEndpoint}/{self.client.account["location"]}/Accounts/{self.client.account["properties"]["accountId"]}/Videos/{video_id}/Summaries/Textual'
        
        self.__validate_parameters(sum_len, sum_style, model_name)
        
        params = {
            'accessToken': self.client.vi_access_token,
            'deploymentName': model_name,
            'length': sum_len,
            'style': sum_style
        }
        
        try:
            response = requests.post(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {e}")
            raise
        except requests.exceptions.RequestException as e:
            print(f"Error occurred: {e}")
            raise

    def __validate_parameters(self, sum_len: Optional[str] = None, sum_style: Optional[str] = None, model_name: Optional[str] = None):
        allowed_lengths = ["Medium", "Short", "Long"]
        if sum_len is not None and sum_len not in allowed_lengths:
            raise ValueError(f"Invalid length value: {sum_len}. Allowed values are: {', '.join(allowed_lengths)}")
        
        allowed_styles = ["Neutral", "Casual", "Formal"]
        if sum_style is not None and sum_style not in allowed_styles:
            raise ValueError(f"Invalid style value: {sum_style}. Allowed values are: {', '.join(allowed_styles)}")
        
        allowed_models = ["gpt-35-turbo", "gpt-4"]
        if model_name is not None and model_name not in allowed_models:
            raise ValueError(f"Invalid model name: {model_name}. Allowed values are: {', '.join(allowed_models)}")