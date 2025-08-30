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


class CmdOpen(Command):
    key="open"
    aliases=["carefully open","hastily open"]

    def func(self):
        self.caller.msg(self.cmdstring)  # outputs 'carefully open' when user types 'carefully open box'
    

class CmdActor(Command):
    key="actor"

    def func(self):

        self.caller.msg_contents("$You([Yoda]) $conj(headpat)")


class CmdTeleportCreate(Command):
    key="tpcreate"

    def func(self):
        pass

from evennia.utils import delay
from evennia.scripts.taskhandler import TASK_HANDLER

class CmdTestDelay(Command):
    key = "testdelay"

    def func(self):
        caller = self.caller

        def bleh(arg: str):
            caller.msg(arg)
            
        def other_bleh(arg: str):
            caller.msg(f"other_bleh: {arg}")

        t = TASK_HANDLER.add(10,other_bleh, "test")
        TASK_HANDLER.remove(t.task_id)

        for x in range(3):
            delay(10, bleh, str(x))

from evennia import MONITOR_HANDLER



class CmdTestMonitor(Command):
     key="testmonitor"
     def func(self):
        caller = self.caller
        
        # Check if hp attribute exists
        hp_attr = caller.attributes.get("hp", return_obj=True)
        caller.msg(f"HP attribute object: {hp_attr}")
        caller.msg(f"HP value: {caller.db.hp}")
        
        # Ensure the attribute exists before monitoring
        if not hp_attr:
            caller.db.hp = caller.db.hp or 10  # Set if not set
            
        # Debug: Check what the add method is working with
        caller.msg(f"About to add monitor for: obj={caller}, fieldname=hp")
        
        # Let's check all objects in monitors after the add
        result = MONITOR_HANDLER.add(caller, "hp", _monitor_callback_global,
                    idstring="1", persistent=False, category=None)
        
        caller.msg(f"Add result: {result}")
        
        # Check what's actually in the monitors dict
        caller.msg(f"All monitored objects: {list(MONITOR_HANDLER.monitors.keys())}")
        caller.msg(f"Monitors for caller: {MONITOR_HANDLER.monitors.get(caller, 'Not found')}")
        
        # Check if hp_attr is being monitored instead
        if hp_attr:
            caller.msg(f"Monitors for hp_attr: {MONITOR_HANDLER.monitors.get(hp_attr, 'Not found')}")
        
        # Try different ways to modify the hp value
        caller.msg("Modifying hp with caller.db.hp += 1")
        caller.db.hp += 1
        
        caller.msg("Modifying hp with caller.attributes.add")
        current_hp = caller.db.hp
        caller.attributes.add("hp", current_hp + 1)
        
        caller.msg("Modifying hp attribute object directly")
        hp_attr.value = hp_attr.value + 1
        hp_attr.save()
        
        # Manually trigger the monitor to test if the callback works
        caller.msg("Manually triggering monitor callback")
        
        # Debug the at_update process
        caller.msg(f"hp_attr in monitors: {hp_attr in MONITOR_HANDLER.monitors}")
        if hp_attr in MONITOR_HANDLER.monitors:
            caller.msg(f"db_value in hp_attr monitors: {'db_value' in MONITOR_HANDLER.monitors[hp_attr]}")
            if 'db_value' in MONITOR_HANDLER.monitors[hp_attr]:
                monitors_for_field = MONITOR_HANDLER.monitors[hp_attr]['db_value']
                caller.msg(f"Monitors for db_value: {monitors_for_field}")
                for idstring, (callback, persistent, kwargs) in monitors_for_field.items():
                    caller.msg(f"About to call callback: {callback}")
                    try:
                        caller.msg(f"hp_attr attributes: {dir(hp_attr)}")
                        result = callback(obj=hp_attr, fieldname="db_value", **kwargs)
                        caller.msg(f"Callback result: {result}")
                    except Exception as e:
                        caller.msg(f"Callback error: {e}")
        
        MONITOR_HANDLER.at_update(hp_attr, "db_value")
        
        # Get monitors for the hp attribute object, not the caller
        monitor_list_hp = MONITOR_HANDLER.all(obj=hp_attr)
        caller.msg(f"Monitor list for hp_attr: {monitor_list_hp}")
        
        # Also check all monitors
        all_monitors = MONITOR_HANDLER.all()
        caller.msg(f"All monitors: {all_monitors}")

def _monitor_callback_global(obj, fieldname, **kwargs):
    """Global callback function for monitor testing"""
    print(f"MONITOR CALLBACK FIRED: obj={obj}, fieldname={fieldname}")
    # obj is the attribute object, so we need to get the character that owns it
    try:
        # Try to find the character through the reverse relationships
        if hasattr(obj, 'objectdb_set') and obj.objectdb_set.exists():
            character = obj.objectdb_set.first()
            character.msg(f"🔥 MONITOR FIRED: {fieldname} changed to {obj.value}!")
        elif hasattr(obj, 'accountdb_set') and obj.accountdb_set.exists():
            character = obj.accountdb_set.first()
            character.msg(f"🔥 MONITOR FIRED: {fieldname} changed to {obj.value}!")
        else:
            print(f"Could not find owning object for attribute {obj}")
    except Exception as e:
        print(f"Error in monitor callback: {e}")
            