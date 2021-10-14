import json
import subprocess


class Service:

    def __init__(self, db_name):
        """
        """
        self._db_name = db_name
        self.db = self._load_db()

    def _process(cmd):
        """
        """
        process = subprocess.run(cmd, capture_output=True, shell=True)
        process.check_returncode()
        try:
            return True, process.stdout.decode("utf-8")
        except subprocess.CalledProcessError as e:
            print(e)
            return False, ""

    def _load_db(self):
        """
        """
        try:
            with open(self._db_name, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_db(self):
        """
        """
        with open(self._db_name, "w") as f:
            f.write(json.dumps(self.db))

    def add_user(self, username):
        """
        TODO: Ajouter un uilisateur à notre réseau
        """
        pass

    def auth_users(src, dst):
        """
        TODO: Fonction recursive
        """
        pass

    def exchange_pubkey(path):
        """
        TODO: échanger les clefs publiques en suivant un chemin donné (ex. [A, C, D, E]) 
        """
        pass
