import argparse
import os
import re
import subprocess
import xml.dom.minidom as mxml
import time


import entity_finder
import builder
from unity_tester import UnityTester


def cmd_build(entities, pymk_root, args):
    print("======[Start to build applications]=========")
    for app in entities.apps:
        builder.AppBuilder(app, pymk_root)
    print("======[Finished building applications]======")

def cmd_test(entity_map, pymk_root, args):
    print("======[Start testing of code]===============")
    tester = UnityTester(entity_map, pymk_root, args)
    tester.prepare()
    tester.run()
    print("======[Finished testing of code]============")

def cmd_clean(entity_map, pymk_root, args):
    print("clean")


def cmd_stats(entity_map, pymk_root, args):
    print("stats")


def cmd_info(entity_map, pymk_root, args):
    print("info")


def main():
    parser = argparse.ArgumentParser(description="Tool to build and test c code.", epilog="Commands iterate through sub-directories recursively, looking for sources, dependencies and unit tests.")
    subparsers = parser.add_subparsers()

    parser_build = subparsers.add_parser("build", help="Iterate directories, compile and link modules and programs.")
    parser_build.set_defaults(func=cmd_build)

    parser_test  = subparsers.add_parser("test",  help="Iterate directories, generate mocks, build and run tests.")
    parser_test.set_defaults(func=cmd_test)

    parser_clean = subparsers.add_parser("clean", help="Remove build and test files.")
    parser_clean.set_defaults(func=cmd_clean)

    parser_stats = subparsers.add_parser("stats", help="Displays useful info about modules.")
    parser_stats.set_defaults(func=cmd_stats)

    parser_info  = subparsers.add_parser("info",  help="Display info on how to use this build system.")
    parser_info.set_defaults(func=cmd_info)

    arguments = parser.parse_args()

    pymk_root = os.path.dirname(os.path.abspath(__file__))
    pymk_root = pymk_root.replace("/cygdrive", "")
    print(pymk_root)

    entities = entity_finder.EntityFinder(pymk_root, exclude_dir_names=["mocks"])
    entities.run()

    arguments.func(entities, pymk_root, arguments)


if __name__ == "__main__":
    main()