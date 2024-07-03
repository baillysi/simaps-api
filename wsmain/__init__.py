import os
import sys

if "ENV" in os.environ:
    # prod ou dev
    env = os.environ["ENV"]
    print(f'Working environment : {env}')
    if env not in ('dev', 'prod'):
        sys.exit('Unknown environment')

