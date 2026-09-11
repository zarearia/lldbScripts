import lldb

def breakAfterRegex(debugger, command, result, internal_dict):
    print("yay. basic script setup with input: {}".format(command))

def __break_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f BreakAfterRegex.breakAfterRegex bar')
