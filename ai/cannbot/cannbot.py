"""
CannBot | Cannlytics
Copyright (c) 2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 5/28/2023
Updated: 6/1/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

"""
from openai import OpenAI

# TODO: Train GPT model on Cannlytics documentation.
# assistant = client.beta.assistants.create(
#     name="Math Tutor",
#     instructions="You are a personal math tutor. Write and run code to answer math questions.",
#     tools=[{"type": "code_interpreter"}],
#     model="gpt-4-1106-preview"
# )


# TODO: Chat with CannBot.
# thread = client.beta.threads.create()
# message = client.beta.threads.messages.create(
#     thread_id=thread.id,
#     role="user",
#     content="I need to solve the equation `3x + 11 = 14`. Can you help me?"
# )
# run = client.beta.threads.runs.create(
#   thread_id=thread.id,
#   assistant_id=assistant.id,
#   instructions="Please address the user as Jane Doe. The user has a premium account."
# )

# Retrieve the run status.
# run = client.beta.threads.runs.retrieve(
#   thread_id=thread.id,
#   run_id=run.id
# )

# Display a run.
# messages = client.beta.threads.messages.list(
#   thread_id=thread.id
# )
