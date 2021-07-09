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

        self._last_printed_line_length = 0

    def __str__(self):
        """
        Renders progress bar as a string.
        :return: str
        """
        # Render prefix
        prefix = ''
        if self._prefix_expression and len(self._prefix_kwargs):
            prefix = self._prefix_expression.format(**self._prefix_kwargs)
        elif self._prefix_expression:
            prefix = self._prefix_expression

        # Render postfix
        postfix = ''
        if self._postfix_expression and len(self._postfix_kwargs):
            postfix = self._postfix_expression.format(**self._postfix_kwargs)
        elif self._postfix_expression:
            postfix = self._postfix_expression

        # Render bar
        bar = ''
        current_progress_length = self.progress_char_length
        nested_progress_positions = []
        # Re-calculate actual progress in screen characters
        for level, max_progress in self.progress_maxes.items():

            if level not in self.progress:
                value = 0
            else:
                value = self.progress[level]

            nested_progress_positions.append((value / max_progress) * current_progress_length)
            current_progress_length = int(current_progress_length / max_progress)

        # Round and floor progress to fit into the character limit
        for i in range(len(nested_progress_positions) - 1):
            nested_progress_positions[i] = int(nested_progress_positions[i])
        nested_progress_positions[-1] = round(nested_progress_positions[-1])

        # Actual bar render
        total_progress_chars = sum(nested_progress_positions)
        bar = self.progress_char * total_progress_chars + \
              self.empty_char * (self.progress_char_length - total_progress_chars)

        return prefix + bar + postfix  # concatenate the bar

    def print(self, *progress):
        """

        :param progress: indicates progress if specified, equal to calling set_progress without level
            (with single progress value or set of values for multiple levels) before print.
            Does not change current progress if not specified. Default: None
        :return:
        """
        self.set_progress(*progress)

        bar = self.__str__()
        print('\r' + ' ' * self._last_printed_line_length + '\r' + bar, sep = '', end = '', flush = True)
        self._last_printed_line_length = len(bar)

    # TODO: Add methods for progress bar total length

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

    def set_prefix_expression(self, expression, clear_args = True):
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
        if clear_args:
            self._prefix_kwargs = {}
        self._prefix_expression = expression

    def set_postfix_expression(self, expression, clear_args = True):
        if expression and type(expression) is not str:
            raise TypeError('expression should be either string or None or False')
        if clear_args:
            self._prefix_kwargs = {}
        self._postfix_expression = expression

    def set_prefix(self, expression):
        """
        Sets prefix string. Note: if you want to use expression formating with dynamic parameters, use
        set_prefix_expression and set_prefix_kwargs instead.
        :param expression:
        :return:
        """
        self.set_prefix_expression(self, expression, clear_args = True)

    def set_postfix(self, expression):
        self.set_postfix_expression(self, expression, clear_args = True)

    def set_prefix_kwargs(self, **kwargs):
        """

        :param kwargs:
        :return:
        """
        self._prefix_kwargs = kwargs

    def set_postfix_kwargs(self, **kwargs):
        """

        :param kwargs:
        :return:
        """
        self._postfix_kwargs = kwargs

    def set_prefix_arg(self, name, value):
        """

        :param name:
        :param value:
        :return:
        """
        self._prefix_kwargs[name] = value

    def set_postfix_arg(self, name, value):
        """

        :param name:
        :param value:
        :return:
        """
        self._postfix_kwargs[name] = value

    def pop_prefix_arg(self, name):
        """

        :param name:
        :return:
        """
        self._prefix_kwargs.pop(name, None)

    def pop_postfix_arg(self, name):
        """

        :param name:
        :return:
        """
        self._postfix_kwargs.pop(name, None)


# Progress bar test
if __name__ == '__main__':

    print('Simple progress bar test:')
    bar = ProgressBar()

    bar.set_prefix_expression('[')
    bar.set_postfix_expression('] {outer} - {inner}')

    bar.progress_char_length = 60
    bar.set_max(outer_level = 20, inner_level = 50)

    for i in range(20):

        bar.set_progress(i, level = 'outer_level')
        bar.set_postfix_arg('outer', i + 1)

        for j in range(10):

            bar.set_progress(j * 10, level = 'inner_level', percent = True)
            bar.set_postfix_arg('inner', j + 1)
            bar.print()
