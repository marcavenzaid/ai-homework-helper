import logging
from brain.brain import BrainConfig
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

class TutorBrainChatCompletion:

    def __init__(self, openai_client, brain_config: BrainConfig):
        self._openai_client = openai_client
        self._brain_config = brain_config
        self._tutor_brain_openai_chat_completion_tree = self._brain_config.get_tutor_brain_openai_chat_completion_tree()

        try:
            self._model = self._tutor_brain_openai_chat_completion_tree.find("model").text
            self._system_message = self._tutor_brain_openai_chat_completion_tree.find("messages")[0].find("content").text
            self._temperature = float(self._tutor_brain_openai_chat_completion_tree.find("temperature").text)
            self._max_tokens = int(self._tutor_brain_openai_chat_completion_tree.find("max_tokens").text)
            self._top_p = float(self._tutor_brain_openai_chat_completion_tree.find("top_p").text)
            self._frequency_penalty = float(self._tutor_brain_openai_chat_completion_tree.find("frequency_penalty").text)
            self._presence_penalty = float(self._tutor_brain_openai_chat_completion_tree.find("presence_penalty").text)
        except ET.ParseError:
            logger.debug("Error while parsing XML.")
        except ValueError as e:
            logger.debug(f"Value error: {e}")
        except AttributeError as e:
            logger.debug(f"Attribute error: {e}")
        except Exception as e:
            logger.debug(f"Unexpected error: {e}")

        self._conversation = list()
        self.initialize_conversation()


    def initialize_conversation(self):
        logger.debug("Initializing conversation..")
        self._conversation.append({
            "role": "system", 
            "content": self._system_message
        })
        logger.debug(f"Initial message added to conversation (role=system).\nConversation: {self._conversation}")


    def reset_conversation(self):
        logger.debug("Resetting conversation..")
        self._conversation.clear()
        self.initialize_conversation()
        logger.debug(f"Conversation has been resetted.")    


    def think(self, message):
        logger.info(f"Brain is thinking..")

        self._conversation.append({
            "role": "user", 
            "content": message
        })

        logger.debug(f"A new message is added to the conversation (role=user).\nConversation: {self._conversation}")

        try:
            chat_completion = self._gpt_chat_completion()
        except Exception as e:
            raise e
        
        logger.info(f"chat_completion: {chat_completion}")

        return chat_completion


    def _gpt_chat_completion(self):
        try:
            chat_completion = self._openai_client.chat.completions.create(
                model=self._model,
                messages=self._conversation,
                temperature=self._temperature,
                max_tokens=self._max_tokens,
                top_p=self._top_p,
                frequency_penalty=self._frequency_penalty,
                presence_penalty=self._presence_penalty
            )
        except Exception as e:
            raise e

        return chat_completion


    def get_model(self):
        return self._model
    

    def get_system_message(self):
        return self._system_message
    
