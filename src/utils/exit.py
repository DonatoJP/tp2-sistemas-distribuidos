import sys

def exit(closables=[], exit_code=0):
    for closable in closables:
        closable.close()
    sys.exit(exit_code)