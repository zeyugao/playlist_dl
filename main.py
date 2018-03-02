# encoding=utf-8
# python3
from netease import download_playist
import getopt
import sys


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], '', [''])
    except getopt.GetoptError as e:
        print(e)
        return
    download_playist(args[0])


if __name__ == '__main__':
    main()
