"""
Commands

Commands describe the input the account can do to the game.

"""

from evennia.commands.command import Command as BaseCommand
from evennia.commands.default.general import CmdLook

# from evennia import default_cmds


class Command(BaseCommand):
    """
    Base command (you may see this if a child command had no help text defined)

    Note that the class's `__doc__` string is used by Evennia to create the
    automatic help entry for the command, so make sure to document consistently
    here. Without setting one, the parent's docstring will show (like now).

    """

    # Each Command class implements the following methods, called in this order
    # (only func() is actually required):
    #
    #     - at_pre_cmd(): If this returns anything truthy, execution is aborted.
    #     - parse(): Should perform any extra parsing needed on self.args
    #         and store the result on self.
    #     - func(): Performs the actual work.
    #     - at_post_cmd(): Extra actions, often things done after
    #         every command, like prompts.
    #
    pass


import debugpy


class CmdDebug(Command):
    key = "debug"
    locks = "cmd:perm(create) or perm(Builder)"
    arg_regex = r"\s|$"
    help_category = "Admin"

    def func(self):
        caller = self.caller
        print("Waiting for debugger attach")
        debugpy.listen(("localhost", 5678))
        debugpy.wait_for_client()
        caller.msg("Debugger attached")
        print("Debugger attached")

class CmdBlah(Command):
    key = "blah"
    locks = "perm(Builder)"
    arg_regex = r"\s|$"
    help_category = "Admin"

    def func(self):
        self.helper1()

    def helper1(self):
        x = []
        self.helper2()

    def helper2(self):
        self.helper3()

    def helper3(self):
        raise Exception("Testing py error traceback")


import sys


def trace_calls(frame, event, arg):
    if event == "call":
        code = frame.f_code
        function_name = code.co_name
        filename = code.co_filename
        lineno = frame.f_lineno

        print(f"Called {function_name} in {filename}:{lineno}")
    return trace_calls


class TracedCmdLook(CmdLook):
    def func(self):
        print("===== Starting Trace for CmdLook =====")
        sys.settrace(trace_calls)

        try:
            super().func()  # Execute original logic
        finally:
            sys.settrace(None)  # Stop tracing after execution
            print("===== Trace Ended =====")


class CmdMXP(Command):
    key = "mxptest"

    def func(self):
        self.caller.msg("|lcsay my test |lt|rMytest|n|le")
        self.caller.msg("|lc say what\;say tree|lh |rhi|n;|bidk|n\;last |lt|bblah|n|le")