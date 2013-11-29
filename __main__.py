"""Markov Chain.

Usage:
  markov [-n <n>] [-p <p>] [-c] [-t] [-P] [--load=<file>]
  markov -h | --help

Options:
  -n <n>         The number of symbols to look at in generation [default: 1]
  -p <p>         The probability to pick a random token [default: 0.05]
  -c             Split input per character, rather than per word
  -t             Consider punctuation marks (when splitting by word) separate
                 tokens.
  -P             Consider paragraph breaks to be a token, also start the generated text
                 on a new paragraph.
  --load=<file>  Load parsed data from this file, process stdin if not given
  -h --help      Show this screen
"""

from docopt import docopt
import sys
from tokenise import Tokeniser
from markov import Markov
from repl import run_repl

if __name__ == "__main__":
    arguments = docopt(__doc__)

    n = int(arguments["-n"])
    p = float(arguments["-p"])

    if p > 1 or p < 0:
        print("p must be in the range 0 to 1 (inclusive)")
        sys.exit(1)

    if n < 0:
        print("n must be greater than 0")
        sys.exit(1)

    m = Markov(n=n, p=p, paragraph=arguments['-P'])

    if arguments["--load"]:
        m.load(arguments["--load"])
    else:
        training_data = Tokeniser(characters=arguments['-c'],
                                  punctuation=arguments['-t'],
                                  paragraphs=arguments['-P'])

        m.train(training_data)

    run_repl(m)
