"""Markov Chain.

Pass input to stdin.

Usage:
  markov <len> [-n <n>] [-p <p>] [-c] [-s <s>]
  markov -h | --help

Options:
  <len>      The length (in tokens) of the output to generate
  -n <n>     The number of symbols to look at in generation [default: 1]
  -p <p>     The probability to pick a random token [default: 0.05]
  -c         Split input per character, rather than per word
  -s <s>     Random seed [default: system time]
  -h --help  Show this screen
"""

from docopt import docopt
import sys
from time import time
from itertools import islice
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

    training_data = sys.stdin.read()

    if not arguments["-c"]:
        training_data = training_data.split()
    
    m = Markov(n=n, p=p, seed=s)
    m.train(training_data)

    print("Seed:", s)

    out = islice(m, int(arguments["<len>"]))
    if arguments["-c"]:
        out = "".join(out)
    else:
        out = " ".join(out)
    
    print(out)
