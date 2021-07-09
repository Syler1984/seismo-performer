# Class for progress bar.
# Works like this:
#  Initialize it.
#  Then set progress change or value.
#  Call render method.
# Add ability for multi stage progress tracking, e.g. trace counts and progress within the trace.
# TODO: Add call examples for every function

class ProgressBar:
    def __init__(self):
    def __str__(self):
        """
        Renders progress bar as a string.
        :return: str
        """

    def print(self, *progress):
        """

        :param progress: indicates progress if specified, equal to calling set_progress without level
            (with single progress value or set of values for multiple levels) before print.
            Does not change current progress if not specified. Default: None
        :return:
        """
        # 1. Use *progress argument
        # 2. Erase previous bar
        # 3. Print the bar
    # TODO: Add methods for progress bar total length
    # TODO: Also add methods for string convertion

    def set_max(self, *max_progress, **max_progress_dictionary):
        """
        Sets max progress values for progress bar rendering. Values can be int or float.
        :param max_progress: one or more arguments for max progress values
        :param max_progress_dictionary: use if you want named progress levels
        :return: list of keywords for current progress levels
        """

    # TODO: Add methods for removing particular levels

    def set_progress(self, *progress, level = None,
                     fraction = False, percent = False):
        """
        Sets progress for a single level or for or existing levels as an absolute value, if progress consists of
        multiple values.
        :param progress:
        :param level:
        :param fraction:
        :param percent:
        """

    def set_progress_kwargs(self, fraction = False, percent = False, **progress):
        """
        Sets progress by dictionary of level keywords with progress values.
        :param progress:
        :param fraction:
        :param percent:
        :return:
        """

    def set_prefix_expression(self, expression):
        """
        Setter for the prefix expression.
        This expression will be used when printing the progress bar. Prefix keyword arguments will be used
        if specified with the expression.format(prefix_keyword_args) like call.
        :param expression: expression string in Pythons format specification mini-language (or just plain string
            if no formatting is needed).
        :return:
        """

    def set_prefix(self, expression):
        """
        Sets prefix string. Note: if you want to use expression formating with dynamic parameters, use
        set_prefix_expression and set_prefix_kwargs instead.
        :param args:
        :param kwargs:
        :return:
        """

    # TODO: Also add ability to set only one keyword argument
    def set_prefix_kwargs(self, **kwargs):
        pass

    def set_postfix_kwargs(self, **kwargs):
        pass
