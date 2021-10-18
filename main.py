#!/usr/bin/python3

import sys
import subprocess
import os
import json

ROOT_DIR = "users"

def process(cmd):
    """
    """
    process = subprocess.run(cmd, capture_output=True, shell=True)
    process.check_returncode()
    try:
        return True, process.stdout.decode("utf-8")
    except subprocess.CalledProcessError as e:
        print(e)
        return False, ""


def create_keys(user):
    """
    """
    ok, _ = process(f"mkdir -p {ROOT_DIR}/{user}/friends && openssl genrsa -out {ROOT_DIR}/{user}/{user}.rsa 2048")
    if not ok:
        return False

    ok, _ = process(f"openssl rsa -in {ROOT_DIR}/{user}/{user}.rsa -outform PEM -pubout -out {ROOT_DIR}/{user}/{user}.pub")
    return ok


def init():
    """
    """
    ok, _ = process(f"mkdir {ROOT_DIR}")
    if not ok:
        return False

    # Create root user and two init users
    ok = create_keys("root") and add_user("A", "root") and add_user("B", "root")
    if not ok:
        return False

    # Link the two previous users
    ok = exchange_pubkeys("A", "B", is_direct=True)
    if not ok:
        return False

    # Delete Root user 
    ok, _ = process(f"rm -r {ROOT_DIR}/root")
    return ok


def clean():
    """
    """
    ok, _ = process(f"rm -r {ROOT_DIR}")
    return ok



def add_user(new_user, godfather):
    """
    """
    return create_keys(new_user) and exchange_pubkeys(new_user, godfather, is_direct=True)


def all_paths(src, dst, explored):
    """
    Search an user in the neighborhood
    """
    paths = []
    explored.append(f"{src}.pub")
    if (src == dst):
        paths.append([])
    else:
        for friend in [file.split(".")[0] for file in os.listdir(f"{ROOT_DIR}/{src}/friends") if file not in explored]:
            for path in all_paths(friend, dst, explored):
                # path.insert(0, friend)
                path.append(friend)
                paths.append(path)
    return paths


def best_path(paths):
    """
    """
    paths.sort()
    return paths[0]

def sign_message_by_user(user, message):
    """
    """
    ok, _ = process(
        f"openssl dgst -sha1 -sign {ROOT_DIR}/{user}/{user}.rsa -binary message | openssl enc -base64")
    if not ok:
        return ""

    # Parsing du certificat en un format transportable
    with open("signature.sign", "rb") as f:
        signature = f.read()

    ok, _ = process(f"rm signature.sign")

    return signature



def send_pubkey_by_path(path):
    """
    """
    path.reverse()
    for i, user in enumerate(path):
        if i == 0:
            # Sign the pub key
            signature = sign_message_by_user(user, {ROOT_DIR}/{path[-2]}/{path[-2]}.pub)

            # Crypt pubkey
            ok, signed_pubkey = process(f"openssl rsautl -encrypt -pubin -inkey {ROOT_DIR}/{user}/{path[i+1]}.pub -in {ROOT_DIR}/{user}/{path[-1]}.pub | openssl enc -base64")
            if not ok:
                return ok

            # Send the request to the next user
            with open("answer.json", "w") as f:
                f.write(json.dumps({
                    "signature": signature,
                    "signed_pubkey": signed_pubkey
                }))
            ok, _ = process(f"mv answer.json {ROOT_DIR}/{path[i+1]}/")
            if not ok:
                return ok
        elif i == len(path) - 2:
            # Decrypt and store pubkey
            # Crypt his pubkey
            # Send the request (pubkey + signature) to the next user
            return True
        elif i == len(path) - 1:
            # Decrypt and store pubkey
            # Verify signature
            # Send the request (pubkey + signature) to the next user
            return True
        else:
            # Decrypt pubkey
            # Crypt pubkey
            # Send the request to the next user
            return True 
    return True

def exchange_pubkeys(requester, requested, is_direct=False):
    """
    """
    err_msg = ""
    if is_direct:
        ok, _ = process(f"cp {ROOT_DIR}/{requester}/{requester}.pub {ROOT_DIR}/{requested}/friends/ && cp {ROOT_DIR}/{requested}/{requested}.pub {ROOT_DIR}/{requester}/friends/")
        if not ok:
            err_msg = "+ Clefs publique non échangées"
    else:
        paths = all_paths(requested, requester, ["root.pub"])
        if len(paths) == 0:
            return False, "+ Aucuns amis en commun"

        # Récuperation de la clef publique du demandé
        ok, requested_pub = process(f"cat {ROOT_DIR}/{requested}/{requested}.pub")
        if not ok:
            return False, ""

        path = best_path(paths)
        print(f"+ Best path: {path}")
        send_pubkey_by_path([path[0]] + [requested] + path[1:])


    return True, err_msg



def main():
    init()
    add_user("C", "B")
    exchange_pubkeys("C", "A")


if __name__ == "__main__":
    main()
