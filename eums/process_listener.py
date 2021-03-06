import sys

import raven
from raven import Client, os

SENTRY_DSN = os.getenv('SENTRY_DSN', 'https://000000:000000@app.getsentry.com/10000')
GIT_SHA = raven.fetch_git_sha(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)))
client = Client(dsn=SENTRY_DSN, release=GIT_SHA)


def write_stdout(s):
    # only eventlistener protocol messages may be sent to stdout
    sys.stdout.write(s)
    sys.stdout.flush()


def write_stderr(s):
    sys.stderr.write(s)
    sys.stderr.flush()


def main():
    while 1:
        # transition from ACKNOWLEDGED to READY
        write_stdout('READY\n')

        # read header line and print it to stderr
        line = sys.stdin.readline()
        write_stderr(line)

        # read event payload and print it to stderr
        headers = dict([ x.split(':') for x in line.split() ])
        data = sys.stdin.read(int(headers['len']))
        write_stderr(data)
        client.captureMessage(data)

        # transition from READY to ACKNOWLEDGED
        write_stdout('RESULT 2\nOK')


if __name__ == '__main__':
    main()
