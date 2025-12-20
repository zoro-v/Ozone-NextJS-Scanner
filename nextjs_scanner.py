import argparse
import re
import time
import requests
import sys
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# الألوان
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
           {Colors.RED}Next.js Scanner v1.0{Colors.RESET}
    """
    print(banner)

def scan_target(url):
    if not url.startswith("http"):
        url = "https://" + url

    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}Targeting: {url}{Colors.RESET}")

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # ملاحظة: إذا كنت تستخدم WSL ولم يعمل، فعل السطر التالي
    # options.binary_location = "/usr/bin/chromium-browser"

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        print(f"{Colors.YELLOW}[*] Browser launched, fetching page...{Colors.RESET}")
        driver.get(url)
        time.sleep(5) # انتظار تحميل الجافاسكريبت
        html = driver.page_source
        driver.quit()
    except Exception as e:
        print(f"{Colors.RED}[!] Selenium Error: {e}{Colors.RESET}")
        return

    # 1. استخراج buildId
    build_id_match = re.search(r'"buildId":"([^"]+)"', html)
    build_id = ""
    
    if build_id_match:
        build_id = build_id_match.group(1)
        print(f"{Colors.GREEN}[+] Found buildId: {Colors.BOLD}{build_id}{Colors.RESET}")
    else:
        print(f"{Colors.RED}[-] No buildId found. Site might not be Next.js.{Colors.RESET}")
        return

    # 2. استخراج الروابط الداخلية
    links = re.findall(r'"link":"(/[^"]+)"', html)
    unique_links = list(set(links))
    print(f"{Colors.CYAN}[*] Found {len(unique_links)} potential Next.js routes.{Colors.RESET}")

    # 3. تخمين وفحص روابط JSON
    print(f"\n{Colors.YELLOW}[*] Fuzzing _next/data endpoints...{Colors.RESET}")
    
    for link in unique_links:
      
        json_url = urljoin(url, f"/_next/data/{build_id}{link}.json")
        
        try:
            res = requests.get(json_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            if res.status_code == 200:
                print(f"[{Colors.GREEN}{res.status_code}{Colors.RESET}] {json_url}")
            else:
                # نخفي الأخطاء لتقليل الإزعاج، أو نظهرها باللون الأحمر
                pass 
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
        scan_target(args.url)
    elif args.list:
        try:
            with open(args.list, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
            for url in urls:
                scan_target(url)
        except FileNotFoundError:
            print(f"{Colors.RED}[!] File not found.{Colors.RESET}")

if __name__ == "__main__":
    main()
