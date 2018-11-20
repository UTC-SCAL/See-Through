"""A file which is filled with all types of useful functions."""

import time
import urllib.request
import urllib.error


def timestamp_is_good(stream_data):
    """Find a timestamp from stream data."""
    token = "Current Time is: "
    time_start = str(stream_data).find(token) + len(token)
    time_end = time_start + 13

    try:  # Done due to decimal truncation
        timestamp = float(str(stream_data)[time_start:time_end])
    except ValueError:
        timestamp = float(str(stream_data)[time_start:time_start + 10])
    if time.time() - timestamp > 1:
        return False
    return True


def extract_timestamp(stream_data):
    """Find the timestamp from stream data and return it."""
    start_token = "Current Time is: "
    time_start = str(stream_data).find(start_token) + len(start_token)
    time_end = time_start + 13
    try:  # Done due to decimal truncation
        timestamp = float(str(stream_data)[time_start:time_end])
    except ValueError:
        timestamp = float(str(stream_data)[time_start:time_start + 10])
    return timestamp


def extract_frame_number(stream_data):
    """Find which frame was sent and return it."""
    num_start = str(stream_data).find("Current Frame is: ") + len("Current Frame is: ")
    num_end = str(stream_data).find("END FRAME NUM")
    return int(str(stream_data)[num_start:num_end])


def open_stream_safely(ip_address, **keyword_parameters):
    """Open the URL safely with timeouts handled by retrying."""
    try:
        stream = urllib.request.urlopen(ip_address)
        return stream
    except urllib.error.URLError:
        print("Connection timed out.. retrying in 5 seconds")
        time.sleep(5)
        if 'counter' in keyword_parameters:
            counter = int(keyword_parameters['counter'])
            if counter < 5:
                return open_stream_safely(ip_address, counter=counter + 1)
            else:
                print("Done trying. Not connecting.")
                return None
        return open_stream_safely(ip_address)
