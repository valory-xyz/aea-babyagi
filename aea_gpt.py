import os
import sys
import time
from threading import Thread

from aea_ledger_ethereum import EthereumCrypto

from aea.aea_builder import AEABuilder
from aea.configurations.base import SkillConfig
from aea.crypto.helpers import PRIVATE_KEY_PATH_SCHEMA, create_private_key
from aea.helpers.file_io import write_with_lock
from aea.skills.base import Skill

from agent import build_fsm_and_skill, create_memory

ROOT_DIR = "./dev/autonolas/valory/langchain-experiments/task/"
INPUT_FILE = "input_file"
OUTPUT_FILE = "output_file"
PRIVATE_KEY_FILE = PRIVATE_KEY_PATH_SCHEMA.format(EthereumCrypto.identifier)

# Create a private key
create_private_key(EthereumCrypto.identifier, PRIVATE_KEY_FILE)

def build_aea(first_task: str, objective: str):

    # instantiate the aea builder
    builder = AEABuilder()
    # set the aea name
    builder.set_name("baby_agi")
    # create the shared state object that serves as memory for the actions of the AEA
    memory = create_memory(first_task, objective)
    # add the AEA's private key
    builder.add_private_key(EthereumCrypto.identifier, PRIVATE_KEY_FILE)
    # add the babyagi skill
    _, skill = build_fsm_and_skill(memory)
    # add the skill to the AEA
    builder.add_component_instance(skill)

    print("\033[89m\033[1m" + "\n======== AEA-GPT ONLINE ========" + "\033[0m\033[0m")

    # Create our AEA
    my_aea = builder.build()
    # Set the AEA's agent context
    skill.skill_context.set_agent_context(my_aea.context)
    # update the shared state of the AEA with the memory object we created above
    skill.skill_context.shared_state.update(memory)
    return my_aea


def run(first_task: str, objective: str):
    """Run babyAGI."""

    # Ensure the input and output files do not exist initially
    if os.path.isfile(INPUT_FILE):
        os.remove(INPUT_FILE)
    if os.path.isfile(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    # Create our AEA
    my_aea = build_aea(first_task, objective)

    # Set the AEA running in a different thread
    try:
        t = Thread(target=my_aea.start)
        t.start()
    except KeyboardInterrupt:
        # Shut down the AEA
        my_aea.stop()
        t.join()
        t = None
        print("\033[89m\033[1m" + "\n======== EXIT ========" + "\033[0m\033[0m")


if __name__ == "__main__":
    _, first_task, objective = sys.argv
    try:
        run(first_task, objective)
    except KeyboardInterrupt:
        pass