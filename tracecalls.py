import sys


def trace_calls(frame, event, arg):
    """
    Trace function calls and print their details.
    """
    if event == "call":
        code = frame.f_code
        function_name = code.co_name
        filename = code.co_filename
        lineno = frame.f_lineno

        print(f"Called {function_name} in {filename}:{lineno}")
    return trace_calls  # Keep tracing subsequent calls


def start_tracing():
    """
    Start tracing all function calls.
    """
    sys.settrace(trace_calls)


def stop_tracing():
    """
    Stop tracing all function calls.
    """
    sys.settrace(None)
