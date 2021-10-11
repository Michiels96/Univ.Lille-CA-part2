#!/usr/bin/python3

import subprocess
import json
import os
import sys


def process(cmd):
    """
    """
    process = subprocess.run(cmd, capture_output=True, shell=True)
    if process.returncode == 0:
        return True, process.stdout.decode("utf-8")
    else:
        print(process.stderr.decode("utf-8"))
        return False, ""



if __name__ == "__main__":

    if sys.argv[1] == "loggin":
        #ok = create_banque()
        print(
            "+ utilisateur connecté avec succès") if ok else print("- utilisateur non connecté")

    if sys.argv[1] == "CreateUser":
        #ok = create_banque()
        print(
            "+ utilisateur crée avec succès") if ok else print("- utilisateur non crée")

    elif sys.argv[1] == "clean":
        #ok = delete_banque()
        print(
            "+ prog effacé avec succès") if ok else print("- prog non effacé")