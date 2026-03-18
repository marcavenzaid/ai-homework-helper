import logging
from brain.brain import BrainConfig
import xml.etree.ElementTree as ET
import time

logger = logging.getLogger(__name__)

class BrainAssistant:
    
# # This is commented out because it creates an assistant every run. 
# # Instead I decided to use the assistant_id of the assistant I created using the OpenAI Assistants Playground.
#     def __init__(self, brain_config: BrainConfig):
#         self._brain_config = brain_config

#         Skip this and just use the assistant I created on the platform.openai assistants playground.
#         Create an Assistant
#         self._assistant = client.beta.assistants.create(
#             name="Tutor - Statistics and Probability",
#             instructions="""You are a personal Statistics and Probability tutor. 
# Answer questions or write and run code to answer questions if necessary.""",
#             model="gpt-4-1106-preview",
#             tools=[{"type": "code_interpreter"}]
#         )

    def __init__(self, client, brain_config: BrainConfig):
        self._client = client
        self._brain_config = brain_config
        self._brain_openai_assistant_tree = self._brain_config.get_tutor_brain_openai_assistant_tree()

        try:
            # The assistant_id is created using the OpenAI Assistants Playground.
            self._assistant_id = self._brain_openai_assistant_tree.find("tutor_statistics_and_probability").text
            # Retrieve the assistant, based on the assistant_id.
            self._assistant = self._client.beta.assistants.retrieve(assistant_id=self._assistant_id)
            # Retrieve the system message.
            self._system_message = self._assistant.instructions
        except ET.ParseError:
            logger.debug("Error while parsing XML.")
        except ValueError as e:
            logger.debug(f"Value error: {e}")
        except AttributeError as e:
            logger.debug(f"Attribute error: {e}")
        except Exception as e:
            logger.debug(f"Unexpected error: {e}")


    def think(self, content, TIMEOUT=600, RUN_CHECK_INTERVAL=5):
        logger.info(f"Brain is thinking..")

        # Create a Thread
        thread = self._client.beta.threads.create()

        # Add a Message to a Thread
        message = self._client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=content
        )

        # Run the Assistant
        run = self._client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=self._assistant.id,
        )

        # Display the Assistant's Response
        time_passed = 0
        while time_passed < TIMEOUT:
            run = self._client.beta.threads.runs.retrieve(
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
                messages = self._client.beta.threads.messages.list(
                    thread_id=thread.id
                )

                run_steps = self._client.beta.threads.runs.steps.list(
                    thread_id=thread.id,
                    run_id=run.id
                )

                logger.info(f"messages: {messages}")
                logger.info(f"run_steps: {run_steps}")

                return messages, run_steps
            
            time.sleep(RUN_CHECK_INTERVAL)
            time_passed += RUN_CHECK_INTERVAL
        
        if time_passed >= TIMEOUT:
            logger.error(f"Error: Run did not complete within the TIMEOUT period ({TIMEOUT}s).")


    def get_assistant(self):
        return self._assistant
    

    def get_system_message(self):
        return self._system_message
    