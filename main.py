#!/usr/bin/python3

import subprocess
import json
import os
import sys

"""
Dans notre diagramme le scénario est le suivant:
H est déjà ami avec E
D est déjà ami avec E
E est déjà ami avec D
D est déjà ami avec H
G est déjà ami avec D

./main.py dejaAmis H E
./main.py dejaAmis D E
./main.py dejaAmis E D
./main.py dejaAmis D H
./main.py dejaAmis G D

on crée le nouvel utilisateur F qui va avoir comme parrain E
F a la clé pub. de E
et en retour E reçoit la clé pub. de F
./main.py newUser F E


F fait une demande d'ami à G

TODO

./main.py ami F G
"""




def process(cmd):
    process = subprocess.run(cmd, capture_output=True, shell=True)
    if process.returncode == 0:
        return True, process.stdout.decode("utf-8")
    else:
        print(process.stderr.decode("utf-8"))
        return False, ""

def demandeDAmi(demandeur, demandee):
    print("demande d'ami de "+demandeur+" à "+demandee)
    #On recoit en paramètre le nom de celui qui demande et le nom de celui à qui la demande d'ami est envoyée. (ex. ./main.py ami F G)
    ok = os.path.exists("people/"+demandeur)
    if not ok:
        print("Erreur, nom d'utilisateur du demandeur n'existe pas")
        return False

    ok = os.path.exists("people/"+demandee)
    if not ok:
        print("Erreur, nom d'utilisateur du demandee n'existe pas")
        return False

    # le demandeur envoit sa liste d'ami au demandee
    ok = os.path.exists("people/"+demandee+"/listeDAmisAAnalyser/")
    if not ok:
        ok = process("mkdir people/"+demandee+"/listeDAmisAAnalyser/")
        if not ok:
            return False
    ok = process("cp people/"+demandeur+"/listeDAmis/* people/"+demandee+"/listeDAmisAAnalyser/")
    if not ok:
        return False
    tierDeConfiance = ""
    # le demandée vérifie dans sa liste d'amis si il possède une des clés reçues du demandeur
    #print("people/"+demandee+"/listeDAmisAAnalyser/")
    for filename in os.listdir("people/"+demandee+"/listeDAmisAAnalyser/"):
        tierDeConfiance = filename.replace(".pub", "")
        if filename.endswith(".pub"): 
            #print(filename)
            #ok, _ = process("find people/"+demandee+"/listeDAmis/ -name "+filename)
            ok = os.path.exists("people/"+demandee+"/listeDAmis/"+filename)
            
            if ok:
                # à comparer clé pub. et privée depuis l'ami tièr de confiance
                # ex: G est ami avec E donc depuis E on vérifie la clé pub. reçue par G (qui prétend être celle de E) avec la clé privée de E
                # générer de nouveau la clé pub. de G dans le fichier 'tmp.pub' pour ensuite comparer le contenu de ce fichier avec la clé pub. reçue par G
                
                ok = process("openssl rsa -in people/"+tierDeConfiance+"/"+tierDeConfiance+".rsa -pubout > people/"+tierDeConfiance+"/tmp.pub")
                if not ok:
                    return False

                ok = process("cmp people/"+demandee+"/listeDAmisAAnalyser/"+filename+" people/"+tierDeConfiance+"/tmp.pub")
                if not ok:
                    print("Erreur, la correspondance n'est pas correcte, faux-ami détecté!")
                    return False
                # vérification OK, la liaison peut être créée, le demandee envoit sa clé pub. au demandeur
                ok = process("cp people/"+demandee+"/"+demandee+".pub people/"+demandeur+"/listeDAmis/")
                if not ok:
                    return False

                return True
    listeDAppels = []
    # TODO si elle n'est pas présente dans listeDAmis/, on va faire la meme demande aux amis du demandee
    ok = rechercheTierDeConfiance(demandee, tierDeConfiance, demandeur, listeDAppels)
    print(listeDappels, tierDeConfiance)

    # A la fin
    # ok = process("rm -rf people/"+demandee+"/listeDAmisAAnalyser/")
    # if not ok:
    #     return False
    
    
    return True

def rechercheTierDeConfiance(personne, tierDeConfiance, demandeur, listeDAppels):
    for filename in os.listdir("people/"+personne+"/listeDAmis/"):
        if filename.endswith(".pub"): 
            ami = filename.replace(".pub", "")
            if ami == tierDeConfiance:
                listeDAppels.append(ami)
                ok = rechercheTierDeConfiance()
                return True

def create_new_user(nomUtilisateur, parrain):
    #recoit en paramètre le nom du nouvel utilisateur et le nom du parrain
    ok = os.path.exists("people/"+nomUtilisateur)
    if ok:
        print("Erreur, nom d'utilisateur donné existe déjà, plantage du programme :p")
        return False
    ok = os.path.exists("people/"+parrain)
    if not ok:
        print("Erreur, nom de l'utilisateur parrain donné n'existe pas,\nvous êtes seul, personne veut de vous!\n\tplantage du programme :p")
        return False

    ok = process("mkdir people/"+nomUtilisateur)
    if not ok:
        return False
    ok = process("mkdir people/"+nomUtilisateur+"/listeDAmis")
    if not ok:
        return False

    # copie de la clé pub. du parrain dans la liste d'ami du nouvel utilisateur
    ok = process("cp people/"+parrain+"/"+parrain+".pub people/"+nomUtilisateur+"/listeDAmis/")
    if not ok:
        return False

    # creation des clés du nouvel utilisateur
    ok = process("openssl genrsa -out people/"+nomUtilisateur+"/"+nomUtilisateur+".rsa 2048")
    if not ok:
        return False
    ok = process("openssl rsa -in people/"+nomUtilisateur+"/"+nomUtilisateur+".rsa -outform PEM -pubout -out people/"+nomUtilisateur+"/"+nomUtilisateur+".pub")
    if not ok:
        return False

    # copie de la clé pub. du nouvel utilisateur dans la liste d'ami du parrain
    ok = process("cp people/"+nomUtilisateur+"/"+nomUtilisateur+".pub people/"+parrain+"/listeDAmis/")
    if not ok:
        return False
    
    return True

def create_keys(nomAmi1, nomAmi2):
    #crée les liens entre ami via les clés
    #création de clés et des dossiers des personnes si elles n'existent pas
    ok = os.path.exists("people/"+nomAmi1)
    if not ok:
        ok = process("mkdir people/"+nomAmi1)
        if not ok:
            return False
        ok = process("mkdir people/"+nomAmi1+"/listeDAmis")
        if not ok:
            return False
        ok = process("openssl genrsa -out people/"+nomAmi1+"/"+nomAmi1+".rsa 2048")
        if not ok:
            return False
        ok = process("openssl rsa -in people/"+nomAmi1+"/"+nomAmi1+".rsa -outform PEM -pubout -out people/"+nomAmi1+"/"+nomAmi1+".pub")
        if not ok:
            return False

    ok = os.path.exists("people/"+nomAmi2)
    if not ok:
        ok = process("mkdir people/"+nomAmi2)
        if not ok:
            return False
        ok = process("mkdir people/"+nomAmi2+"/listeDAmis")
        if not ok:
            return False
        ok = process("openssl genrsa -out people/"+nomAmi2+"/"+nomAmi2+".rsa 2048")
        if not ok:
            return False
        ok = process("openssl rsa -in people/"+nomAmi2+"/"+nomAmi2+".rsa -outform PEM -pubout -out people/"+nomAmi2+"/"+nomAmi2+".pub")
        if not ok:
            return False

    # copie de la clé pub de ami2 vers le dossier d'amis d'ami1
    ok = process("cp people/"+nomAmi2+"/"+nomAmi2+".pub people/"+nomAmi1+"/listeDAmis/")
    if not ok:
        return False




    return True
    
def clean():
    ok, _ = process("rm -rf people/*")
    return ok
    


if __name__ == "__main__":

    if(sys.argv[1] == "ami"):
        ok = demandeDAmi(sys.argv[2], sys.argv[3])
        print(
            "+ demande d'ami effectué avec succès") if ok else print("- demande d'ami non créée")

    if(sys.argv[1] == "newUser"):
        ok = create_new_user(sys.argv[2], sys.argv[3])
        print(
            "+ utilisateur crée avec succès") if ok else print("- utilisateur non crée")

    if(sys.argv[1] == "dejaAmis"):
        ok = create_keys(sys.argv[2], sys.argv[3])
        print(
            "+ liaison d'amitié entre "+sys.argv[2]+" et "+sys.argv[3]+" crée avec succès") if ok else print("- liaison d'amitié non créée")

    elif(sys.argv[1] == "clean"):
        ok = clean()
        print(
            "+ prog effacé avec succès") if ok else print("- prog non effacé")

    # else:
    #     print("\ntemplate:")
    #     print("\t./main.py ami <ami1> <ami2>")
    #     print("\t./main.py newUser <nomNouvelUtilisateur> <nomDuParrain>")
    #     print("\t./main.py dejaAmis <ami1> <ami2>")
    #     print("\t./main.py clean")
        