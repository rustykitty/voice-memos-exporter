import sqlite3
import sys
import os
import os.path

from collections import namedtuple, Counter
import time
import shutil

import util

# macOS storage locations as of macOS 15 Sequoia
DEFAULT_DATA_DIR = os.path.expanduser("~/Library/Group Containers/group.com.apple.VoiceMemos.shared/Recordings/")
OUTPUT_DIRECTORY = "out"

QUERY = """
SELECT ZCLOUDRECORDING.ZENCRYPTEDTITLE, ZDATE, ZPATH, ZFOLDER.ZENCRYPTEDNAME
FROM ZCLOUDRECORDING 
LEFT JOIN ZFOLDER ON ZCLOUDRECORDING.ZFOLDER = ZFOLDER.Z_PK 
ORDER BY ZDATE ASC;
"""

def work(data_dir: str, db_filename: str = None):

    db_filename = db_filename or os.path.join(data_dir, "CloudRecordings.db")

    conn = sqlite3.connect(db_filename)

    cursor = conn.cursor()

    Row = namedtuple("Row", "name date filename folder")

    cursor.execute(QUERY)
    result = cursor.fetchall()
    
    result = [
        Row(*row) for row in result
    ]

    util.mkdir_exist_ok(OUTPUT_DIRECTORY)
    util.mkdir_exist_ok(os.path.join(OUTPUT_DIRECTORY, "folders"))

    # for name collisions
    name_counter = Counter()

    table = []

    for row in result:
        name, date, filename, folder = row

        if folder:
            folder = util.escape(folder)
            util.mkdir_exist_ok(os.path.join(OUTPUT_DIRECTORY, "folders", folder))

        output_basename = util.escape(name)
        if output_basename in name_counter:
            output_basename += f" ({name_counter[output_basename]})"

        output_filename = os.path.join(OUTPUT_DIRECTORY, output_basename) + ".m4a"

        timestamp = util.convert_timestamp(date)

        # todo: split across multiple lines
        table.append("\t".join(util.non_nullify((name, folder, util.iso8601(timestamp)))))

        # actually write the file now
        filename = os.path.join(DEFAULT_DATA_DIR, filename)

        shutil.copy(filename, output_filename)
        # (atime, mtime)
        os.utime(output_filename, times = (time.time(), timestamp))

        if folder:
            os.symlink(output_filename, os.path.join(OUTPUT_DIRECTORY, "folders", folder, output_basename))

        name_counter[output_basename] += 1

    table_txt = "\n".join(table)
    with open(os.path.join(OUTPUT_DIRECTORY, "data.tsv"), "w") as fp:
        fp.write(table_txt)

def main():
    dirname = DEFAULT_DATA_DIR
    filename = None

    if len(sys.argv) > 1:
        dirname = sys.argv[1]
    if len(sys.argv) > 2:
        filename = sys.argv[2]

    work(dirname, filename)

if __name__ == "__main__":
    sys.exit(main())