#!/usr/bin/env python

import craterstats.cli as cli
import multiprocessing

if __name__ == "__main__":
    multiprocessing.freeze_support()
    cli.main(None)
