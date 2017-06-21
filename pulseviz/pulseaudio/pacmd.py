import subprocess
import re


def list_sources():
    result = []

    process = subprocess.Popen(['pacmd', 'list-sources'],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, _ = process.communicate(timeout=10.0)
    if process.returncode != 0:
        raise Exception('pacmd exited with return code {0}'.format(process.returncode))

    for line in stdout.splitlines(keepends=False):
        line = line.decode('ascii')
        match = re.match('^[\t]name: <(.*)>$', line)
        if match is not None:
            result.append(match.group(1))

    return result
