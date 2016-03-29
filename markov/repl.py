import cmd
import shlex
import docopt
import os
import glob
import fileinput
import functools
from markov import markovstate


def decorator_with_arguments(wrapper):
    return lambda *args, **kwargs: lambda func: wrapper(func, *args, **kwargs)


@decorator_with_arguments
def arg_wrapper(f, cmd, argstr="", types={}):
    @functools.wraps(f)
    def wrapper(self, line):
        try:
            args = docopt.docopt("usage: {} {}".format(cmd, argstr),
                                 argv=shlex.split(line),
                                 help=False)

            for k, v in types.items():
                try:
                    if k in args:
                        args[k] = v[1] if args[k] == [] else v[0](args[k])
                except:
                    args[k] = v[1]

            return f(self, args)
        except docopt.DocoptExit:
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

generator <len> [--seed=<seed>] [--prob=<prob>] [--offset=<offset>] [--cln=<cln>] [--] [<prefix>...]

<len> is the length of the sequence; <seed> is the optional random
seed. If no seed is given, the current system time is used; and <prob>
is the probability of random token choice. The default value for <prob>
is 0. If an offset is give, drop that many tokens from the start of the
output. <cln> is the <n> value to use after a clause ends, the default
is <n>. The optional prefix is used to see the generator with tokens. A
prefix of length longer than the generator's n will be truncated.  """)

    @arg_wrapper("tokens",
                 "<len> [--seed=<seed>] [--prob=<prob>] [--offset=<offset>] [--cln=<cln>] [--] [<prefix>...]",
                 {"<len>": (int,),
                  "--seed": (int, None),
                  "--prob": (float, 0),
                  "--offset": (int, 0),
                  "--cln": (int, None),
                  "<prefix>": (tuple, ())})
    def do_tokens(self, args):
        """Generate tokens of output. See 'help generators'."""

        try:
            print(self.markov.generate(args["<len>"], args["--seed"],
                                       args["--prob"], args["--offset"],
                                       args["--cln"],
                                       prefix=args["<prefix>"]))
        except markovstate.MarkovStateError as e:
            print(e.value)

    @arg_wrapper("paragraphs",
                 "<len> [--seed=<seed>] [--prob=<prob>] [--offset=<offset>] [--cln=<cln>] [--] [<prefix>...]",
                 {"<len>": (int,),
                  "--seed": (int, None),
                  "--prob": (float, 0),
                  "--offset": (int, 0),
                  "--cln": (int, None),
                  "<prefix>": (tuple, ('\n\n',))})
    def do_paragraphs(self, args):
        """Generate paragraphs of output. See 'help generators'."""

        try:
            print(self.markov.generate(args["<len>"], args["--seed"],
                                       args["--prob"], args["--offset"],
                                       endchunkf=lambda t: t == '\n\n',
                                       kill=1, prefix=args["<prefix>"]))
        except markovstate.MarkovStateError as e:
            print(e.value)

    @arg_wrapper("sentences",
                 "<len> [--seed=<seed>] [--prob=<prob>] [--offset=<offset>] [--cln=<cln>] [--] [<prefix>...]",
                 {"<len>": (int,),
                  "--seed": (int, None),
                  "--prob": (float, 0),
                  "--offset": (int, 0),
                  "--cln": (int, None),
                  "<prefix>": (tuple, ())})
    def do_sentences(self, args):
        """Generate sentences of output. See 'help generators'."""

        sentence_token = lambda t: t[-1] in ".!?"
        try:
            print(self.markov.generate(args["<len>"], args["--seed"],
                                       args["--prob"], args["--offset"],
                                       startf=sentence_token,
                                       endchunkf=sentence_token,
                                       prefix=args["<prefix>"]))
        except markovstate.MarkovStateError as e:
            print(e.value)

    @arg_wrapper("continue", "[<len>]", {"<len>": (int, 1)})
    def do_continue(self, args):
        """Continue generating output.

continue [<len>]"""

        try:
            print(self.markov.more(args["<len>"]))
        except markovstate.MarkovStateError as e:
            print(e.value)

    # Loading and saving data
    @arg_wrapper("train", "<n> [--noparagraphs] <path> ...", {"<n>": (int,)})
    def do_train(self, args):
        """Train a generator on a corpus.

train <n> [--noparagraphs] <path> ...

Discard the current generator, and train a new generator on the given paths.
Wildcards are allowed.

<n> is the length of prefix (producing <n+1>-grams). If the 'noparagraphs'
option is given, paragraph breaks are treated as spaces and discarded, rather
than a separate token.
"""

        paths = [path
                 for ps in args["<path>"]
                 for path in glob.glob(os.path.expanduser(ps))]

        def charinput(paths):
            with fileinput.input(paths) as fi:
                for line in fi:
                    for char in line:
                        yield char

        self.markov.train(args["<n>"],
                          charinput(paths),
                          noparagraphs=args["--noparagraphs"])

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
