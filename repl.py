#import readline
import cmd
import shlex
from docopt import docopt
from time import time
from itertools import islice
import os


class Repl(cmd.Cmd):
    """REPL for Markov interaction. This is way overkill, yay!
    """

    def __init__(self, markov):
        """Initialise a new REPL.
        :param markov: The Markov chain object.
        """

        super().__init__()
        self.generator = None
        self.markov = markov

    def _args(self, cmd, argstr, line):
        """Parse a line of input into arguments.
        :param cmd: Name of the command.
        :param argstr: Argument format / help string.
        :param line: Line of text.
        """

        args = docopt("usage: {} {}\n{} [dummy ...]".format(cmd, argstr, cmd),
                      argv=shlex.split(line),
                      help=False)

        if args["dummy"] or not line:
            print(cmd + " " + argstr)
            return None
        else:
            del args["dummy"]
            return args

    # Generate output
    def do_tokens(self, line):
        """Generate tokens of output.

tokens <len> [seed <seed>]

<len> is the length of the sequence, and <seed> is the optional random seed. If
no seed is given, the current system time is used.
"""

        args = self._args("tokens", "<len> [seed <seed>]", line)
        if not args:
            return False

        try:
            seed = int(args["<seed>"])
        except:
            seed = int(time())
            print("Using seed: {}".format(seed))

        self.generator = self.markov
        self.generator.reset(seed)
        print(" ".join(islice(self.generator, int(args["<len>"]))))

    def do_continue(self, line):
        """Continue generating tokens.

continue <len>"""

        args = self._args("continue", "<len>", line)
        if not args:
            return False

        if self.generator:
            print(" ".join(islice(self.generator, int(args["<len>"]))))
        else:
            print("No generator to resume!")

    # Dump data to disk
    def do_dump(self, line):
        """Save a generator to disk.

dump <file>

Save the trained generator to the given file."""

        args = self._args("dump", "<file>", line)
        if not args:
            return False

        try:
            print(os.path.expanduser(args["<file>"]))
            with open(os.path.expanduser(args["<file>"]), "wb") as f:
                f.write(self.markov.dump())
        except:
            print("Could not dump to file.")


def run_repl(markov):
    repl = Repl(markov)
    repl.cmdloop()
