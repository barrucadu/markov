README
======

Overview
-----------


The program presents a REPL, from which you can generate text in a
number of different ways, a list of commands can be produced by typing
`help`, and help for specific topics can be found by typing `help
topic`.

Dependencies
------------

 - python3
 - docopt

Getting Started
---------------

1. Download the KingJamesProgramming corpus from this repo:

    ````
    tar xvf KingJamesProgramming.tar.xz
    ````

2. Fire up the program

    ````
    python3 /path/to/repo
    ````

3. Generate text

    ````
    train 3 --noparagraphs /path/to/KingJamesProgramming/*
    tokens 350
    ````

Warning: Repetition
--------------------

To avoid infinite loops, the `paragraphs` and `sentences` generators may end 
abruptly. Because they generate blocks of text at a time, and a block would only 
end when a specific token (such as a paragraph break) occurs, the generators are
programmed to end the chunk immediately if they find themselves generating a
token from the same state repeatedly (with the threshold set at the number of
occurences of that state in the training corpus). This can cause issues with
small training sets or, if the training set has many rare words, with a high 
chance of choosing a random token. 
