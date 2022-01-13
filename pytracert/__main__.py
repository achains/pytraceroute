import argparse
import sys

from pytracert.Pytracert import Pytracert


def main(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--hops",
        type=int,
        help="Set maximum hops to destination",
        default=30
    )

    parser.add_argument(
        "--destination",
        "-d",
        type=str,
        help="Destination domain name"
    )

    args = parser.parse_args(args=argv)

    tracert = Pytracert(destination=args.destination, hops=args.hops)

    return tracert.run()


if __name__ == "__main__":
    main(sys.argv[1:])
