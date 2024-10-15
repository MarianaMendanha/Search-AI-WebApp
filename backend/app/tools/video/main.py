from client.video_indexer_client import VideoIndexerClient
from client.Consts import Consts
import json
from dotenv import dotenv_values
from pprint import pprint


if __name__ == "__main__":
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
  
  ###################################### Upload Video ######################################
  # By URL
  # client.upload_video(video_name="Example Video", video_path_or_url="https://www.youtube.com/watch?v=w_lDeCxjLQc", wait_for_index=True)
  
  # By FILE
  LocalVideoPath = "C:/Users/MarianaCruz/OneDrive - CrazyTechLabs/Área de Trabalho/AzureOpenAI/AzureAI/VideoIndexerClient/refactor/videos/Dungeon Meshi  Teaser oficial  Netflix.mp4"
  # client.upload_video(video_name="Dungeon Meshi", video_path_or_url=LocalVideoPath, wait_for_index=True, language="Japanese")
  
  ###################################### Generate Prompt ######################################
  video_id = "ibp4wzpywr"
  # video_id = "9jzpx7vrqt"
  content = client.generate_prompt(video_id, operation='get_prompt_content')
  # pprint(content)
  
  # Escrever o JSON no arquivo
  # filename = 'prompt_content/prompt_content.json'
  # with open(filename, 'w') as file:
  #     json.dump(content, file, indent=4)
  
  ###################################### List Videos ######################################
  # client.list_videos()
  
  ###################################### Summary ######################################
  # pprint(client.video_summary(video_id, operation="list"))
  # pprint(client.video_summary(video_id, operation="create"))
  

  