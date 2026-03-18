import logging
from brain.brain import BrainConfig
import xml.etree.ElementTree as ET
import time
import pip._vendor.requests as requests
from werkzeug.utils import secure_filename
import base64
import os
import definitions

logger = logging.getLogger(__name__)

class TutorBrainChatCompletionAndAssistant:

    def __init__(self, openai_client, brain_config: BrainConfig):
        self._openai_client = openai_client
        self._brain_config = brain_config
        self._openai_chat_completion_and_assistant = self._brain_config.get_openai_chat_completion_and_assistant()
        self._openai_chat_completion = self._openai_chat_completion_and_assistant.get('openai_chat_completion')
        self._openai_assistant = self._openai_chat_completion_and_assistant.get("openai_assistant")
        self._merger_openai_chat_completion = self._openai_chat_completion_and_assistant.get("merger_openai_chat_completion")

        try:
            # Chat Completion
            self._chat_completion_model = self._openai_chat_completion.get("model")
            self._chat_completion_system_message = self._openai_chat_completion['messages'][0].get('content')
            self._chat_completion_temperature = float(self._openai_chat_completion.get("temperature"))
            self._chat_completion_max_tokens = int(self._openai_chat_completion.get("max_tokens"))
            self._chat_completion_top_p = float(self._openai_chat_completion.get("top_p"))
            self._chat_completion_frequency_penalty = float(self._openai_chat_completion.get("frequency_penalty"))
            self._chat_completion_presence_penalty = float(self._openai_chat_completion.get("presence_penalty"))

            # Assistant
            self._assistant_id = self._openai_assistant.get("tutor_statistics_and_probability") # The assistant_id is created using the OpenAI Assistants Playground.
            self._assistant = self._openai_client.beta.assistants.retrieve(assistant_id=self._assistant_id) # Retrieve the assistant, based on the assistant_id.
            self._assistant_system_message = self._assistant.instructions # Retrieve the system message.

            # Merger Chat Completion
            self._merger_model = self._merger_openai_chat_completion.get("model")
            self._merger_system_message = self._merger_openai_chat_completion['messages'][0].get('content')
            self._merger_temperature = float(self._merger_openai_chat_completion.get("temperature"))
            self._merger_max_tokens = int(self._merger_openai_chat_completion.get("max_tokens"))
            self._merger_top_p = float(self._merger_openai_chat_completion.get("top_p"))
            self._merger_frequency_penalty = float(self._merger_openai_chat_completion.get("frequency_penalty"))
            self._merger_presence_penalty = float(self._merger_openai_chat_completion.get("presence_penalty"))
        except ET.ParseError:
            logger.debug("Error while parsing XML.")
        except ValueError as e:
            logger.debug(f"Value error: {e}")
        except AttributeError as e:
            logger.debug(f"Attribute error: {e}")
        except Exception as e:
            logger.debug(f"Unexpected error: {e}")

        self._chat_completion_conversation = list()
        self.initialize_chat_completion_conversation()


    def initialize_chat_completion_conversation(self):
        logger.debug("Initializing chat completion conversation..")
        self._chat_completion_conversation.append({
            "role": "system", 
            "content": self._chat_completion_system_message
        })
        logger.debug(f"Initial message added to conversation (role=system).\nConversation: {self._chat_completion_conversation}")


    def reset_conversation(self):
        logger.debug("Resetting conversation..")
        self._chat_completion_conversation.clear()
        self.initialize_chat_completion_conversation()
        logger.debug(f"Conversation has been resetted.") 


    def think(self, input_message, base64_images):
        self.reset_conversation()

        logger.info(f"Brain is thinking..")

        self._chat_completion_conversation.append({
            "role": "user", 
            "content": input_message
        })
        logger.debug(f"A new message is added to the conversation (role=user).\nConversation: {self._chat_completion_conversation}")

        try:
            # Chat Completion will think about the process of solving the problem.
            if len(base64_images) > 0:
                chat_completion = self._gpt_chat_completion_base64(input_message, base64_images)
            else:
                chat_completion = self._gpt_chat_completion(self._chat_completion_conversation)

            input_and_chat_completion_result = "[Question]\n" + input_message
            if len(base64_images) > 0:
                input_and_chat_completion_result += "\n\n" + chat_completion['choices'][0]['message']['content']
            else:
                input_and_chat_completion_result += "\n\n" + chat_completion.choices[0].message.content
            logger.debug(f"Input for assistant: {input_and_chat_completion_result}")

            # Assistant will solve the problem using the process of solving given by Chat Completion.
            assistant_messages, assistant_run_steps = self._gpt_assistant(input_and_chat_completion_result)

            # Merger will combine, rewrite, and polish the process of solving and solution given by chat completion and assistant.
            merged_output_chat_completion = self._merger_chat_completion(input_and_chat_completion_result, assistant_messages)
        except Exception as e:
            raise e

        return chat_completion, assistant_messages, assistant_run_steps, merged_output_chat_completion


    def _merger_chat_completion(self, input_and_chat_completion_result, assistant_messages):
        """
        Merges the result from both chat completion and assistant.
        """

        messages = list()
        messages.append({
            "role": "system", 
            "content": self._merger_system_message
        })

        merged_outputs = input_and_chat_completion_result

        assistant_messages_data = assistant_messages.data

        assistant_messages_data_iterator = reversed(assistant_messages_data)
        next(assistant_messages_data_iterator, None)  # Advance the iterator once to skip the first item. (The first item is the input.)
        for message in assistant_messages_data_iterator:
            for content in message.content:
                if content.type == "text":
                    merged_outputs += "\n\n" + content.text.value
                elif content.type == "image_file":
                    # Download the image files.
                    image_data = self._openai_client.files.content(content.image_file.file_id)
                    image_data_bytes = image_data.read()
                    image_path = definitions.IMAGES_OUTPUT_OUTPUT_PATH + content.image_file.file_id + ".png"
                    if not os.path.exists(image_path):
                        with open(image_path, "wb") as file:
                            file.write(image_data_bytes)
                    image_name = content.image_file.file_id + ".png"

                    image_placeholder = "image:[" + image_name + "]"

                    merged_outputs += "\n\n" + image_placeholder

        logger.debug(f"merged_outputs: {merged_outputs}")

        messages.append({
            "role": "user", 
            "content": merged_outputs
        })

        input_and_chat_completion_result = self._gpt_chat_completion(messages)

        return input_and_chat_completion_result


    def _gpt_chat_completion(self, messages):
        try:
            chat_completion = self._openai_client.chat.completions.create(
                model=self._chat_completion_model,
                messages=messages,
                temperature=self._chat_completion_temperature,
                max_tokens=self._chat_completion_max_tokens,
                top_p=self._chat_completion_top_p,
                frequency_penalty=self._chat_completion_frequency_penalty,
                presence_penalty=self._chat_completion_presence_penalty
            )
        except Exception as e:
            raise e

        logger.info(f"chat_completion: {chat_completion}")

        return chat_completion
    

    def _gpt_chat_completion_base64(self, message, base64_images):
        """
        GPT chat completion with local image input.
        """

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._openai_client.api_key}"
        }

        content = [
            {
                "type": "text",
                "text": message
            }
        ]
        # Dynamically add images to the content list
        for base64_image in base64_images:
            image_content = {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            }
            content.append(image_content)

        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ],
            "temperature": self._chat_completion_temperature,
            "max_tokens": self._chat_completion_max_tokens,
            "top_p": self._chat_completion_top_p,
            "frequency_penalty": self._chat_completion_frequency_penalty,
            "presence_penalty": self._chat_completion_presence_penalty
        }

        try:
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        except Exception as e:
            raise e

        return response.json()
    

    def _gpt_assistant(self, content, TIMEOUT=600, RUN_CHECK_INTERVAL=5):
        # Create a Thread
        thread = self._openai_client.beta.threads.create()

        # Add a Message to a Thread
        message = self._openai_client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=content
        )

        # Run the Assistant
        run = self._openai_client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=self._assistant.id,
        )

        # Display the Assistant's Response
        time_passed = 0
        while time_passed < TIMEOUT:
            run = self._openai_client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )

            # Check status.
            logger.debug(f"(Time passed: {time_passed}s) --- Run status: {run.status}")
            if run.status in ["queued", "in_progress", "requires_action", "cancelling"]:
                pass
            if run.status in ["cancelled", "expired", "failed"]:
                break
            if run.status in ["completed"]:
                messages = self._openai_client.beta.threads.messages.list(
                    thread_id=thread.id
                )

                run_steps = self._openai_client.beta.threads.runs.steps.list(
                    thread_id=thread.id,
                    run_id=run.id
                )

                logger.info(f"assistant messages: {messages}")
                logger.info(f"assistant run_steps: {run_steps}")

                return messages, run_steps
            
            time.sleep(RUN_CHECK_INTERVAL)
            time_passed += RUN_CHECK_INTERVAL
        
        if time_passed >= TIMEOUT:
            logger.error(f"Error: Run did not complete within the TIMEOUT period ({TIMEOUT}s).")


    def get_chat_completion_model(self):
        return self._chat_completion_model
    

    def get_chat_completion_system_message(self):
        return self._chat_completion_system_message
    

    def get_assistant(self):
        return self._assistant


    def get_assistant_system_message(self):
        return self._assistant_system_message
    
