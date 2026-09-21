import lldb
import optparse
import shlex

def breakAfterRegex(debugger, command, result, internal_dict):
    
    command = command.replace('\\', '\\\\')
    command_args = shlex.split(command, posix=False)
    parser = generateOptionParser()

    try:
        (options, args) = parser.parse_args(command_args)
    except:
        result.SetError(parser.usage)
        return

    target = debugger.GetSelectedTarget()
    clean_command = shlex.split(args[0])[0]


    print(clean_command)

    if options.non_regex:
        breakpoint = target.BreakpointCreateByName(clean_command, options.module)
    else:
        breakpoint = target.BreakpointCreateByRegex(clean_command, options.module)


    if not breakpoint.IsValid() or breakpoint.num_locations == 0:
        result.AppendWarning("breakpoint is not valid or has not found any hits.")
    else:
        result.AppendMessage("{}".format(breakpoint))
        
    breakpoint.SetScriptCallbackFunction("BreakAfterRegex.breakpointHandler")

def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f BreakAfterRegex.breakAfterRegex bar')

def breakpointHandler(frame, bp_loc, dict):
    '''function called when the regular expression breakpoint gets triggered'''

    #breakpoint()
    thread = frame.GetThread()
    process = thread.GetProcess()
    debugger = process.GetTarget().GetDebugger()

    function_name = frame.GetFunctionName()

    debugger.SetAsync(False)

    thread.StepOut()

    output = evaluateReturnedObject(debugger, thread, function_name)
    #breakpoint()

    if output is not None:
        print(output)
    
     
    print("stopped in: {}".format(function_name))
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



def generateOptionParser():
    '''Generates the Parsers to parse the command input
    '''
    usage = "usage: %prog [options] breakpoint_query \n Use 'bar -h' for option desc"

    parser = optparse.OptionParser(usage=usage, prog=usage)

    parser.add_option("-n", "--non_regex", action="store_true", default=False, dest="non_regex", help="Use a non-regex breakpoint instead")

    parser.add_option("-m", "--module",
                      action="store",
                      default=None,
                      dest="module",
                      help="Filter a breakpoint by only searching within a specific Module")
    return parser
