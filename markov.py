import random
import pickle
import os
import sys


class Markov:
    def __init__(self, n=3):
        self.n = n
        self.p = 0
        self.seed = None
        self.data = {}
        self.paragraph = False

    def train(self, training_data):
        prev = ()
        for token in training_data:
            token = sys.intern(token)
            if token == '\n\n':
                # This data set has paragraph breaks in.
                self.paragraph = True

            for pprev in [prev[i:] for i in range(len(prev) + 1)]:
                if not pprev in self.data:
                    self.data[pprev] = [0, {}]

                if not token in self.data[pprev][1]:
                    self.data[pprev][1][token] = 0

                self.data[pprev][1][token] += 1
                self.data[pprev][0] += 1

            prev += (token,)
            if len(prev) > self.n:
                prev = prev[1:]

    def load(self, filename):
        with open(os.path.expanduser(filename), "rb") as f:
            try:
                n, self.paragraph, self.data = pickle.load(f)

                if self.n > n:
                    print("warning: changing n value to", n)
                    self.n = n
                return True
            except:
                print("Loading data file failed!")
                return False

    def dump(self, filename):
        try:
            with open(os.path.expanduser(filename), "wb") as f:
                return pickle.dump((self.n, self.paragraph, self.data), f)
            return True
        except:
            print("Could not dump to file.")
            return False

    def reset(self, seed, prob, prev):
        self.seed = seed
        self.p = prob
        self.prev = prev
        random.seed(seed)

    def __iter__(self):
        return self

    def __next__(self):
        if self.prev == () or random.random() < self.p:
            next = self._choose(self.data[()])
        else:
            try:
                next = self._choose(self.data[self.prev])
            except:
                self.prev = ()
                next = self._choose(self.data[self.prev])

        self.prev += (next,)
        if len(self.prev) > self.n:
            self.prev = self.prev[1:]

        return next

    def _choose(self, freqdict):
        total, choices = freqdict
        idx = random.randrange(total)

        for token, freq in choices.items():
            if idx <= freq:
                return token

            idx -= freq
