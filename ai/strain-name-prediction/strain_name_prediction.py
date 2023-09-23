import openai
import os


def train_strain_name_model():
    """Train a GPT model to predict strain names given product names or descriptions."""

    # TODO: Use lab results with both product name and strain name
    # to create a training dataset.
    training_data = []
    strain_name = ''
    product_name = ''
    training_data.append({
        'prompt': 'Product name: %s' % product_name,
        'completion': '{"strain_name": "%s"}' % strain_name,
    })

    # Use the CLI:
    # openai api fine_tunes.create -t <TRAIN_FILE_ID_OR_PATH> -m <BASE_MODEL>

    # Resume the job if the stream is interrupted:
    # openai api fine_tunes.follow -i <YOUR_FINE_TUNE_JOB_ID>

    # create_args = {
    #     "training_file": training_file_id,
    #     "validation_file": validation_file_id,
    #     "model": "davinci",
    #     "n_epochs": 15,
    #     "batch_size": 3,
    #     "learning_rate_multiplier": 0.3
    # }

    # response = openai.FineTune.create(**create_args)
    # job_id = response["id"]
    # status = response["status"]

    # print(f'Fine-tunning model with jobID: {job_id}.')
    # print(f"Training Response: {response}")
    # print(f"Training Status: {status}")


def predict_strain_name():
    """Use OpenAI to predict strain name given product name or description."""

    # Initialize the OpenAI API.
    openai.api_key = os.environ.get('OPENAI_API_KEY')
    
    # TODO: Format prompt.
    system_prompt = 'Return the strain name as JSON, e.g. {"strain_name": "Blue Dream"}'
    system_prompt_2 = 'Handle multiple strains as JSON, e.g. {"strain_name": "Blue Dream x GSC"}'
    prompt = "Given the following product name and description, predict the strain name."
    prompt += "\n\nProduct name: %s\n\nProduct description: %s\n\n" % (product_name, product_description)

    # Retrieve the finetuned model
    # fine_tuned_model = result.fine_tuned_model
    # print(fine_tuned_model)

    # TODO: Query the fine-tuned model.


import signal
import datetime

# def signal_handler(sig, frame):
# 	status = openai.FineTune.retrieve(job_id).status
# 	print(f"Stream interrupted. Job is still {status}.")
# 	return

# print(f'Streaming events for the fine-tuning job: {job_id}')
# signal.signal(signal.SIGINT, signal_handler)

# events = openai.FineTune.stream_events(job_id)
# try:
# 	for event in events:
#     	print(f'{datetime.datetime.fromtimestamp(event["created_at"])} {event["message"]}')

# except Exception:
# 	print("Stream interrupted (client disconnected).")

# import time

# status = openai.FineTune.retrieve(id=job_id)["status"]
# if status not in ["succeeded", "failed"]:
# 	print(f'Job not in terminal status: {status}. Waiting.')
# 	while status not in ["succeeded", "failed"]:
#     	time.sleep(2)
#     	status = openai.FineTune.retrieve(id=job_id)["status"]
#     	print(f'Status: {status}')
# else:
# 	print(f'Finetune job {job_id} finished with status: {status}')

# print('Checking other finetune jobs in the subscription.')
# result = openai.FineTune.list()
# print(f'Found {len(result.data)} finetune jobs.')
