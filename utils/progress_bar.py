# Class for progress bar.
# Works like this:
#  Initialize it.
#  Then set progress change or value.
#  Call render method.
# Add ability for multi stage progress tracking, e.g. trace counts and progress within the trace.
# TODO: Add call examples for every function

class ProgressBar:

    def __init__(self):

        self.progress_maxes = {}
        self.progress = {}

        self.progress_char = '#'
        self.empty_char = '-'
        self.progress_char_length = 30

        self._prefix_expression = None
        self._postfix_expression = None
        self._prefix_kwargs = {}
        self._postfix_kwargs = {}

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
        if not len(max_progress) and not len(max_progress_dictionary):
            return
        if len(max_progress) and len(max_progress_dictionary):
            raise AttributeError('max progress should be either all positional or all keyword arguments')

        self.progress_maxes = {}

        if len(max_progress):
            for i, max_val in enumerate(max_progress):
                self.progress_maxes[str(i)] = max_val
        else:
            self.progress_maxes = max_progress_dictionary

        return self.progress_maxes.keys()

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
        if not len(progress):
            return
        if not level and len(progress) > 1:
            raise AttributeError('multiple progress values with specified level are not compatible')
        if not level and len(progress) != len(self.progress_maxes):
            raise AttributeError(f'progress values count ({len(progress)}) should be equal'
                                 f' to the number of progress levels ({len(self.progress_maxes)})')
        if fraction and percent:
            raise AttributeError('both fraction and percent could not be True simultaneously')

        if not level:

            self.progress = {}
            for value, (level, max_progress) in zip(progress, self.progress_maxes.items()):
                if fraction:
                    value = min(value, 1.)
                    self.progress[level] = value * max_progress
                elif percent:
                    value = min(value, 100.)
                    self.progress[level] = (value * max_progress) / 100.
                else:
                    value = min(value, max_progress)
                    self.progress[level] = value

        else:

            if level not in self.progress_maxes:
                raise AttributeError(f'level {level} is not defined in progress maxes')
            if type(level) is not str:
                level = str(level)

            value = progress[0]
            max_progress = self.progress_maxes[level]

            if fraction:
                value = min(value, 1.)
                self.progress[level] = value * max_progress
            elif percent:
                value = min(value, 100.)
                self.progress[level] = (value * max_progress) / 100.
            else:
                value = min(value, max_progress)
                self.progress[level] = value


    def set_progress_kwargs(self, fraction = False, percent = False, **progress):
        """
        Sets progress by dictionary of level keywords with progress values.
        :param progress:
        :param fraction:
        :param percent:
        :return:
        """
        if not len(progress):
            return

        for level, value in progress.items():

            if level not in self.progress_maxes:
                raise AttributeError(f'level {level} is not defined in progress maxes')
            max_progress = self.progress_maxes[level]

            if fraction:
                value = min(value, 1.)
                self.progress[level] = value * max_progress
            elif percent:
                value = min(value, 100.)
                self.progress[level] = (value * max_progress) / 100.
            else:
                value = min(value, max_progress)
                self.progress[level] = value

    def set_prefix_expression(self, expression):
        """
        Setter for the prefix expression.
        This expression will be used when printing the progress bar. Prefix keyword arguments will be used
        if specified with the expression.format(prefix_keyword_args) like call.
        :param expression: expression string in Pythons format specification mini-language (or just plain string
            if no formatting is needed).
        :return:
        """
        if expression and type(expression) is not str:
            raise TypeError('expression should be either string or None or False')
        self._prefix_expression = expression

    def set_postfix_expression(self, expression):
        if expression and type(expression) is not str:
            raise TypeError('expression should be either string or None or False')
        self._postfix_expression = expression

    def set_prefix(self, expression):
        """
        Sets prefix string. Note: if you want to use expression formating with dynamic parameters, use
        set_prefix_expression and set_prefix_kwargs instead.
        :param args:
        :param kwargs:
        :return:
        """
        self._prefix_kwargs = {}
        self.set_prefix_expression(self, expression)

    def set_postfix(self, expression):
        self._postfix_kwargs = {}
        self.set_postfix_expression(self, expression)

    # TODO: Also add ability to set only one keyword argument
    def set_prefix_kwargs(self, **kwargs):
        pass

    def set_postfix_kwargs(self, **kwargs):
        pass
