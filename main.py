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

def verify_signature(user, signature, message):
    """
    """
    # Convertir le certificat en binaire
    with open("tmp.sign", "wb") as f:
        f.write(signature.encode("latin-1"))
    
    # Convertir le certificat en binaire
    with open("from.tmp", "w") as f:
        f.write(message)

    # Vérification du certificat du client
    ok, _ = process(
        f"(openssl dgst -sha1 -verify {ROOT_DIR}/{user}/{user}.pub -signature tmp.sign from.tmp)")

    _, _ = process("rm from.tmp tmp.sign")

    return ok

def arrange_paths(paths, user):
    """
    """
    print(paths) # F E D => F G E D
    
    return  [[path[-1]] + [user] + path[:-1] for path in paths]


def create_keys(user):
    """
    """
    ok, _ = process(f"mkdir -p {ROOT_DIR}/{user}/friends && openssl genrsa -out {ROOT_DIR}/{user}/{user}.rsa 2048")
    if not ok:
        return False

    ok, _ = process(f"openssl rsa -in {ROOT_DIR}/{user}/{user}.rsa -outform PEM -pubout -out {ROOT_DIR}/{user}/{user}.pub")
    return ok


def init(user1, user2):
    """
    """
    ok, _ = process(f"mkdir {ROOT_DIR}")
    if not ok:
        return False

    # Create root user and two init users
    ok = create_keys("root") and add_user(user1, "root") and add_user(user2, "root")
    if not ok:
        return False

    # Link the two previous users
    ok = exchange_pubkeys(user1, user2, is_direct=True)
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
                path.insert(0, friend)
                # path.append(friend)
                paths.append(path)
    return paths


def best_path(paths):
    """
    """
    paths.sort()
    return paths[0]


def send_pubkey_by_path(path):
    """
    """
    path.reverse()
    for i, user in enumerate(path):
        if i == 0:
            # Sign the pub key
            ok, _ = process(
                f"openssl dgst -sha1 -sign {ROOT_DIR}/{user}/{user}.rsa -out pubkey.sign {ROOT_DIR}/{path[-2]}/{path[-2]}.pub ")
            if not ok:
                return True
            
            # Parsing du certificat en un format transportable
            with open("pubkey.sign", "rb") as f:
                signature = f.read()

            ok, _ = process(f"rm pubkey.sign")

    
            # Crypt pubkey
            # print(f"{ROOT_DIR}/{user}/friends/{path[i+1]}.pub", f"{ROOT_DIR}/{user}/friends/{path[-1]}.pub")
            # print(f"openssl rsautl -encrypt -pubin -inkey {ROOT_DIR}/{user}/friends/{path[i+1]}.pub -in {ROOT_DIR}/{user}/friends/{path[-1]}.pub | openssl enc -base64")
            # ok, signed_pubkey = process(f"openssl -encrypt -pubin -inkey {ROOT_DIR}/{user}/friends/{path[i+1]}.pub -in {ROOT_DIR}/{user}/friends/{path[-1]}.pub | openssl enc -base64")
            ok, pubkey = process(f"cat {ROOT_DIR}/{user}/friends/{path[-1]}.pub")
            if not ok:
                return ok

            # Send the request to the next user
            with open("answer.json", "w") as f:
                f.write(json.dumps({
                    "signature": signature.decode("latin-1"),
                    "signed_pubkey": "\n" + pubkey
                }))
            ok, _ = process(f"mv answer.json {ROOT_DIR}/{path[i+1]}/")
            if not ok:
                return ok

        elif i == len(path) - 2:
            with open(f"{ROOT_DIR}/{user}/answer.json", "r") as f:
                answer = json.load(f)

            # Store incoming pubkey
            pubkey = answer["signed_pubkey"] # Should be decrypted
            ok, _ = process(
                f"cat > {ROOT_DIR}/{user}/friends/{path[-1]}.pub << EOF && echo -e {pubkey}")
            if not ok:
                return ok

            # Crypt his pubkey
            ok, pubkey = process(f"cat {ROOT_DIR}/{user}/{user}.pub") # Should be encryted
            if not ok:
                return ok
            answer["signed_pubkey"] = "\n" + pubkey

            # Send the request (pubkey + signature) to the next user
            with open(f"{ROOT_DIR}/{user}/answer.json", "w") as f:
                    f.write(json.dumps(answer))
            ok, _ = process(f"mv {ROOT_DIR}/{user}/answer.json {ROOT_DIR}/{path[i+1]}/")

            if not ok:
                return ok
        
        elif i == len(path) - 1:
            with open(f"{ROOT_DIR}/{user}/answer.json", "r") as f:
                answer = json.load(f)
            # Decrypt pubkey
            pubkey = answer["signed_pubkey"] # Should be decrypt

            # Verify signature
            if not verify_signature(path[0], answer["signature"], pubkey[1:]):
                return False

            # Store pubkey
            ok, _ = process(
                f"cat > {ROOT_DIR}/{user}/friends/{path[-2]}.pub << EOF && echo -e {pubkey}")
            if not ok:
                return ok
    
        else:
            with open(f"{ROOT_DIR}/{user}/answer.json", "r") as f:
                answer = json.load(f)
            # Decrypt pubkey
            pubkey = answer["signed_pubkey"] # Should be decrypt

            # Crypt pubkey again
            answer["signed_pubkey"] = "\n" + pubkey

            # Send the request to the next user
            with open(f"{ROOT_DIR}/{user}/answer.json", "w") as f:
                    f.write(json.dumps(answer))
            ok, _ = process(f"mv {ROOT_DIR}/{user}/answer.json {ROOT_DIR}/{path[i+1]}/")
            if not ok:
                return ok

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
        paths = arrange_paths(all_paths(requested, requester, ["root.pub"]), requested)
        print("+ The paths are:")
        for p in paths:
            print(f"\t+ {p}")

        if len(paths) == 0:
            return False, "+ Aucuns amis en commun"

        # Récuperation de la clef publique du demandé
        ok, requested_pub = process(f"cat {ROOT_DIR}/{requested}/{requested}.pub")
        if not ok:
            return False, ""

        path = best_path(paths)
        print(f"\n+ Best path: {path}")
        ok = send_pubkey_by_path(path)


    return ok, err_msg



def main():
    init("D", "E")
    add_user("F", "E")
    add_user("G", "D")
    exchange_pubkeys("F", "G")
    add_user("H", "D")
    exchange_pubkeys("H", "E")


if __name__ == "__main__":
    main()
