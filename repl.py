import cmd
import shlex
from docopt import docopt
from time import time
import os
from glob import glob
from tokenise import Tokeniser
from markov import Markov
import fileinput
from functools import wraps
import itertools


def decorator_with_arguments(wrapper):
    return lambda *args, **kwargs: lambda func: wrapper(func, *args, **kwargs)


@decorator_with_arguments
def arg_wrapper(f, cmd, argstr="", types={}):
    @wraps(f)
    def wrapper(self, line):
        if not argstr:
            return f(self, line)

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
        self.markov = None
        self.generator = None

    # Generate output
    def _gen(self, args,
             startf=lambda t: True, endf=lambda t: True,
             kill=0, prefix=[]):
        """Generate a stream of output.
        """

        if not self.markov:
            print("No markov chain loaded!")
            return False

        if args["--seed"] is None:
            args["--seed"] = int(time())
            print("Using seed: {}".format(args["--seed"]))

        self.markov.reset(args["--seed"], args["--prob"], tuple(prefix))

        itertools.dropwhile(lambda t: not startf(t), self.markov)
        next(itertools.islice(self.markov,
                              args["--offset"],
                              args["--offset"]), None)

        def gen(n):
            out = []
            while n > 0:
                tok = next(self.markov)
                out.append(tok)
                if endf(tok):
                    n -= 1
            return(' '.join(out if not kill else out[:-kill]))

        self.generator = gen
        print(self.generator(args["<len>"]))

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

        self._gen(args)

    @arg_wrapper("paragraphs",
                 "<len> [--seed=<seed>] [--prob=<prob>] [--offset=<offset>]",
                 {"<len>": (int,),
                  "--seed": (int, None),
                  "--prob": (float, 0),
                  "--offset": (int, 0)})
    def do_paragraphs(self, args):
        """Generate paragraphs of output. See 'help generators'."""

        if self.markov and not self.markov.paragraph:
            print("Current markov chain has no paragraphs!")
            return False

        self._gen(args, endf=lambda t: t == '\n\n', kill=1, prefix=['\n\n'])

    @arg_wrapper("sentences",
                 "<len> [--seed=<seed>] [--prob=<prob>] [--offset=<offset>]",
                 {"<len>": (int,),
                  "--seed": (int, None),
                  "--prob": (float, 0),
                  "--offset": (int, 0)})
    def do_sentences(self, args):
        """Generate sentences of output. See 'help generators'."""

        sentence_token = lambda t: t[-1] in ".!?"
        self._gen(args, startf=sentence_token, endf=sentence_token)

    @arg_wrapper("continue",
                 "[<len>]",
                 {"<len>": (int, 1)})
    def do_continue(self, args):
        """Continue generating output.

continue [<len>]"""

        if self.generator is not None:
            print(self.generator(args["<len>"]))
        else:
            print("No generator to resume!")

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

        training_data = Tokeniser(stream=charinput(paths),
                                  punctuation=args["--punctuation"],
                                  paragraphs=args["--paragraphs"])

        self.markov = Markov(args["<n>"])
        self.markov.train(training_data)
        self.generator = None

    @arg_wrapper("load", "<file>")
    def do_load(self, args):
        """Load a generator from disk.

load <file>

Discard the current generator, and load the trained generator in the given
file."""

        self.generator = None
        self.markov = Markov()
        self.markov.load(args["<file>"])

    @arg_wrapper("dump", "<file>")
    def do_dump(self, args):
        """Save a generator to disk.

dump <file>

Save the trained generator to the given file."""

        self.markov.dump(args["<file>"])
