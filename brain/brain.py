from openai import OpenAI
from brain.brain_config import BrainConfig
from brain.tutor_brain_chat_completion_and_assistant import TutorBrainChatCompletionAndAssistant
import logging
import os

logger = logging.getLogger(__name__)

class Brain():

    def __init__(self):
        # defaults to getting the key using os.environ.get("OPENAI_API_KEY")
        # if you saved the key under a different environment variable name, you can do something like:
        # client = OpenAI(
        #   api_key=os.environ.get("CUSTOM_ENV_NAME"),
        # )
        self._openai_client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY")
        )

        self._brain_config = BrainConfig()

        # Tutor brain
        self._chat_completion_and_assistant = TutorBrainChatCompletionAndAssistant(self._openai_client, self._brain_config)


    def get_openai_client(self):
        return self._openai_client


    def get_brain_config(self):
        return self._brain_config


    def get_chat_completion_and_assistant(self):
        return self._chat_completion_and_assistant


    # def get_tutor_brain_chat_completion(self):
    #     return self._tutor_brain_chat_completion
    

    # def get_tutor_brain_assistant(self):
    #     return self._tutor_brain_assistant
    

    # def get_image_brain_chat_completion(self):
    #     return self._image_brain_chat_completion
