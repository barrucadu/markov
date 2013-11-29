#import readline
import cmd
import shlex
from docopt import docopt
from time import time
from itertools import islice
import os
from glob import glob
from tokenise import Tokeniser
from markov import Markov
import fileinput


class Repl(cmd.Cmd):
    """REPL for Markov interaction. This is way overkill, yay!
    """

    def __init__(self):
        """Initialise a new REPL.
        :param markov: The Markov chain object.
        """

        super().__init__()
        self.markov = None
        self.generator = None

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

tokens <len> [--seed=<seed>] [--prob=<prob>]

<len> is the length of the sequence; <seed> is the optional random seed. If no
seed is given, the current system time is used; and <prob> is the probability of
random token choice. The default value for <prob> is 0.
"""

        args = self._args("tokens", "<len> [--seed=<seed>] [--prob=<prob>]", line)
        if not args:
            return False

        if not self.markov:
            print("No markov chain loaded!")
            return False

        try:
            seed = int(args["<seed>"])
        except:
            seed = int(time())
            print("Using seed: {}".format(seed))

        try:
            prob = float(args["<prob>"])
        except:
            prob = 0

        self.generator = self.markov
        self.generator.reset(seed, prob)
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

    # Loading and saving data
    def do_train(self, line):
        """Train a generator on a corpus.

train <n> ([--characters] | [--punctuation] [--paragraphs]) <path> ...

Discard the current generator, and train a new generator on the given paths.
Wildcards are allowed.

<n> is the length of prefix (producing <n+1>-grams).

Training can be either done per character, or per word. The 'characters' option
enables the former. The 'punctuation' option treats punctuation marks as
separate tokens, and the 'paragraphs' option treats paragraph breaks as a token.
"""

        args = self._args("train", "<n> ([--characters] | [--punctuation] [--paragraphs]) <path> ...", line)
        if not args:
            return False

        paths = [path
                 for ps in args["<path>"]
                 for path in glob(os.path.expanduser(ps))]

        def charinput(paths):
            with fileinput.input(paths) as fi:
                for line in fi:
                    for char in line:
                        yield char

        training_data = Tokeniser(stream=charinput(paths),
                                  characters=args["--characters"],
                                  punctuation=args["--punctuation"],
                                  paragraphs=args["--paragraphs"])

        try:
            n = int(args["<n>"])
        except:
            n = 3

        self.markov = Markov(n)
        self.markov.train(training_data)
        self.generator = None

    def do_load(self, line):
        """Load a generator from disk.

load <file>

Discard the current generator, and load the trained generator in the given
file."""

        args = self._args("load", "<file>", line)
        if not args:
            return False

        self.generator = None
        self.markov = Markov()
        self.markov.load(args["<file>"])

    def do_dump(self, line):
        """Save a generator to disk.

dump <file>

Save the trained generator to the given file."""

        args = self._args("dump", "<file>", line)
        if not args:
            return False

        self.markov.dump(args["<file>"])
