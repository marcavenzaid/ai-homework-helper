# Loading the dotenv should come first before the import so that os.getenv works on other imported python files.
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, redirect, render_template, request, url_for
from processor import Processor
import definitions
import logging
import logging.config
import logger.logger_handler as logger_handler
import os
import definitions
import json
import utilities.utilities as utilities
import config.config as config
from utilities.utilities import ExecutionTimeMeasurer
from utilities.file_deleter import FileDeleter
from playsound import playsound

app = Flask(__name__)

# Disable flask logger so that i can use my own logger. 
# To prevent error from using TimedRotatingFileHandler, because flask logger is accessing the log file as well.
# https://stackoverflow.com/questions/14888799/disable-console-messages-in-flask-server
log = logging.getLogger("werkzeug")
log.disabled = True
# Setup the logger by calling setup_logger(). Only need to call this once in main.
logger_handler.setup_logger()
logger = logging.getLogger(__name__)

processor: Processor = Processor()

error_list = []

@app.route("/", methods=["GET", "POST"])
def index():

    global error_list

    if request.method == "POST":

        error_list = []

        try:
            # Get the form data.
            input_message = request.form.get("inputMessage")
            input_images = request.files.getlist("inputImages[]")
            print("input_images:", input_images)

            # Check how many images are passed.
            # valid_images = []
            # for image in input_images:
            #     if image.filename and image.content_type.startswith('image/'):
            #         valid_images.append(image)
            # print("len(valid_images):", len(valid_images))
            # prev_result_has_images = False
            # if len(valid_images) > 0:
            #     prev_result_has_images = True

            # # Save "True" if result has images, otherwise, save "False" in the output folder.
            # with open(definitions.PREV_RESULT_HAS_IMAGES_OUTPUT_PATH, "w", encoding="utf-8") as file:
            #     file.write(str(prev_result_has_images))

            execution_time_measurer = ExecutionTimeMeasurer()
            execution_time_measurer.start()

            processor.process_thinking(input_message, input_images)
            
            execution_time = execution_time_measurer.get_elapsed_time()
            logger.info(f"Execution time of process_tutor_brain_thinking is: {execution_time} seconds.")

        except Exception as e:
            error_list.append(e)
            logger.exception(f"{e}")
        finally:
            # Play audio file when thinking is completed.
            logger.debug("Playing audio: thinking_complete.wav..")
            audio_path = os.path.join(definitions.AUDIO_PATH, "thinking_complete.wav")
            playsound(audio_path)

        return redirect(url_for("index"))

    input_message = None
    openai_chat_completion_obj = None
    openai_assistant_messages_data_obj = None
    openai_assistant_run_steps_data_obj = None
    merged_output_chat_completion = None

    try:
        input_message, openai_chat_completion_obj, openai_assistant_messages_data_obj, \
        openai_assistant_run_steps_data_obj, merged_output_chat_completion = processor.read_saved_outputs()
    except Exception as e:
        error_list.append(e)
        logger.exception(f"{e}")

    # Format the outputs (change '\n' to '<br>', replace '\\' to '\', etc.)
    input_message, merged_output_chat_completion = processor.format_outputs_for_html(input_message, merged_output_chat_completion)

    answer, step_by_step_solution = processor.extract_answer_step_by_step_solution(merged_output_chat_completion.choices[0].message.content)

    # prev_result_brain_used = ""
    # if os.path.exists(definitions.PREV_RESULT_BRAIN_USED_OUTPUT_PATH):
    #     with open(definitions.PREV_RESULT_BRAIN_USED_OUTPUT_PATH, "r", encoding="utf-8") as file:
    #         prev_result_brain_used = file.read()

    return render_template(
        "index.html", 
        brain=processor.get_brain(),
        # prev_result_brain_used=prev_result_brain_used,
        input_message=input_message,
        openai_chat_completion_obj=openai_chat_completion_obj, 
        openai_assistant_messages_data_obj=openai_assistant_messages_data_obj,
        openai_assistant_run_steps_data_obj=openai_assistant_run_steps_data_obj,
        merged_output_chat_completion=merged_output_chat_completion,
        answer=answer,
        step_by_step_solution=step_by_step_solution,
        asdf=(utilities.string_to_html_paragraphs(merged_output_chat_completion.choices[0].message.content) if merged_output_chat_completion is not None else None),
        error_list=error_list,
        definitions_json=definitions.definitions_json,
    ) 


# Maybe remove this later and just use flask run. 
if __name__ == "__main__":

    cleaner = FileDeleter(folder_path=definitions.IMAGES_INPUT_OUTPUT_PATH, age_in_days=config.FILE_DELETER_AGE_IN_DAYS, max_files=config.FILE_DELETER_MAX_FILES)
    cleaner.delete_files()

    cleaner = FileDeleter(folder_path=definitions.IMAGES_OUTPUT_OUTPUT_PATH, age_in_days=config.FILE_DELETER_AGE_IN_DAYS, max_files=config.FILE_DELETER_MAX_FILES)
    cleaner.delete_files()

    port = os.getenv("PORT") or "5000"
    app_url = f"http://127.0.0.1:{port}"
    print(f"App URL: {app_url}")
    
    # Run the app.
    app.run(debug=True, load_dotenv=False, use_reloader=False, port=port)
