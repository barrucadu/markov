"""Markov Chain.

Usage:
  markov dump [-n <n>] [-c]
  markov <len> [-n <n>] [-p <p>] [-c] [-s <s>] [-t] [--load=<file>]
  markov -h | --help

Options:
  <len>          The length (in tokens) of the output to generate
  -n <n>         The number of symbols to look at in generation [default: 1]
  -p <p>         The probability to pick a random token [default: 0.05]
  -c             Split input per character, rather than per word
  -t             Consider punctuation marks (when splitting by word) separate
                 tokens.
  -s <s>         Random seed [default: system time]
  --load=<file>  Load parsed data from this file, process stdin if not given
  dump           Process text on stdin and dump data file to stdout
  -h --help      Show this screen
"""

from docopt import docopt
import sys
from time import time
from itertools import islice
from tokenise import Tokeniser
from markov import Markov

if __name__ == "__main__":
    arguments = docopt(__doc__)

    n = int(arguments["-n"])
    p = float(arguments["-p"])

    try:
        s = int(arguments["-s"])
    except:
        s = int(time())

    if p > 1 or p < 0:
        print("p must be in the range 0 to 1 (inclusive)")
        sys.exit(1)

    if n < 0:
        print("n must be greater than 0")
        sys.exit(1)

    m = Markov(n=n, p=p, seed=s)

    if arguments["--load"]:
        m.load(arguments["--load"])
    else:
        training_data = Tokeniser(characters=arguments['-c'],
                                  punctuation=arguments['-t'])

        m.train(training_data)

    if arguments["dump"]:
        sys.stdout.buffer.write(m.dump())
    else:
        print("Seed:", s)

        out = islice(m, int(arguments["<len>"]))
        if arguments["-c"]:
            print("".join(out))
        else:
            print(" ".join(out))
