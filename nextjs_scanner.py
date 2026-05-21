import asyncio
import argparse
import re
import requests
from urllib.parse import urljoin
from playwright.async_api import async_playwright

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_banner():
    banner = f"""{Colors.CYAN}
      ___  ____  ___  _  _  ____
     / _ \(__  )/ _ \( \( )(  __)
    ( (_) )/ _/( (_) ))  (  ) _)
     \___/(____)\___/(_)\_)(____)
           {Colors.RED}Next.js Scanner v2.0{Colors.RESET}
    """
    print(banner)

async def scan_target(url):
    if not url.startswith("http"):
        url = "https://" + url

    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}Targeting: {url}{Colors.RESET}")

    html = ""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        try:
            print(f"{Colors.YELLOW}[*] Fetching page...{Colors.RESET}")
            await page.goto(url, wait_until="networkidle", timeout=30000)
            html = await page.content()
        except Exception as e:
            print(f"{Colors.RED}[!] Browser Error: {e}{Colors.RESET}")
        finally:
            await browser.close()

    if not html:
        return

    # 1. Extract buildId
    build_id_match = re.search(r'"buildId":"([^"]+)"', html)
    if not build_id_match:
        print(f"{Colors.RED}[-] No buildId found. Site might not be Next.js.{Colors.RESET}")
        return

    build_id = build_id_match.group(1)
    print(f"{Colors.GREEN}[+] Found buildId: {Colors.BOLD}{build_id}{Colors.RESET}")

    # 2. Extract internal routes
    links = list(set(re.findall(r'"link":"(/[^"]+)"', html)))
    print(f"{Colors.CYAN}[*] Found {len(links)} potential Next.js routes.{Colors.RESET}")

    # 3. Fuzz _next/data endpoints
    print(f"\n{Colors.YELLOW}[*] Fuzzing _next/data endpoints...{Colors.RESET}")
    for link in links:
        json_url = urljoin(url, f"/_next/data/{build_id}{link}.json")
        try:
            res = requests.get(
                json_url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0"},
                timeout=10
            )
            if res.status_code == 200:
                print(f"[{Colors.GREEN}{res.status_code}{Colors.RESET}] {json_url}")
        except Exception as e:
            print(f"{Colors.RED}[Error] {e}{Colors.RESET}")

def main():
    print_banner()
    parser = argparse.ArgumentParser(description="Ozone Next.js Scanner")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-u', '--url', help="Target URL")
    group.add_argument('-l', '--list', help="List of URLs")

    args = parser.parse_args()

    if args.url:
        asyncio.run(scan_target(args.url))
    elif args.list:
        try:
            with open(args.list, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
            for url in urls:
                asyncio.run(scan_target(url))
        except FileNotFoundError:
            print(f"{Colors.RED}[!] File not found.{Colors.RESET}")

if __name__ == "__main__":
    main()
