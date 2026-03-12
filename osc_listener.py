#!/usr/bin/env python3
"""Quick OSC listener — prints every incoming message to the terminal."""

import argparse
import datetime
from pythonosc import dispatcher, osc_server


def handle_any(address, *args):
    ts = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    args_str = "  ".join(repr(a) for a in args) if args else "(no args)"
    print(f"[{ts}]  {address}   {args_str}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OSC listener")
    parser.add_argument("--host", default="0.0.0.0", help="Bind address (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=3333, help="UDP port (default: 3333)")
    args = parser.parse_args()

    d = dispatcher.Dispatcher()
    d.set_default_handler(handle_any)

    server = osc_server.ThreadingOSCUDPServer((args.host, args.port), d)
    print(f"Listening for OSC on {args.host}:{args.port}  (Ctrl+C to stop)\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
