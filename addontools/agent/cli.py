import os
import argparse
import logging
import subprocess

logger = logging.getLogger("addon-tools.agent")

# Agent tools


def kill_running_agent(agentName: str):
    try:
        subprocess.run(["taskkill", "/f", "/im", agentName], check=True)
    except subprocess.CalledProcessError:
        pass


def agent_handler(args):
    devDir = "F:/WoWDev/Agent"
    agentName = "Agent.exe"
    agentPath = f"C:/ProgramData/Battle.net/Agent/Beta/{agentName}"
    keyFile = f"{devDir}/keys/keyfile.txt"

    kill_running_agent(agentName)

    agentArgs = [
        "--show",
        "--allowcommands",
        "--extendedblizzarderrorui",
        "--loglevel=5",
        "--tracelevel=5",
    ]

    env = os.environ.copy()
    env.update({"SSLKEYLOGFILE": keyFile})

    try:
        with open(f"{devDir}/startup.log", "w") as f:
            f.truncate(0)
            f.write("-- AGENT START --\n")
        agent = subprocess.Popen(
            [agentPath] + agentArgs,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            env=env,
            shell=True,
        )

        for line in agent.stdout:
            logger.info(line)
            with open(f"{devDir}/startup.log", "a") as f:
                f.write(line)

        return_code = agent.wait()
        if return_code != 0:
            logger.error(f"Process returned non-zero exit code: {return_code}")
        else:
            logger.info("Agent constructor process exited gracefully.")

    except subprocess.CalledProcessError:
        logger.error("Failed to start new Agent process.")


def register_agent_parser(subparsers: argparse._SubParsersAction):
    parser = subparsers.add_parser(
        "agent",
        help="Helper tools for agenting specific WoW versions. All arguments provided with -- are forwarded to the WoW executable.",
    )

    parser.set_defaults(func=agent_handler)
