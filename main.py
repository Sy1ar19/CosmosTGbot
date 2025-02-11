import asyncio
import logging
import sys
from bot import run_bot

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    asyncio.run(run_bot())
