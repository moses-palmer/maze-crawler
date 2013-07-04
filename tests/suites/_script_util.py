import os
import subprocess
import tempfile

def _run_script(code, arguments, suffix):
    """
    Runs interpreted code.

    @param code
        The code to execute. This is written to a temporary file.
    @param arguments
        The argument list to execute. A generated file name will be appeded to
        this list before executing.
    @param suffix
        The file extension to use for the temporary file.
    @return the output of the code
    @raise ValueError if the code could not be run
    """
    try:
        fd, name = tempfile.mkstemp(suffix = suffix)
        with os.fdopen(fd, 'w') as f:
            f.write(code)

        p = subprocess.Popen(
            arguments + [name],
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE)
        stdout, stderr = p.communicate()

        if p.returncode:
            raise ValueError(stderr)

        return stdout

    finally:
        try:
            os.unlink(name)
        except:
            pass


def run_js(code):
    """
    Runs JavaScript code.

    @param code
        The JavaScript to execute.
    @return the output of the code
    @raise ValueError if the code could not be run
    @see run_script
    """
    # nodejs must be installed on the system
    nodejs_command = [
        os.getenv('NODEJS_BIN', 'nodejs')]

    return _run_script(code, nodejs_command, '.js')


def run_coffee(code):
    """
    Runs CoffeeScript code.

    @param code
        The CoffeeScript to execute.
    @return the output of the code
    @raise ValueError if the code could not be run
    @see run_script
    """
    # coffe is located in coffee-script/bin in the project root; we are in
    # tests/suites
    coffee_command = [
        os.getenv('NODEJS_BIN', 'nodejs'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
            os.pardir, os.pardir, 'coffee-script', 'bin', 'coffee')]

    return _run_script(code, coffee_command, '.coffee')
