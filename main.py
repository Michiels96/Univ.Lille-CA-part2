#!/usr/bin/python3

import sys
from Service import *


def main():
    service = Service("test.json")
    print(service.db)
    service.save_db()


if __name__ == "__main__":
    main()
