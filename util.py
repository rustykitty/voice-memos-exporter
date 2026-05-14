import datetime

from os import mkdir
from contextlib import suppress

def convert_timestamp(timestamp):
    return timestamp + 978307200

def escape(s: str):
    # I'm not gonna escape anything else because you shouldn't be running
    # this program on anything other than macOS.
    # You shouldn't be putting tabs in your Voice Memo names, but if you do, it
    # messes with the TSV that this program outputs.
    return s.replace("/", "-").replace("\t", " ")
    
def mkdir_exist_ok(*args, **kwargs):
    with suppress(FileExistsError):
        mkdir(*args, **kwargs)

def non_nullify(it):
    # let's just hope no one names their files empty strings lol
    return (x if x is not None else "" for x in it)

def iso8601(ts):
    return datetime.datetime.fromtimestamp(ts).isoformat() + "Z"