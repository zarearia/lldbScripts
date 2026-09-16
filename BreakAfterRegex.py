import lldb

def breakAfterRegex(debugger, command, result, internal_dict):
    target = debugger.GetSelectedTarget()
    breakpoint = target.BreakpointCreateByRegex(command)

    if not breakpoint.IsValid() or breakpoint.num_locations == 0:
        result.AppendWarning("breakpoint is not valid or has not found any hits.")
    else:
        result.AppendMessage("{}".format(breakpoint))
        
    breakpoint.SetScriptCallbackFunction("BreakAfterRegex.breakpointHandler")

def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f BreakAfterRegex.breakAfterRegex bar')

def breakpointHandler(frame, bp_loc, dict):
    '''function called when the regular expression breakpoint gets triggered'''

    thread = frame.GetThread()
    process = thread.GetProcess()
    debugger = process.GetTarget().GetDebugger()

    function_name = frame.GetFunctionName()

    debugger.SetAsync(False)

    thread.StepOut()

    output = evaluateReturnedObject(debugger, thread, function_name)

    if output is not None:
        print(output)
     
    # print("stopped in: {}".format(function_name))
    return True

def evaluateReturnedObject(debugger, thread, function_name):
    
    '''
    Grabs the reference from the return register and returns a string from the evaluated value.
    TODO ObjC only.
    '''

    res = lldb.SBCommandReturnObject()

    interpreter = debugger.GetCommandInterpreter()
    target = debugger.GetSelectedTarget()
    frame = thread.GetSelectedFrame()
    parent_function_name = frame.GetFunctionName()

    expression = 'expression -l objc -O -- $arg1'

    interpreter.HandleCommand(expression, res)

    if res.HasResult():
        output = '{}\nbreakpoint: {}\nobject: {}\nstopped: {}'.format('*' * 80, function_name, res.GetOutput().replace('\n', ''), parent_function_name)
        return output
    else:
        return None

