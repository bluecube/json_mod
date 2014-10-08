import json_mod
from nose.tools import *
import os

def check_pass(filename):
    with open(filename, "r") as fp:
        enabled_extensions = json_mod.load(fp, enable_extensions = True)
    with open(filename, "r") as fp:
        disabled_extensions = json_mod.load(fp, enable_extensions = False)
    assert_equal(enabled_extensions, disabled_extensions)

def check_fail(filename):
    with open(filename, "r") as fp:
        with assert_raises(ValueError):
            json_mod.load(fp, enable_extensions = False)

def test():
    path = os.path.join(os.path.dirname(__file__), "json_org_test_cases")
    for filename in sorted(os.listdir(path)):
        filename = os.path.join(path, filename)
        if not filename.endswith(".json"):
            continue
        elif "pass" in filename:
            yield check_pass, filename
            return
        elif "fail" in filename:
            yield check_fail, filename
        else:
            continue
