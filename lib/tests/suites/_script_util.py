import os
import subprocess
import tempfile

def _run_script(code, *arguments):
    """
    Runs interpreted code.

    @param code
        The code to execute.
    @param arguments
        The argument list to execute.
    @return the output of the code
    @raise ValueError if the code could not be run
    """
    p = subprocess.Popen(
        arguments,
        stdin = subprocess.PIPE,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE)
    stdout, stderr = p.communicate(code)

    if p.returncode:
        raise ValueError(stderr)

    return stdout


def run_js(code):
    """
    Runs JavaScript code.

    @param code
        The JavaScript to execute.
    @return the output of the code
    @raise ValueError if the code could not be run
    @see run_script
    """
    return _run_script(code,
        os.getenv('NODEJS_BIN', 'nodejs'))


def run_coffee(code):
    """
    Runs CoffeeScript code.

    @param code
        The CoffeeScript to execute.
    @return the output of the code
    @raise ValueError if the code could not be run
    @see run_script
    """
    return _run_script(code,
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
            os.pardir, os.pardir, os.pardir, 'node_modules', 'coffee-script',
            'bin', 'coffee'),
        '--stdio')
