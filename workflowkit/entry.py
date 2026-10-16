import sys
from workflowkit.cli import main

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print('Controller stopped.')
    except Exception as error:
        print(f'Workflow stopped: {error}')
        if sys.stdin.isatty():
            input('Press Enter to close...')
        raise SystemExit(1)
