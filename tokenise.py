import sys


class Tokeniser:
    """Flexible tokeniser for the Markov chain.
    """

    def __init__(self, stream=None, characters=False, punctuation=False):
        self.stream = sys.stdin if stream is None else stream
        self.characters = characters
        self.punctuation = punctuation

    def __iter__(self):
        self.buffer = ''
        self.tok = ''
        self.halt = False
        return self

    def __next__(self):
        while not self.halt:
            # Return a pending token, if we have one
            if self.tok:
                out = self.tok
                self.tok = ''
                return out

            # Read the next character. If EOF, return what we have in the
            # buffer as the final token. Set a flag so we know to terminate
            # after this point.
            next_char = self.stream.read(1)
            if next_char == '':
                self.halt = True
                if not self.buffer:
                    break

            # Determine if we have a new token
            if self.buffer:
                out = None
                cout = False

                if self.characters:
                    # Split by character
                    out = self.buffer

                elif self.punctuation and not next_char.isalnum() and next_char.isprintable():
                    # Punctuation mark
                    out = self.buffer
                    cout = True

                elif next_char.isspace():
                    # A word
                    out = self.buffer

                # If the next_char is a token, save i
                if cout:
                    self.tok = next_char
                    next_char = ''

                # If a token has been found, return it and reset the buffer
                if out:
                    self.buffer = ''
                    return out

            self.buffer += next_char

        # If we're here, we got nothing but EOF.
        raise StopIteration
