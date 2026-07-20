import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """
    Always logs to stderr, never stdout. This matters specifically for the
    MCP stdio servers (tools/*/server.py): stdout is the JSON-RPC channel
    between server and client, and any stray non-JSON line on stdout (like
    a log message) breaks the protocol parser on the client side.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(
            logging.Formatter("[%(asctime)s] %(levelname)-7s %(name)s: %(message)s",
                               datefmt="%H:%M:%S")
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
