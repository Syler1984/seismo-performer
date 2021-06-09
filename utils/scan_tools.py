import obspy.core as oc
from scipy.signal import find_peaks
import numpy as np
import matplotlib.pyplot as plt
import os


def pre_process_stream(stream, no_filter = False, no_detrend = False):
    """
    Does preprocessing on the stream (changes it's frequency), does linear detrend and
    highpass filtering with frequency of 2 Hz.

    Arguments:
    stream      -- obspy.core.stream object to pre process
    frequency   -- required frequency
    """
    if not no_detrend:
        stream.detrend(type="linear")
    if not no_filter:
        stream.filter(type="highpass", freq = 2)

    frequency = 100.
    required_dt = 1. / frequency
    dt = stream[0].stats.delta

    if dt != required_dt:
        stream.interpolate(frequency)


def trim_streams(streams):
    """
    Trims streams to the same overall time span.
    :return: list of trimmed streams
    """
    max_start_time = None
    min_end_time = None

    for stream in streams:

        current_start = min([x.stats.starttime for x in stream])
        current_end = max([x.stats.endtime for x in stream])

        if not max_start_time:
            max_start_time = current_start
        if not min_end_time:
            min_end_time = current_end

        if current_start > max_start_time:
            max_start_time = current_start
        if current_end < min_end_time:
            min_end_time = current_end

    cut_streams = []
    for st in streams:
        cut_streams.append(st.slice(max_start_time, min_end_time))

    return cut_streams


def get_traces(streams, i):
    """
    Returns traces with specified index
    :return: list of traces
    """
    traces = [st[i] for st in streams]  # get traces

    # Trim traces to the same length
    start_time = max([trace.stats.starttime for trace in traces])
    end_time = min([trace.stats.endtime for trace in traces])

    for j in range(len(traces)):
        traces[j] = traces[j].slice(start_time, end_time)

    return traces


def progress_bar(progress, characters_count = 20,
                 erase_line = True,
                 empty_bar = '.', filled_bar = '=', filled_edge = '>',
                 prefix = '', postfix = '',
                 add_space_around = True):
    """
    Prints progress bar.
    :param progress: percentage (0..1) of progress, or int number of characters filled in progress bar.
    :param characters_count: length of the bar in characters.
    :param erase_line: preform return carriage.
    :param empty_bar: empty bar character.
    :param filled_bar: progress character.
    :param filled_edge: progress character on the borderline between progressed and empty,
                        set to None to disable.
    :param prefix: progress bar prefix.
    :param postfix: progress bar postfix.
    :param add_space_around: add space after prefix and before postfix.
    :return:
    """

    space_characters = ' \t\n'
    if add_space_around:
        if len(prefix) > 0 and prefix[-1] not in space_characters:
            prefix += ' '

        if len(postfix) > 0 and postfix[0] not in space_characters:
            postfix = ' ' + postfix

    if erase_line:
        print('\r', end = '')

    progress_num = int(characters_count * progress)
    if filled_edge is None:
        print(prefix + filled_bar * progress_num + empty_bar * (characters_count - progress_num) + postfix, end = '')
    else:
        bar_str = prefix + filled_bar * progress_num
        bar_str += filled_edge * min(characters_count - progress_num, 1)
        bar_str += empty_bar * (characters_count - progress_num - 1)
        bar_str += postfix

        print(bar_str, end = '')


def cut_traces(*_traces):
    """
    Cut traces to same timeframe (same start time and end time). Returns list of new traces.

    Positional arguments:
    Any number of traces (depends on the amount of channels). Unpack * if passing a list of traces.
    e.g. scan_traces(*trs)
    """
    _start_time = max([x.stats.starttime for x in _traces])
    _end_time = max([x.stats.endtime for x in _traces])

    return_traces = [x.slice(_start_time, _end_time) for x in _traces]

    return return_traces


def sliding_window(data, n_features, n_shift):
    """
    Return NumPy array of sliding windows. Which is basically a view into a copy of original data array.

    Arguments:
    data       -- numpy array to make a sliding windows on
    n_features -- length in samples of the individual window
    n_shift    -- shift between windows starting points
    """
    # Get sliding windows shape
    win_count = np.floor(data.shape[0]/n_shift - n_features/n_shift + 1).astype(int)
    shape = (win_count, n_features)

    windows = np.zeros(shape)

    for _i in range(win_count):

        _start_pos = _i * n_shift
        _end_pos = _start_pos + n_features

        windows[_i][:] = data[_start_pos : _end_pos]

    return windows.copy()


def normalize_windows_global(windows):
    """
    Normalizes sliding windows array. IMPORTANT: windows should have separate memory, striped windows would break.
    :param windows:
    :return:
    """
    # Shape (windows_number, n_features, channels_number)
    n_win = windows.shape[0]
    ch_num = windows.shape[2]

    for _i in range(n_win):

        win_max = np.max(np.abs(windows[_i, :, :]))
        windows[_i, :, :] = windows[_i, :, :] / win_max


def normalize_windows_per_trace(windows):
    """
    Normalizes sliding windows array. IMPORTANT: windows should have separate memory, striped windows would break.
    :param windows:
    :return:
    """
    # Shape (windows_number, n_features, channels_number)
    n_win = windows.shape[0]
    ch_num = windows.shape[2]

    for _i in range(n_win):

        for _j in range(ch_num):

            win_max = np.max(np.abs(windows[_i, :, _j]))
            windows[_i, :, _j] = windows[_i, :, _j] / win_max


def plot_positives(scores, windows, threshold):

    idx = 0
    save_name = 'positive_' + str(idx) + '.jpg'
    while os.path.exists(save_name):
        idx += 1
        save_name = 'positive_' + str(idx) + '.jpg'

    for i in range(len(scores)):

        if scores[i][1] > threshold:

            fig, (ax1, ax2, ax3) = plt.subplots(3, sharex = True)

            ax1.set_ylabel('N', rotation = 0.)
            ax1.plot(windows[i, :, 0], 'r')

            ax2.set_ylabel('E', rotation = 0.)
            ax2.plot(windows[i, :, 1], 'g')

            ax3.set_ylabel('Z', rotation = 0.)
            ax3.plot(windows[i, :, 2], 'y')

            plt.savefig(save_name)
            plt.clf()

            """
            np_s_array = np.zeros((400, 3))

            np_s_array[:, 0] = windows[i, :, 0]
            np_s_array[:, 1] = windows[i, :, 1]
            np_s_array[:, 2] = windows[i, :, 2]

            np.save(params['plot_path'] + code + '_' + str(i) + '_p' + '.npy', np_s_array)
            """


def plot_oririnal_positives(scores, original_windows, threshold, original_scores = None):

    idx = 0
    save_name = 'original_positive_' + str(idx) + '.jpg'
    while os.path.exists(save_name):
        idx += 1
        save_name = 'original_positive_' + str(idx) + '.jpg'

    for i in range(len(scores)):

        if scores[i][1] > threshold:

            fig, (ax1, ax2, ax3) = plt.subplots(3, sharex = True)

            ax1.set_ylabel('N', rotation = 0.)
            ax1.plot(original_windows[i, :, 0], 'r')

            ax2.set_ylabel('E', rotation = 0.)
            ax2.plot(original_windows[i, :, 1], 'g')

            ax3.set_ylabel('Z', rotation = 0.)
            ax3.plot(original_windows[i, :, 2], 'y')

            plt.savefig(save_name)
            plt.clf()


def scan_traces(*_traces, model = None, args = None, n_features = 400, shift = 10, original_data = None):
    """
    Get predictions on the group of traces.

    Positional arguments:
    Any number of traces (depends on the amount of channels). Unpack * if passing a list of traces.
    e.g. scan_traces(*trs)

    Keyword arguments
    model            -- NN model
    n_features       -- number of input features in a single channel
    shift            -- amount of samples between windows
    global_normalize -- normalize globaly all traces if True or locally if False
    batch_size       -- model.fit batch size
    """
    # Check args
    import argparse
    if not args and type(args) != argparse.Namespace:
        raise AttributeError('args should have an argparse.Namespace type')

    batch_size = args.batch_size

    # Check input types
    for x in _traces:
        if type(x) != oc.trace.Trace:
            raise TypeError('traces should be a list or containing obspy.core.trace.Trace objects')
    # plot-positives-original
    # Cut all traces to a same timeframe
    _traces = cut_traces(*_traces)

    # Normalize
    # TODO: Change normalization to normalization per element
    # normalize_traces(*traces, global_normalize = global_normalize)

    # Get sliding window arrays
    l_windows = []
    for x in _traces:
        l_windows.append(sliding_window(x.data, n_features = n_features, n_shift = shift))

    if args.plot_positives_original:
        original_l_windows = []
        for x in original_data:
            original_l_windows.append(sliding_window(x.data, n_features = n_features, n_shift = shift))

    w_length = min([x.shape[0] for x in l_windows])

    # Prepare data
    windows = np.zeros((w_length, n_features, len(l_windows)))
    for _i in range(len(l_windows)):
        windows[:, :, _i] = l_windows[_i][:w_length]

    if args.plot_positives_original:
        original_windows = np.zeros((w_length, n_features, len(original_l_windows)))
        for _i in range(len(original_l_windows)):
            original_windows[:, :, _i] = original_l_windows[_i][:w_length]

    # Global max normalization:
    # TODO: Make an parameter for local normalization
    normalize_windows_global(windows)
    if args.plot_positives_original:
        normalize_windows_global(original_windows)

    # Per-channel normalization:
    # normalize_windows_per_trace(windows)

    # Predict
    _scores = model.predict(windows, verbose = False, batch_size = batch_size)
    # TODO: create another flag for this, e.g. --culculate-original-probs or something
    if args.plot_positives_original:
        original_scores = model.predict(original_windows, verbose = False, batch_size = batch_size)

    # Plot
    # if args and args.plot_positives:
    #     plot_threshold_scores(scores, windows, params['threshold'], file_name, params['plot_labels'])

    # Save scores
    # if args and args.save_positives:
    #     save_threshold_scores(scores, windows, params['threshold'],
    #                           params['positives_h5_path'], params['save_h5_labels'])

    # Positives plotting
    if args.plot_positives:
        plot_positives(_scores, windows, args.threshold)
    if args.plot_positives_original:
        plot_oririnal_positives(_scores, original_windows, args.threshold, original_scores)

    return _scores


def restore_scores(_scores, shape, shift):
    """
    Restores scores to original size using linear interpolation.

    Arguments:
    scores -- original 'compressed' scores
    shape  -- shape of the restored scores
    shift  -- sliding windows shift
    """
    new_scores = np.zeros(shape)
    for i in range(1, _scores.shape[0]):

        for j in range(_scores.shape[1]):

            start_i = (i - 1) * shift
            end_i = i * shift
            if end_i >= shape[0]:
                end_i = shape[0] - 1

            new_scores[start_i : end_i, j] = np.linspace(_scores[i - 1, j], _scores[i, j], shift + 1)[:end_i - start_i]

    return new_scores


def get_positives(_scores, peak_idx, other_idxs, peak_dist = 10000, avg_window_half_size = 100, threshold = 0.8):
    """
    Returns positive prediction list in format: [[sample, pseudo-probability], ...]
    """
    _positives = []

    x = _scores[:, peak_idx]

    peaks = find_peaks(x, distance = peak_dist, height=[threshold, 1.])

    for _i in range(len(peaks[0])):

        start_id = peaks[0][_i] - avg_window_half_size
        if start_id < 0:
            start_id = 0

        end_id = start_id + avg_window_half_size*2
        if end_id > len(x):
            end_id = len(x) - 1
            start_id = end_id - avg_window_half_size*2

        # Get mean values
        peak_mean = x[start_id : end_id].mean()

        means = []
        for idx in other_idxs:
            means.append(_scores[:, idx][start_id : end_id].mean())

        is_max = True
        for m in means:

            if m > peak_mean:
                is_max = False

        if is_max:
            _positives.append([peaks[0][_i], peaks[1]['peak_heights'][_i]])

    return _positives


def truncate(f, n):
    """
    Floors float to n-digits after comma.
    """
    import math
    return math.floor(f * 10 ** n) / 10 ** n


def print_results(_detected_peaks, filename, precision = 2, upper_case = True):
    """
    Prints out peaks in the file.
    """
    with open(filename, 'a') as f:

        for record in _detected_peaks:

            line = ''
            # Print wave type
            tp = record['type'].upper() if upper_case else record['type']
            line += f'{tp} '

            # Print pseudo-probability
            line += f'{truncate(record["pseudo-probability"], precision):1.{precision}f} '

            # Print time
            dt_str = record["datetime"].strftime("%d.%m.%Y %H:%M:%S.%f").rstrip('0')
            line += f'{dt_str}\n'

            # Write
            f.write(line)


def parse_archive_csv(path):
    """
    Parses archives names file. Returns list of filename lists: [[archive1, archive2, archive3], ...]
    :param path:
    :return:
    """
    with open(path) as f:
        lines = f.readlines()

    _archives = []
    for line in lines:
        _archives.append([x for x in line.split()])

    return _archives
