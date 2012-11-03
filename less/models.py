from less.settings import LESS_DEVMODE


if LESS_DEVMODE:
    # Run the devmode daemon if it's enabled.
    # We start it here because this file is auto imported by Django when
    # devserver is started.
    from less.devmode import start_daemon
    start_daemon()
