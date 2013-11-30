import cmd
import shlex
from docopt import docopt
import os
from glob import glob
import markovstate
import fileinput
from functools import wraps


def decorator_with_arguments(wrapper):
    return lambda *args, **kwargs: lambda func: wrapper(func, *args, **kwargs)


@decorator_with_arguments
def arg_wrapper(f, cmd, argstr="", types={}):
    @wraps(f)
    def wrapper(self, line):
        try:
            args = docopt("usage: {} {}".format(cmd, argstr),
                          argv=shlex.split(line),
                          help=False)

            for k, v in types.items():
                try:
                    if k in args:
                        args[k] = v[0](args[k])
                except:
                    args[k] = v[1]

            return f(self, args)
        except:
            print(cmd + " " + argstr)
    return wrapper


class Repl(cmd.Cmd):
    """REPL for Markov interaction. This is way overkill, yay!
    """

    def __init__(self):
        """Initialise a new REPL.
        """

        super().__init__()
        self.markov = markovstate.MarkovState()

    def help_generators(self):
        print("""Generate a sequence of output:

generator <len> [--seed=<seed>] [--prob=<prob>] [--offset=<offset>]

<len> is the length of the sequence; <seed> is the optional random seed. If no
seed is given, the current system time is used; and <prob> is the probability
of random token choice. The default value for <prob> is 0. If an offset is
give, drop that many tokens from the start of the output.
""")

    @arg_wrapper("tokens",
                 "<len> [--seed=<seed>] [--prob=<prob>] [--offset=<offset>]",
                 {"<len>": (int,),
                  "--seed": (int, None),
                  "--prob": (float, 0),
                  "--offset": (int, 0)})
    def do_tokens(self, args):
        """Generate tokens of output. See 'help generators'."""

        try:
            print(self.markov.generate(args["<len>"], args["--seed"],
                                       args["--prob"], args["--offset"]))
        except markovstate.MarkovStateError as e:
            print(e.value)

    @arg_wrapper("paragraphs",
                 "<len> [--seed=<seed>] [--prob=<prob>] [--offset=<offset>]",
                 {"<len>": (int,),
                  "--seed": (int, None),
                  "--prob": (float, 0),
                  "--offset": (int, 0)})
    def do_paragraphs(self, args):
        """Generate paragraphs of output. See 'help generators'."""

        if not self.markov.paragraphs():
            print("Current markov chain has no paragraphs!")
            return

        try:
            print(self.markov.generate(args["<len>"], args["--seed"],
                                       args["--prob"], args["--offset"],
                                       endchunkf=lambda t: t == '\n\n',
                                       kill=1, prefix=('\n\n',)))
        except markovstate.MarkovStateError as e:
            print(e.value)

    @arg_wrapper("sentences",
                 "<len> [--seed=<seed>] [--prob=<prob>] [--offset=<offset>]",
                 {"<len>": (int,),
                  "--seed": (int, None),
                  "--prob": (float, 0),
                  "--offset": (int, 0)})
    def do_sentences(self, args):
        """Generate sentences of output. See 'help generators'."""

        sentence_token = lambda t: t[-1] in ".!?"
        try:
            print(self.markov.generate(args["<len>"], args["--seed"],
                                       args["--prob"], args["--offset"],
                                       startf=sentence_token,
                                       endchunkf=sentence_token))
        except markovstate.MarkovStateError as e:
            print(e.value)

    @arg_wrapper("continue",
                 "[<len>]",
                 {"<len>": (int, 1)})
    def do_continue(self, args):
        """Continue generating output.

continue [<len>]"""

        try:
            print(self.markov.more(args["<len>"]))
        except markovstate.MarkovStateError as e:
            print(e.value)

    # Loading and saving data
    @arg_wrapper("train",
                 "<n> [--punctuation] [--paragraphs] <path> ...",
                 {"<n>": (int,)})
    def do_train(self, args):
        """Train a generator on a corpus.

train <n> [--punctuation] [--paragraphs] <path> ...

Discard the current generator, and train a new generator on the given paths.
Wildcards are allowed.

<n> is the length of prefix (producing <n+1>-grams).

Training is done per token (word). The 'punctuation' option treats punctuation
marks as separate tokens, and the 'paragraphs' option treats paragraph breaks
as a token.
"""

        paths = [path
                 for ps in args["<path>"]
                 for path in glob(os.path.expanduser(ps))]

        def charinput(paths):
            with fileinput.input(paths) as fi:
                for line in fi:
                    for char in line:
                        yield char

        self.markov.train(args["<n>"],
                          charinput(paths),
                          punctuation=args["--punctuation"],
                          paragraphs=args["--paragraphs"])

    @arg_wrapper("load", "<file>")
    def do_load(self, args):
        """Load a generator from disk.

load <file>

Discard the current generator, and load the trained generator in the given
file."""

        self.markov.load(args["<file>"])

    @arg_wrapper("dump", "<file>")
    def do_dump(self, args):
        """Save a generator to disk.

dump <file>

Save the trained generator to the given file."""

        try:
            self.markov.dump(args["<file>"])
        except markovstate.MarkovStateError as e:
            print(e.value)
