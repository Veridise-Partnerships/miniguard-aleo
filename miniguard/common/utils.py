from llvmlite.binding.module import ModuleRef
from llvmlite.binding.value import ValueRef

def regularize_name(arg_obj):
    if len(arg_obj.name) == 0:
        # could be customized constants like "i1 true" and "i1 false"
        return str(arg_obj)
    else:
        return arg_obj.name
    
def locate_function(arg_obj, arg_fun_name):
    """
    Locate the first function with given name.
    """
    if isinstance(arg_obj, ModuleRef):
        # iterate all functions
        for dfunction in arg_obj.functions:
            if isinstance(dfunction, ValueRef) and dfunction.is_function:
                if dfunction.name == arg_fun_name:
                    return dfunction
            else:
                raise Exception("dfunction is not a ValueRef / function")
    else:
        raise Exception("arg_obj is not a ModuleRef")
    return None

# FIXME: refactor aleo2llvm to remove this summary
def summary_conversion(arg_sum):
    """
    Convert summary from record form to dictionary form.
    """
    new_sum = {"module": arg_sum["module"], "functions": {}}
    for p in arg_sum["functions"]:
        new_sum["functions"][p["name"]] = {"arguments": {}, "returns": {}}
        for q in p["arguments"]:
            new_sum["functions"][p["name"]]["arguments"][q["name"]] = {
                "visibility": q["visibility"]
            }
        for q in p["returns"]:
            new_sum["functions"][p["name"]]["returns"][q["name"]] ={
                "visibility": q["visibility"]
            }
    return new_sum