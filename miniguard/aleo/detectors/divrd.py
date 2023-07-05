import json

from llvmlite.binding.module import ModuleRef
from llvmlite.binding.value import ValueRef

def report(fn):
    def inner(*args, **kwargs):
        res = fn(*args, **kwargs)
        # wrap into a report
        obj = [{
            "detector": "DivRD",
            "result": res,
            "details": None
        }]
        return obj
    return inner

@report
def divrd_detector(arg_fun):
    # iterate on blocks
    for dblock in arg_fun.blocks:
        if isinstance(dblock, ValueRef) and dblock.is_block:
            # iterate on instructions
            for dinst in dblock.instructions:
                if isinstance(dinst, ValueRef) and dinst.is_instruction:
                    if dinst.opcode == "sdiv":
                        return True
                else:
                    raise Exception("dinst is not a ValueRef / instruction")
        else:
            raise Exception("dblock is not a ValueRef / block")
    return False