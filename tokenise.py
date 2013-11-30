import sys


class Tokeniser:
    """Flexible tokeniser for the Markov chain.
    """

    def __init__(self, stream=None, noparagraphs=False):
        self.stream = sys.stdin if stream is None else stream
        self.noparagraphs = noparagraphs

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
            try:
                next_char = next(self.stream)
            except:
                next_char = ''
                self.halt = True
                if not self.buffer:
                    break

            # Determine if we have a new token
            out = None
            if self.buffer:
                cout = False

                if self.buffer == '\n' and next_char == '\n':
                    # Paragraph break
                    if not self.noparagraphs:
                        out = self.buffer + next_char
                        next_char = ''

                elif not self.buffer.isspace() and next_char.isspace():
                    # A word
                    out = self.buffer

                # If the next_char is a token, save it
                if cout:
                    self.tok = next_char
                    next_char = ''

            # If a token has been found, reset the buffer
            if out:
                self.buffer = ''

            # If the buffer is only spaces, clear it when a word is added
            if self.buffer.isspace() and not next_char.isspace():
                self.buffer = next_char
            else:
                self.buffer += next_char

            # Return the found token
            if out:
                return out

        # If we're here, we got nothing but EOF.
        raise StopIteration
