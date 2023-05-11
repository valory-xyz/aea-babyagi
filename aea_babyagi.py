import sys
from threading import Thread

# AEA dependencies
from aea_ledger_ethereum import EthereumCrypto
from aea.aea_builder import AEABuilder
from aea.crypto.helpers import PRIVATE_KEY_PATH_SCHEMA, create_private_key

# agent_babyagi dependencies
# build_fsm_and_skill builds the skill we add to the AEA
# create_memory creates the shared state used by the AEA to move between actions
from agent_babyagi import build_fsm_and_skill, create_memory

# Create a dummy private key for the AEA wallet
PRIVATE_KEY_FILE = PRIVATE_KEY_PATH_SCHEMA.format(EthereumCrypto.identifier)
create_private_key(EthereumCrypto.identifier, PRIVATE_KEY_FILE)


def build_aea(first_task: str, objective: str):
    """Build the AEA with the babyagi skill.

    Args:
        first_task (str): the first task to be completed by the agent
        objective (str): the objective of the agent

    Returns:
        AEA: the AEA with the babyagi skill
    """
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
    # Create our AEA
    my_aea = builder.build()

    print("\033[89m\033[1m" + "\n====== AEA babyAGI ONLINE ======" + "\033[0m\033[0m")

    # Set the AEA's agent context
    skill.skill_context.set_agent_context(my_aea.context)
    # update the shared state of the AEA with the memory object we created above
    skill.skill_context.shared_state.update(memory)
    return my_aea


def run(first_task: str, objective: str):
    """Run babyAGI.

    Args:
        first_task (str): the first task to be completed by the agent
        objective (str): the objective of the agent
    """

    # Build AEA-GPT
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


if __name__ == "__main__":
    _, first_task, objective = sys.argv
    try:
        run(first_task, objective)
    except KeyboardInterrupt:
        print("\033[89m\033[1m" + "\n======== EXIT ========" + "\033[0m\033[0m")
        pass
