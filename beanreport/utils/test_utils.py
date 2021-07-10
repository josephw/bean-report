"""Support utilities for testing scripts.
"""
__copyright__ = "Copyright (C) 2014-2016  Martin Blais"
__license__ = "GNU GPLv2"

import textwrap
import unittest
import io
import re
import tempfile
import logging
import sys
import contextlib
import functools
from os import path

def find_repository_root(filename=None):
    """Return the path to the repository root.

    Args:
      filename: A string, the name of a file within the repository.
    Returns:
      A string, the root directory.
    """
    if filename is None:
        filename = __file__

    # Support root directory under Bazel.
    match = re.match(r"(.*\.runfiles/beancount)/", filename)
    if match:
        return match.group(1)

    while not all(path.exists(path.join(filename, sigfile))
                  for sigfile in ('COPYING', 'README.md')):
        prev_filename = filename
        filename = path.dirname(filename)
        if prev_filename == filename:
            raise ValueError("Failed to find the root directory.")
    return filename


def run_with_args(function, args, runner_file=None):
    """Run the given function with sys.argv set to argv. The first argument is
    automatically inferred to be where the function object was defined. sys.argv
    is restored after the function is called.

    Args:
      function: A function object to call with no arguments.
      argv: A list of arguments, excluding the script name, to be temporarily
        set on sys.argv.
      runner_file: An optional name of the top-level file being run.
    Returns:
      The return value of the function run.
    """
    saved_argv = sys.argv
    saved_handlers = logging.root.handlers

    try:
        if runner_file is None:
            module = sys.modules[function.__module__]
            runner_file = module.__file__
        sys.argv = [runner_file] + args
        logging.root.handlers = []
        return function()
    finally:
        sys.argv = saved_argv
        logging.root.handlers = saved_handlers


# TODO(blais): Improve this with kwargs instead.
def capture(*attributes):
    """A context manager that captures what's printed to stdout.

    Args:
      *attributes: A tuple of strings, the name of the sys attributes to override
        with StringIO instances.
    Yields:
      A StringIO string accumulator.
    """
    if not attributes:
        attributes = 'stdout'
    elif len(attributes) == 1:
        attributes = attributes[0]
    return patch(sys, attributes, io.StringIO)


@contextlib.contextmanager
def patch(obj, attributes, replacement_type):
    """A context manager that temporarily patches an object's attributes.

    All attributes in 'attributes' are saved and replaced by new instances
    of type 'replacement_type'.

    Args:
      obj: The object to patch up.
      attributes: A string or a sequence of strings, the names of attributes to replace.
      replacement_type: A callable to build replacement objects.
    Yields:
      An instance of a list of sequences of 'replacement_type'.
    """
    single = isinstance(attributes, str)
    if single:
        attributes = [attributes]

    saved = []
    replacements = []
    for attribute in attributes:
        replacement = replacement_type()
        replacements.append(replacement)
        saved.append(getattr(obj, attribute))
        setattr(obj, attribute, replacement)

    yield replacements[0] if single else replacements

    for attribute, saved_attr in zip(attributes, saved):
        setattr(obj, attribute, saved_attr)


def docfile(function, **kwargs):
    """A decorator that write the function's docstring to a temporary file
    and calls the decorated function with the temporary filename.  This is
    useful for writing tests.

    Args:
      function: A function to decorate.
    Returns:
      The decorated function.
    """
    @functools.wraps(function)
    def new_function(self):
        allowed = ('buffering', 'encoding', 'newline', 'dir', 'prefix', 'suffix')
        if any([key not in allowed for key in kwargs]):
            raise ValueError("Invalid kwarg to docfile_extra")
        with tempfile.NamedTemporaryFile('w', **kwargs) as file:
            text = function.__doc__
            file.write(textwrap.dedent(text))
            file.flush()
            return function(self, file.name)
    new_function.__doc__ = None
    return new_function


def search_words(words, line):
    """Search for a sequence of words in a line.

    Args:
      words: A list of strings, the words to look for, or a space-separated string.
      line: A string, the line to search into.
    Returns:
      A MatchObject, or None.
    """
    if isinstance(words, str):
        words = words.split()
    return re.search('.*'.join(r'\b{}\b'.format(word) for word in words), line)


class TestCase(unittest.TestCase):

    def assertLines(self, text1, text2, message=None):
        """Compare the lines of text1 and text2, ignoring whitespace.

        Args:
          text1: A string, the expected text.
          text2: A string, the actual text.
          message: An optional string message in case the assertion fails.
        Raises:
          AssertionError: If the exception fails.
        """
        clean_text1 = textwrap.dedent(text1.strip())
        clean_text2 = textwrap.dedent(text2.strip())
        lines1 = [line.strip() for line in clean_text1.splitlines()]
        lines2 = [line.strip() for line in clean_text2.splitlines()]

        # Compress all space longer than 4 spaces to exactly 4.
        # This affords us to be even looser.
        lines1 = [re.sub('    [ \t]*', '    ', line) for line in lines1]
        lines2 = [re.sub('    [ \t]*', '    ', line) for line in lines2]
        self.assertEqual(lines1, lines2, message)

    @contextlib.contextmanager
    def assertOutput(self, expected_text):
        """Expect text printed to stdout.

        Args:
          expected_text: A string, the text that should have been printed to stdout.
        Raises:
          AssertionError: If the text differs.
        """
        with capture() as oss:
            yield oss
        self.assertLines(textwrap.dedent(expected_text), oss.getvalue())
