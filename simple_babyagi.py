"""
Heavily inspired by: https://github.com/yoheinakajima/babyagi

python simple_babyagi.py "develop a task list" "solve world hunger"
"""

import os
import sys
import openai
from typing import List, Tuple, Any
from collections import deque
from dotenv import load_dotenv
import time
# import pinecone (if using pinecone)

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set up OpenAI API key
openai.api_key = OPENAI_API_KEY

STOP_PROCEDURE = False

"""Use Pinecone, not currently setup"""
# PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
# PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
# PINECONE_TABLE = os.getenv("PINECONE_TABLE")

# USE_PINECONE = False

# # Init Pinecone
# pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)

# # Create Pinecone index
# DIMENSION = 1536
# METRIC = "cosine"
# POD_TYPE = "p1"
# if USE_PINECONE and PINECONE_TABLE not in pinecone.list_indexes():
#     pinecone.create_index(
#         PINECONE_TABLE, dimension=DIMENSION, metric=METRIC, pod_type=POD_TYPE
#     )

# Templates used for all the prompt types
# This gives GPT context everytime it is called as to what step in the process of the agent loop is it acting as to provide a corresponding response
task_creation_template = """
You are a task creation AI that uses the result of an execution agent to create new tasks with the following objective: {objective}. 
The last completed task has the result: {result}. This result was based on this task description: {task_description}. 
These are incomplete tasks: {incomplete_tasks}. Based on the result, create new tasks to be completed by the AI system that do 
not overlap with incomplete tasks. Return the result as a list that is not numbered and simply lists each task in its own line, like:

First task
Second task
Third task

Do not include anything else except the list in your response.
"""
task_prioritization_template = """
You are a task prioritization AI tasked with cleaning the formatting of and reprioritizing the following tasks: {task_names}. Consider the ultimate objective of your team: {objective}. 
Do not remove any tasks. Return the result as a numbered list, like:

#. First task
#. Second task

Start the task list with number 1 and do not include anything else except the list in your response.
"""
task_execution_template = """
You are an AI that performs one task based on the following objective: {objective}.\nTake into account these previously completed tasks: {context}...and your assigned task: {task}\n. 
What is your response? Make sure to respond with a detailed solution to the assigned task you have been given only, and do not address any other tasks or make any lists. 
your response should be in paragraph form.
"""
task_stop_or_not_template = """
You are an AI that assess task completion for the following objective: {objective}. Take into account these previously completed tasks: {context}.
Has the objective been achieved? Answer with only yes or no. Only answer with yes if you think this is the best answer possible.
"""


def task_execution_prompt_builder(globals_: dict) -> str:
    """
    This function builds and returns the execution prompt for GPT to take in as input when executing a task.
    It also prints the next task in the task list.

    Args:
        globals_ (dict): The globals dictionary
    
    Returns:
        str: The prompt for GPT task execution
    """
    task_list = globals_["task_list"]
    task = task_list.popleft()
    globals_["current_task"] = task

    print("\033[92m\033[1m" + "\n***** NEXT TASK *****\n" + "\033[0m\033[0m")
    print(str(task["id"]) + ": " + task["name"])

    context = get_context(globals_)
    return task_execution_template.format(
        objective=globals_["objective"], task=globals_["current_task"], context=context
    )


def task_execution_handler(response: str, globals_: dict) -> None:
    """
    This function handles the GPT response corresponding to the last task execution, allows for the
    result to be further enriched and prints the resultant GPT response from executing the task. It also prints the result

    Args:
        response (str): The GPT response from task execution
        globals_ (dict): The globals dictionary
    """
    enriched_result = {
        "data": response
    }  # This is where you should enrich the result if needed
    globals_["result"] = enriched_result

    """Use Pinecone, not currently setup"""
    #id_ = globals_["current_task"]["id"]
    #result_id = f"result_{id_}"
    #vector = enriched_result["data"]  # extract the actual result from the dictionary
    #if USE_PINECONE:
    #    index = pinecone.Index(index_name=PINECONE_TABLE)
    #    index.upsert(
    #        [
    #            (
    #                result_id,
    #                get_ada_embedding(vector),
    #                {"task": globals_["current_task"]["name"], "result": response},
    #            )
    #        ]
    #    )

    print("\033[93m\033[1m" + "\n***** TASK RESULT *****\n" + "\033[0m\033[0m")
    print(globals_["result"]["data"])

    return "done"


def task_creation_prompt_builder(globals_: dict) -> str:
    """
    This function builds and returns the prompt for GPT task creation so GPT can create task lists.

    Args:
        globals_ (dict): The globals dictionary

    Returns:
        str: The prompt for GPT task creation
    """
    incomplete_tasks = [t["name"] for t in globals_["task_list"]]
    return task_creation_template.format(
        objective=globals_["objective"],
        result=globals_["result"],
        task_description=globals_["current_task"].get("name", "default"),
        incomplete_tasks=incomplete_tasks,
    )


def task_creation_handler(response: str, globals_: dict):
    """
    This function handles the GPT response corresponding to the task creation prompt built by the task creation prompt builder and
    prints the resultant GPT response that is creating new tasks.

    Args:
        response (str): The GPT response from task creation
        globals_ (dict): The globals dictionary

    Returns:
        str: The status of the task creation handler

    """
    new_tasks = response.split("\n")
    if len(globals_["task_list"]) > 0:
        id_ = globals_["task_list"][-1]["id"] + 1
    else:
        id_ = 1
    task_list = [{"id": id_ + i, "name": task_name} for i, task_name in enumerate(new_tasks)]
    globals_["task_list"] = deque(task_list)

    print("\033[89m\033[1m" + "\nTASK LIST:" + "\033[0m\033[0m")
    for t in task_list:
        print(t["name"])
    
    return "done"


def task_prioritization_prompt_builder(globals_: dict) -> str:
    """
    This function builds and returns the prompt for GPT task prioritization so existing tasks can be re-prioritized.

    Args:
        globals_ (dict): The globals dictionary

    Returns:
        str: The prompt for GPT task prioritization
    """
    task_list = globals_["task_list"]
    current_task = globals_["current_task"]
    task_names = [t["name"] for t in task_list]
    current_task_id = int(current_task["id"]) + 1
    objective = globals_["objective"]
    return task_prioritization_template.format(
        task_names=task_names, objective=objective, starting_id=current_task_id
    )


def task_prioritization_handler(response: str, globals_: dict):
    """
    This function handles the GPT response corresponding to the task prioritization prompt built by the task prioritization prompt builder and
    prints the resultant GPT response that is re-prioritizing existing tasks.
    """
    new_tasks = response.split("\n")
    task_list = deque([])
    for task_string in new_tasks:
        task_parts = task_string.strip().split(".", 1)
        if len(task_parts) == 2:
            task_id = int(task_parts[0].strip())
            task_name = task_parts[1].strip()
            task_list.append({"id": task_id, "name": task_name})
    globals_["task_list"] = task_list
    globals_["current_task"] = {}
    print("\033[94m\033[1m" + "\n***** RE-PRIORITIZED TASK LIST *****\n" + "\033[0m\033[0m")
    for t in task_list:
        print(str(t["id"]) + ": " + t["name"])
    return "done"


def get_ada_embedding(text):
    text = text.replace("\n", " ")
    return openai.Embedding.create(input=[text], model="text-embedding-ada-002")[
        "data"
    ][0]["embedding"]


def get_context(globals_: dict) -> List[Tuple[str]]:
    """
    Get the current context (task list) from the dictionary state variable, globals_
    """
    """Use Pinecone, not currently setup"""
    #if USE_PINECONE:
    #    query = objective
    #    query_embedding = get_ada_embedding(query)
    #    index = pinecone.Index(index_name=PINECONE_TABLE)
    #    results = index.query(query_embedding, top_k=5, include_metadata=True)
    #    sorted_results = sorted(results.matches, key=lambda x: x.score, reverse=True)
    #    return [(str(item.metadata["task"])) for item in sorted_results]
    return globals_["task_list"]


def task_stop_or_not_prompt_builder(globals_: dict) -> str:
    """
    This function builds and returns the task stop or not prompt for GPT in order to reason about the objective completeness when 
    the user stops the agent loop.

    Args:
        globals_ (dict): The globals dictionary

    Returns:
        str: The prompt for GPT task stop or not
    """
    context = get_context(globals_)
    return task_stop_or_not_template.format(
        objective=globals_["objective"], context=context
    )


def task_stop_or_not_handler(response: str, globals_: dict) -> None:
    """
    This function handles the GPT response corresponding to the task stop or not prompt built by the task stop or not prompt builder and
    prints the resultant GPT response that is reasoning about the objective completeness when the user stops the agent loop.
    """
    globals_["keep_going"] = response.strip().lower() != "yes"
    print(
        "\033[94m\033[1m" + "\n*****TASK CONTINUATION*****\n" + "\033[0m\033[0m"
    )
    print(globals_["keep_going"])
    return "done" if globals_["keep_going"] else "stop"


# Definition of the action types for the simple agent
action_types = {
    "task_creation": {
        "prompt_builder": task_creation_prompt_builder,
        "handler": task_creation_handler,
    },
    "task_prioritization": {
        "prompt_builder": task_prioritization_prompt_builder,
        "handler": task_prioritization_handler,
    },
    "task_execution": {
        "prompt_builder": task_execution_prompt_builder,
        "handler": task_execution_handler,
    },
    "task_stop_or_not": {
        "prompt_builder": task_stop_or_not_prompt_builder,
        "handler": task_stop_or_not_handler,
    },
}


def executor(globals_: dict, agent_type: str) -> None:
    """
    execute an action using simple agent

    Args:
        globals_ (dict): The globals dictionary
        agent_type (str): The action type to execute
    """
    # load the action type into "agent"
    agent = action_types[agent_type]
    # build the prompt for the corresponding action type
    builder_ = agent["prompt_builder"]
    # create the corresponding prompt for GPT to execute the action type "agent" and load it into "prompt"
    prompt = builder_(globals_)
    # call GPT with the corresponding "prompt" to execute the action and load the response from the "prompt" into "response"
    response = openai_call(prompt)
    # handle the response from GPT for the corresponding action type "agent"
    handler_ = agent["handler"]
    handler_(response, globals_)


def main(first_task: str, objective: str):
    # initialize the globals dictionary
    # this is simple_agent's state variable which is used to keep track of the task list, current task, and the objective so GPT can reason about them
    globals_ = {
        "objective": objective,
        "task_list": deque([]),
        "current_task": {},
        "result": {"data": ""},
        "keep_going": True,
    }
    # initialize the task list with the first task
    globals_["task_list"].append({"id": 1, "name": first_task})

    print("\033[89m\033[1m" + "\n======== Simple Loop babyAGI ONLINE ========" + "\033[0m\033[0m")

    # simple agent loop
    while globals_["keep_going"]:
        # execution
        executor(globals_, "task_execution")
        # creation
        executor(globals_, "task_creation")
        # re-prioritization
        executor(globals_, "task_prioritization")
        if STOP_PROCEDURE:
            executor(globals_, "task_stop_or_not")
        time.sleep(1)


def openai_call(
    prompt: str, use_gpt4: bool = False, temperature: float = 0.5, max_tokens: int = 200
):
    if not use_gpt4:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        return response.choices[0].text.strip()
    else:
        messages = [{"role": "user", "content": prompt}]
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            n=1,
            stop=None,
        )
        return response.choices[0].message.content.strip()


if __name__ == "__main__":
    _, first_task, objective = sys.argv
    try:
        main(first_task, objective)
    except KeyboardInterrupt:
        print("\033[89m\033[1m" + "\n======== EXIT ========" + "\033[0m\033[0m")
        pass
