#!/usr/bin/env python3

import subprocess

def start_server():
    subprocess.call(['python3', 'src/routes.py'])

if __name__ == '__main__':
    start_server()
