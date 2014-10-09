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

def check_pass_extension(filename):
    with open(filename, "r") as fp:
        json_mod.load(fp, enable_extensions = True)
    with open(filename, "r") as fp:
        with open(filename, "r") as fp:
            with assert_raises(ValueError):
                json_mod.load(fp, enable_extensions = False)

def check_fail_extension(filename):
    with open(filename, "r") as fp:
        with assert_raises(ValueError):
            json_mod.load(fp, enable_extensions = False)
    with open(filename, "r") as fp:
        with assert_raises(ValueError):
            json_mod.load(fp, enable_extensions = True)

def run_in_directory(path):
    for filename in sorted(os.listdir(path)):
        full_path = os.path.join(path, filename)
        if not filename.endswith(".json"):
            continue
        elif "pass_ext" in filename:
            yield check_pass_extension, full_path
        elif "fail_ext" in filename:
            yield check_fail_extension, full_path
        elif "pass" in filename:
            yield check_pass, full_path
            return
        elif "fail" in filename:
            yield check_fail, full_path
        else:
            continue

def test():
    path = os.path.dirname(__file__)
    yield from run_in_directory(os.path.join(path, "test_cases"))
    yield from run_in_directory(os.path.join(path, "json_org_test_cases"))
