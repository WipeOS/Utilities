from wipeos_bottle.bottle import route, run, response
from parsers.utility import Logger
import subprocess
from subprocess import Popen, PIPE
from datetime import datetime, timedelta
import shlex
import json
import requests

machine = {}
logger = Logger("command")

@route('/execute/<command:path>')
def execute_command(command):
    if not command:
        response.status = 400
        return "Please provide a 'command' query parameter."

    # Execute the command using subprocess.run
    logger.info("Executing command: {}".format(command))
    try:
        commands = command.split('|')
        pipes = []
        for cmd in commands:
            cmd = cmd.strip()
            cmds = shlex.split(cmd)
            if len(pipes) == 0:
                # First command, no input
                pipes.append(subprocess.Popen(cmds, stdout=subprocess.PIPE))
            else:
                pipes.append(subprocess.Popen(cmds, stdin=pipes[-1].stdout, stdout=subprocess.PIPE))
                pipes[-2].stdout.close()

        # Get the output from the last command
        output, errors = pipes[-1].communicate()

        response.status = 200
        return output
    
    except subprocess.CalledProcessError as e:
        logger.error("Error executing command: {}\nError Output: {}\n".format(command, errors))
        response.status = 400
        logger.info("Error executing command: {}\nError Output: {}\n".format(command, errors))
        return e
    
    except Exception as e:
        response.status = 400
        logger.info("An unexpected error occurred: {}\nError Output: {}\n".format(command, e))
        return e

if __name__ == '__main__':
    run(host='0.0.0.0', port=8087, debug=True, reload=True)
