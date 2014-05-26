from .. import test

def inject_suites():
    """
    The function that injects coffee scripts in this directory as test suites.
    """
    import json
    import os
    import subprocess
    from .. import printf, suite, test
    from ._script_util import run_coffee

    # Check that nodejs and jasmine-node are installed
    args = {}
    try:
        with open(os.devnull, 'w') as devnull:
            args['run_jasmine_suites'] = subprocess.call(
                ['nodejs', '--eval', 'require("jasmine-node");'],
                stdout = devnull,
                stderr = devnull) == 0
            if not args['run_jasmine_suites']:
                args['error_message'] = 'jasmine-node is not installed'
    except OSError:
        args['error_message'] = 'nodejs is not installed'
        args['run_jasmine_suites'] = False

    # These are the file extensions of files in the current directory that we
    # inject
    extensions = ('.coffee', '.js')

    class JasmineSuite(object):
        """
        A callable that, when decorated with suite, injects a js or coffee suite
        as a test suite.
        """
        def __init__(self, path, run_jasmine_suites = True,
                error_message = None):
            self.__name__ = 'jasmine.' + os.path.basename(path).split('.', 1)[0]
            self.path = path
            self.run_jasmine_suites = run_jasmine_suites
            self.error_message = error_message
            self.failures = []
            self.specs = {}

        def setup(self):
            if not self.run_jasmine_suites:
                printf('Cannot run suite: %s' % (self.error_message))
                return False
            return True

        def __call__(self):
            # Launch the jasmine runner with nodejs
            jasmine_runner = os.path.join(
                    os.path.dirname(__file__),
                    os.pardir,
                    'jasmine-runner.js')
            process = subprocess.Popen([
                'nodejs',
                jasmine_runner,
                self.path],
                stderr = subprocess.STDOUT,
                stdout = subprocess.PIPE)

            # Locate lines printed by the jasmine runner reporter
            for line in process.stdout:
                try:
                    # Extract the type of result
                    result = json.loads(line.strip())
                    when = result['when']
                    del result['when']

                    # Call the handler
                    getattr(self, '_handle_%s' % when)(**result)

                except (ValueError, KeyError, AttributeError):
                    # This is not a spec result
                    pass

            return self.failures

        def _spec_id_to_str(self, spec_id):
            """
            Converts a spec ID to a test name.

            @param spec_id
                The spec ID to convert.
            @return a string usable as a test name
            """
            return 'Test %d' % (spec_id + 1)

        def _describe_failures(self, failures):
            """
            Returns a string representation of a failure list.

            @param failures
                The failures to describe.
            @return a printable version of the failures
            """
            # Ignore all but the first failure
            return failures[0]['message']

        def _handle_spec_start(self, spec_id, description):
            """
            Handles a spec_start output line fron the jasmine runner.

            @param spec_id
                The ID of the current spec.
            @param description
                The full description of the spec.
            """
            printf('%s - %s',
                self._spec_id_to_str(spec_id),
                description)
            self.specs[spec_id] = description

        def _handle_spec_failed(self, spec_id, failures):
            """
            Handles a spec_failed output line from the jamine runner.

            @param spec_id
                The ID of the spec that failed.
            @param failues
                The list of failures for the spec. This must be a non-empty list
                of dicts with the key 'stacktrace' present. Currently only the
                first element is used.
            """
            printf('%s did not pass: %s',
                self._spec_id_to_str(spec_id),
                self._describe_failures(failures))
            self.failures.append(
                (self._spec_id_to_str(spec_id), self.specs[spec_id]))

    directory = os.path.dirname(os.path.abspath(__file__))
    for filename in (
            f for f in os.listdir(directory)
            if f[0] != '_'
                and any(f.endswith(extension) for extension in extensions)):
        path = os.path.join(directory, filename)
        suite(JasmineSuite(path, **args))


inject_suites()
