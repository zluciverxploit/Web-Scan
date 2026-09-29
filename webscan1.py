#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════╗
║        TERMUX WEBSCAN PRO - 100 FITUR PENTEST            ║
║              Developer: Ari Marshello                    ║
║           AUTO SCAN MODE - Full Automation               ║
║           For Educational Purpose Only                   ║
╚══════════════════════════════════════════════════════════╝
"""

import os, sys, time, socket, ssl, json, re, base64, hashlib, random, string
import argparse, concurrent.futures, subprocess
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urlencode, quote
from collections import defaultdict

try:
    import requests
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
    from rich.prompt import Prompt
    from rich.text import Text
    from rich.rule import Rule
    from rich import box
    import dns.resolver
    from bs4 import BeautifulSoup
except ImportError:
    os.system("pip install rich requests dnspython beautifulsoup4 urllib3")
    import requests
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
    from rich.prompt import Prompt
    from rich.text import Text
    from rich.rule import Rule
    from rich import box
    import dns.resolver
    from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings()

# ═══════════════════════════════════════════════
# KONFIGURASI GLOBAL
# ═══════════════════════════════════════════════
DEVELOPER = "Ari Marshello"
VERSION   = "3.0.0"
LOG_FILE  = "webscan_report.txt"

console = Console()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0 Safari/537.36 WebScanPro/3.0"
}

BANNER = r"""
[bold red]
 ██╗    ██╗███████╗██████╗ ███████╗ ██████╗ █████╗ ███╗   ██╗
 ██║    ██║██╔════╝██╔══██╗██╔════╝██╔════╝██╔══██╗████╗  ██║
 ██║ █╗ ██║█████╗  ██████╔╝███████╗██║     ███████║██╔██╗ ██║
 ██║███╗██║██╔══╝  ██╔══██╗╚════██║██║     ██╔══██║██║╚██╗██║
 ╚███╔███╔╝███████╗██████╔╝███████║╚██████╗██║  ██║██║ ╚████║
  ╚══╝╚══╝ ╚══════╝╚═════╝ ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝
[/bold red]
[bold cyan]              ⚡ TERMUX WEBSCAN PRO ⚡[/bold cyan]
[bold yellow]           Developer : Ari Marshello[/bold yellow]
[bold green]           Version   : 3.0.0 | 100 Features[/bold green]
[bold magenta]           Mode      : AUTO SCAN (Full Automation)[/bold magenta]
"""

# ═══════════════════════════════════════════════
# UTILITY
# ═══════════════════════════════════════════════
def log(msg, level="info"):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] [{level.upper()}] {msg}\n")
    except Exception:
        pass


def normalize_url(url):
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    return url.rstrip("/")


def get_host(url):
    return urlparse(normalize_url(url)).hostname


def section(num, title, icon="🔹"):
    console.print()
    console.print(Rule(f"[bold yellow]{icon} [{num}/100] {title}[/bold yellow]", style="red"))
    console.print()


def req(url, method="GET", timeout=6, **kw):
    try:
        return requests.request(method, url, headers=HEADERS,
                                timeout=timeout, verify=False,
                                allow_redirects=True, **kw)
    except Exception:
        return None


def safe_print(msg, style="white"):
    try:
        console.print(f"[{style}]{msg}[/{style}]")
    except Exception:
        pass


# ═══════════════════════════════════════════════
# 100 FITUR PENTEST (RINGKAS & CEPAT)
# ═══════════════════════════════════════════════

# ── 1. HTTP Headers ──
def f001(url, R):
    section(1, "HTTP Headers", "📋")
    r = req(url)
    if not r: safe_print("✗ Gagal", "red"); return
    t = Table(border_style="cyan")
    t.add_column("Header", style="green"); t.add_column("Value", style="white")
    for k, v in list(r.headers.items())[:20]:
        t.add_row(k, v[:80])
    console.print(t)
    R["headers"] = dict(r.headers)


# ── 2. Status Code ──
def f002(url, R):
    section(2, "Status Code Check", "🔢")
    r = req(url)
    if r:
        console.print(f"[yellow]Status:[/yellow] {r.status_code}")
        R["status"] = r.status_code


# ── 3. SSL/TLS ──
def f003(url, R):
    section(3, "SSL/TLS Info", "🔒")
    try:
        ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
        with socket.create_connection((get_host(url), 443), timeout=6) as s:
            with ctx.wrap_socket(s, server_hostname=get_host(url)) as ss:
                cert = ss.getpeercert(); ver = ss.version()
        console.print(f"[green]TLS:[/green] {ver}")
        console.print(f"[green]Subject:[/green] {cert.get('subject')}")
        console.print(f"[green]Issuer:[/green] {cert.get('issuer')}")
        R["ssl"] = {"ver": ver, "subject": str(cert.get('subject'))}
    except Exception as e:
        safe_print(f"⚠ {e}", "yellow")


# ── 4. Port Scanner ──
TOP_PORTS = [21,22,23,25,53,80,110,111,135,139,143,443,445,993,995,1723,
             3306,3389,5432,5900,6379,8080,8443,8888,9200,27017,5000,5001,
             11211,2049,1521,1433,161,389,636,873,1080,3128,4444,4848,5555,
             7001,7002,8181,9080,9443,10000,20000,30000,40000,50000,1234,
             1235,1010,1025,5555,6666,7777,8000,8008,8880,9000,9090,9999,
             554,1935,5060,5061,161,162,88,464,749,750,123,137,138,179,
             513,514,587,993,995,1080,1720,1812,1813,3268,3269,5222,5269,
             5353,5500,5601,5672,5984,6380,6443,6667,7000,7474,8009,8180,
             8443,8500,8888,9042,9092,9160,9300,9999,11211,15672,25565]

def _scan_p(ip, p):
    try:
        s = socket.socket(); s.settimeout(0.8)
        r = s.connect_ex((ip, p)); s.close()
        return p if r == 0 else None
    except Exception:
        return None


def f004(url, R):
    section(4, "Port Scanner", "🔍")
    host = get_host(url)
    try:
        ip = socket.gethostbyname(host)
    except Exception:
        safe_print("✗ Host tidak resolve", "red"); return
    open_ports = []
    with Progress(SpinnerColumn(), TextColumn("[cyan]scanning"),
                  BarColumn(), TextColumn("{task.completed}/{task.total}"),
                  console=console) as pr:
        task = pr.add_task("port", total=len(TOP_PORTS))
        with concurrent.futures.ThreadPoolExecutor(max_workers=300) as ex:
            for f in concurrent.futures.as_completed(
                    [ex.submit(_scan_p, ip, p) for p in TOP_PORTS]):
                res = f.result()
                if res: open_ports.append(res)
                pr.advance(task)
    if open_ports:
        t = Table(border_style="green")
        t.add_column("Port", style="yellow"); t.add_column("Service", style="cyan")
        svc = {21:"FTP",22:"SSH",23:"Telnet",80:"HTTP",443:"HTTPS",3306:"MySQL",
               3389:"RDP",5432:"PostgreSQL",6379:"Redis",8080:"HTTP-Alt",
               27017:"MongoDB",9200:"Elastic",11211:"Memcached"}
        for p in sorted(open_ports):
            t.add_row(str(p), svc.get(p, "Unknown"))
        console.print(t)
    else:
        safe_print("⚠ Tidak ada port terbuka", "yellow")
    R["ports"] = open_ports


# ── 5. DNS Enumeration ──
def f005(url, R):
    section(5, "DNS Records", "📡")
    host = get_host(url)
    t = Table(border_style="cyan")
    t.add_column("Type", style="yellow"); t.add_column("Value", style="white")
    res = {}
    for rec in ["A","AAAA","MX","NS","TXT","CNAME","SOA"]:
        try:
            for a in dns.resolver.resolve(host, rec, lifetime=4):
                t.add_row(rec, str(a)[:100])
            res[rec] = [str(a) for a in dns.resolver.resolve(host, rec, lifetime=4)]
        except Exception:
            res[rec] = []
    console.print(t)
    R["dns"] = res


# ── 6. WHOIS ──
def f006(url, R):
    section(6, "WHOIS Lookup", "🌐")
    try:
        r = requests.get(f"https://api.hackertarget.com/whois/?q={get_host(url)}",
                         headers=HEADERS, timeout=15)
        console.print(Panel(r.text[:2000], border_style="green"))
        R["whois"] = r.text[:2000]
    except Exception as e:
        safe_print(f"✗ {e}", "red")


# ── 7. Robots.txt ──
def f007(url, R):
    section(7, "Robots.txt", "🤖")
    r = req(url + "/robots.txt")
    if r and r.status_code == 200:
        console.print(Panel(r.text[:1500], border_style="green"))
        R["robots"] = r.text[:1500]
    else:
        safe_print("⚠ Tidak ditemukan", "yellow")


# ── 8. Sitemap.xml ──
def f008(url, R):
    section(8, "Sitemap.xml", "🗺️")
    for p in ["/sitemap.xml","/sitemap_index.xml","/sitemap-index.xml"]:
        r = req(url + p)
        if r and r.status_code == 200 and "<url" in r.text.lower():
            urls = re.findall(r"<loc>(.*?)</loc>", r.text)
            console.print(f"[green]✓ Ditemukan:[/green] {p} ({len(urls)} URLs)")
            for u in urls[:10]: console.print(f"  [cyan]→[/cyan] {u[:90]}")
            R["sitemap"] = urls
            return
    safe_print("⚠ Tidak ada sitemap", "yellow")


# ── 9. Security Headers ──
def f009(url, R):
    section(9, "Security Headers", "🛡️")
    r = req(url)
    if not r: return
    checks = ["Strict-Transport-Security","Content-Security-Policy",
              "X-Frame-Options","X-Content-Type-Options","Referrer-Policy",
              "Permissions-Policy","X-XSS-Protection"]
    missing = []
    for h in checks:
        if h in r.headers:
            console.print(f"[green]✓[/green] {h}")
        else:
            console.print(f"[red]✗[/red] {h}")
            missing.append(h)
    R["missing_sec_headers"] = missing


# ── 10. Cookie Audit ──
def f010(url, R):
    section(10, "Cookie Audit", "🍪")
    r = req(url)
    if not r or not r.cookies:
        safe_print("⚠ Tidak ada cookie", "yellow"); return
    for c in r.cookies:
        s = "✓" if c.secure else "✗"
        console.print(f"[yellow]{c.name}[/yellow] | Secure:{s}")


# ── 11. HTTP Methods ──
def f011(url, R):
    section(11, "HTTP Methods", "🔧")
    allowed = []
    for m in ["GET","POST","PUT","DELETE","OPTIONS","HEAD","PATCH","TRACE"]:
        r = req(url, method=m, timeout=4)
        if r:
            ok = r.status_code < 400
            if ok: allowed.append(m)
            console.print(f"[yellow]{m:8}[/yellow] → {r.status_code} {'✓' if ok else '✗'}")
    R["methods"] = allowed


# ── 12. Server Info ──
def f012(url, R):
    section(12, "Server Info", "🖥️")
    r = req(url)
    if r:
        console.print(f"[cyan]Server:[/cyan] {r.headers.get('Server','N/A')}")
        console.print(f"[cyan]Powered:[/cyan] {r.headers.get('X-Powered-By','N/A')}")
        R["server"] = r.headers.get('Server','')


# ── 13. Redirect Chain ──
def f013(url, R):
    section(13, "Redirect Chain", "↪️")
    try:
        r = requests.get(url, headers=HEADERS, timeout=8, verify=False)
        chain = [h.status_code for h in r.history]
        console.print(f"[yellow]Chain:[/yellow] {chain} → {r.status_code}")
        console.print(f"[yellow]Final:[/yellow] {r.url}")
        R["redirects"] = chain
    except Exception as e:
        safe_print(f"✗ {e}", "red")


# ── 14. Tech Fingerprint ──
def f014(url, R):
    section(14, "Tech Fingerprint", "⚙️")
    r = req(url)
    if not r: return
    html = r.text.lower(); hdrs = str(r.headers).lower()
    checks = {"WordPress":["wp-content"],"Joomla":["joomla"],"Drupal":["drupal"],
              "React":["react"],"Vue":["vue.js"],"Angular":["ng-version"],
              "jQuery":["jquery"],"Bootstrap":["bootstrap"],"Tailwind":["tailwind"],
              "Nginx":["nginx"],"Apache":["apache"],"Cloudflare":["cloudflare"],
              "PHP":["php"],"ASP.NET":["asp.net"],"Node":["node"],"Laravel":["laravel"]}
    techs = [n for n, s in checks.items() if any(x in html or x in hdrs for x in s)]
    for t in techs: console.print(f"[green]✓[/green] {t}")
    if not techs: safe_print("⚠ Tidak terdeteksi", "yellow")
    R["tech"] = techs


# ── 15. CMS Detector ──
def f015(url, R):
    section(15, "CMS Detector", "🧩")
    r = req(url)
    if not r: return
    html = r.text.lower()
    cms = "Unknown"
    for n, s in [("WordPress","wp-content"),("Joomla","joomla"),("Drupal","drupal"),
                 ("Magento","magento"),("Shopify","shopify"),("Blogger","blogspot")]:
        if s in html: cms = n; break
    console.print(f"[yellow]CMS:[/yellow] {cms}")
    R["cms"] = cms


# ── 16. XSS Scanner ──
XSS_PL = ['<script>alert(1)</script>','"><img src=x onerror=alert(1)>',"'><svg/onload=alert(1)>"]

def f016(url, R):
    section(16, "XSS Scanner", "💉")
    p = urlparse(url)
    if not p.query: safe_print("⚠ Tidak ada parameter", "yellow"); return
    params = parse_qs(p.query)
    vulns = []
    for prm in params:
        for pl in XSS_PL:
            q = urlencode({**params, prm: pl})
            test = f"{p.scheme}://{p.netloc}{p.path}?{q}"
            r = req(test)
            if r and pl in r.text:
                vulns.append(prm)
                console.print(f"[red]⚠ XSS di '{prm}'[/red]")
                break
    if not vulns: console.print("[green]✓ Aman[/green]")
    R["xss_vulns"] = vulns


# ── 17. SQLi Scanner ──
SQLI_PL = ["'", "\"", "' OR '1'='1", "1' OR 1=1--"]
SQLI_ERR = ["sql syntax","mysql_fetch","sqlite","postgresql","ora-","sqlstate"]

def f017(url, R):
    section(17, "SQLi Scanner", "🗄️")
    p = urlparse(url)
    if not p.query: safe_print("⚠ Tidak ada parameter", "yellow"); return
    params = parse_qs(p.query)
    vulns = []
    for prm in params:
        for pl in SQLI_PL:
            q = urlencode({**params, prm: pl})
            test = f"{p.scheme}://{p.netloc}{p.path}?{q}"
            r = req(test)
            if r and any(e in r.text.lower() for e in SQLI_ERR):
                vulns.append(prm)
                console.print(f"[red]⚠ SQLi di '{prm}'[/red]")
                break
    if not vulns: console.print("[green]✓ Aman[/green]")
    R["sqli_vulns"] = vulns


# ── 18. Open Redirect ──
def f018(url, R):
    section(18, "Open Redirect", "↪️")
    p = urlparse(url)
    if not p.query: safe_print("⚠ Tidak ada parameter", "yellow"); return
    evil = "https://evil.example.com"
    for prm in parse_qs(p.query):
        r = req(f"{p.scheme}://{p.netloc}{p.path}?{prm}={evil}", timeout=5)
        if r and evil in r.url:
            console.print(f"[red]⚠ Redirect di '{prm}'[/red]")
        else:
            console.print(f"[green]✓ '{prm}' aman[/green]")


# ── 19. CORS ──
def f019(url, R):
    section(19, "CORS Check", "🌍")
    try:
        r = requests.get(url, headers={**HEADERS, "Origin": "https://evil.example.com"},
                         timeout=6, verify=False)
        acao = r.headers.get("Access-Control-Allow-Origin","N/A")
        console.print(f"[cyan]ACAO:[/cyan] {acao}")
        if acao == "*" or "evil" in acao:
            console.print("[red]⚠ Misconfig![/red]")
        else:
            console.print("[green]✓ Aman[/green]")
        R["cors"] = acao
    except Exception: pass


# ── 20. Clickjacking ──
def f020(url, R):
    section(20, "Clickjacking", "🖼️")
    r = req(url)
    if not r: return
    xfo = r.headers.get("X-Frame-Options","")
    csp = r.headers.get("Content-Security-Policy","")
    if xfo or "frame-ancestors" in csp:
        console.print("[green]✓ Terproteksi[/green]")
    else:
        console.print("[red]⚠ Rentan![/red]")


# ── 21. Email Extractor ──
def f021(url, R):
    section(21, "Email Extractor", "📧")
    r = req(url)
    if not r: return
    emails = set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", r.text))
    for e in list(emails)[:20]: console.print(f"[cyan]→[/cyan] {e}")
    if not emails: safe_print("⚠ Tidak ada email", "yellow")
    R["emails"] = list(emails)


# ── 22. Form Finder ──
def f022(url, R):
    section(22, "Form Finder", "📝")
    r = req(url)
    if not r: return
    forms = BeautifulSoup(r.text, "html.parser").find_all("form")
    if not forms: safe_print("⚠ Tidak ada form", "yellow"); return
    for i, f in enumerate(forms, 1):
        console.print(f"[cyan]Form #{i}:[/cyan] {f.get('action','N/A')} [{f.get('method','GET').upper()}]")
    R["forms"] = len(forms)


# ── 23. JS Analyzer ──
def f023(url, R):
    section(23, "JavaScript Files", "📜")
    r = req(url)
    if not r: return
    scripts = BeautifulSoup(r.text, "html.parser").find_all("script", src=True)
    for s in scripts[:15]: console.print(f"[cyan]→[/cyan] {s['src'][:90]}")
    R["scripts"] = [s["src"] for s in scripts]


# ── 24. Link Crawler ──
def f024(url, R):
    section(24, "Link Crawler", "🔗")
    r = req(url)
    if not r: return
    links = set()
    base = urlparse(url)
    for a in BeautifulSoup(r.text, "html.parser").find_all("a", href=True):
        h = a["href"]
        if h.startswith("http"): links.add(h)
        elif h.startswith("/"): links.add(f"{base.scheme}://{base.netloc}{h}")
    console.print(f"[yellow]Total:[/yellow] {len(links)}")
    for l in list(links)[:15]: console.print(f"  [green]→[/green] {l[:90]}")
    R["links"] = list(links)


# ── 25. WAF Detector ──
def f025(url, R):
    section(25, "WAF Detector", "🚧")
    r = req(url)
    if not r: return
    hdrs = str(r.headers).lower()
    sigs = {"Cloudflare":["cf-ray"],"Sucuri":["x-sucuri"],"Akamai":["akamai"],
            "AWS":["x-amzn"],"Imperva":["incap_ses"],"F5":["big-ip"],
            "ModSecurity":["mod_security"],"Fastly":["fastly"]}
    wafs = [w for w, s in sigs.items() if any(x in hdrs for x in s)]
    if wafs: console.print(f"[red]⚠ WAF:[/red] {', '.join(wafs)}")
    else: console.print("[green]✓ Tidak ada WAF[/green]")
    R["waf"] = wafs


# ── 26. Favicon Hash ──
def f026(url, R):
    section(26, "Favicon Hash", "🎯")
    r = req(url + "/favicon.ico")
    if r and r.status_code == 200:
        h = hashlib.md5(r.content).hexdigest()
        console.print(f"[yellow]MD5:[/yellow] {h}")
        R["favicon_hash"] = h
    else: safe_print("⚠ Tidak ada favicon", "yellow")


# ── 27. IP Info ──
def f027(url, R):
    section(27, "IP Info", "🌍")
    try:
        ip = socket.gethostbyname(get_host(url))
        console.print(f"[yellow]IP:[/yellow] {ip}")
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=8)
        d = r.json()
        for k in ["country","regionName","city","isp","org","as"]:
            console.print(f"[cyan]{k}:[/cyan] {d.get(k,'N/A')}")
        R["ip_info"] = d
    except Exception as e:
        safe_print(f"✗ {e}", "red")


# ── 28. Reverse DNS ──
def f028(url, R):
    section(28, "Reverse DNS", "🔄")
    try:
        ip = socket.gethostbyname(get_host(url))
        h = socket.gethostbyaddr(ip)
        console.print(f"[yellow]Hostname:[/yellow] {h[0]}")
        R["rdns"] = h[0]
    except Exception as e:
        safe_print(f"✗ {e}", "yellow")


# ── 29. Traceroute ──
def f029(url, R):
    section(29, "Traceroute", "🛣️")
    try:
        cmd = ["traceroute", "-m", "5", "-w", "2", get_host(url)]
        out = subprocess.check_output(cmd, timeout=20, stderr=subprocess.DEVNULL).decode()
        console.print(out[:1000])
        R["traceroute"] = out[:1000]
    except Exception:
        safe_print("⚠ Traceroute tidak tersedia", "yellow")


# ── 30. Ping Test ──
def f030(url, R):
    section(30, "Ping Test", "🏓")
    try:
        cmd = ["ping", "-c", "3", "-W", "2", get_host(url)]
        out = subprocess.check_output(cmd, timeout=15, stderr=subprocess.DEVNULL).decode()
        console.print(out[:600])
        R["ping"] = "ok"
    except Exception:
        safe_print("⚠ Ping gagal", "yellow")


# ── 31-40: Content & Path Discovery ──
COMMON_PATHS = ["/admin","/login","/wp-admin","/wp-login.php","/dashboard",
                "/api","/v1","/v2","/backup","/config","/uploads","/images",
                "/css","/js","/assets","/includes","/test","/dev","/staging",
                "/private","/secure","/.git","/.env","/phpinfo.php","/info.php",
                "/server-status","/console","/robots.txt","/sitemap.xml",
                "/.htaccess","/web.config","/crossdomain.xml","/clientaccesspolicy.xml",
                "/.well-known/security.txt","/humans.txt","/manifest.json",
                "/swagger.json","/openapi.json","/.git/config","/readme.md"]

def _check_path(base, p):
    try:
        r = requests.get(base + p, headers=HEADERS, timeout=4, verify=False, allow_redirects=False)
        return (p, r.status_code)
    except Exception:
        return None


def f031(url, R):
    section(31, "Path Discovery", "📁")
    base = normalize_url(url)
    found = []
    with Progress(SpinnerColumn(), TextColumn("[cyan]scanning"),
                  BarColumn(), TextColumn("{task.completed}/{task.total}"),
                  console=console) as pr:
        task = pr.add_task("paths", total=len(COMMON_PATHS))
        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as ex:
            for f in concurrent.futures.as_completed(
                    [ex.submit(_check_path, base, p) for p in COMMON_PATHS]):
                res = f.result()
                if res and res[1] in (200,301,302,401,403):
                    found.append(res)
                    c = "green" if res[1] == 200 else "yellow"
                    console.print(f"[{c}]✓[/{c}] [{res[1]}] {res[0]}")
                pr.advance(task)
    R["paths"] = found


def f032(url, R):
    section(32, "Sensitive Files", "🔐")
    files = ["/.env","/.git/config","/config.php","/wp-config.php",
             "/.htaccess","/web.config","/database.yml","/.aws/credentials"]
    for f in files:
        r = req(normalize_url(url) + f, timeout=4)
        if r and r.status_code == 200:
            console.print(f"[red]⚠ Ditemukan:[/red] {f}")


def f033(url, R):
    section(33, "Admin Panels", "👑")
    for p in ["/admin","/administrator","/wp-admin","/cpanel","/phpmyadmin","/adminer"]:
        r = req(normalize_url(url) + p, timeout=4)
        if r and r.status_code in (200,401,403):
            console.print(f"[red]⚠[/red] {p} [{r.status_code}]")


def f034(url, R):
    section(34, "Backup Files", "💾")
    for f in ["/backup.zip","/backup.tar.gz","/backup.sql","/db.sql","/dump.sql",
              "/site.zip","/www.zip","/backup.rar"]:
        r = req(normalize_url(url) + f, timeout=4)
        if r and r.status_code == 200:
            console.print(f"[red]⚠ Ditemukan:[/red] {f}")


def f035(url, R):
    section(35, "Config Files", "⚙️")
    for f in ["/config.json","/config.yaml","/config.xml","/settings.py",
              "/application.properties"]:
        r = req(normalize_url(url) + f, timeout=4)
        if r and r.status_code == 200:
            console.print(f"[red]⚠[/red] {f}")


def f036(url, R):
    section(36, "Directory Listing", "📂")
    for p in ["/uploads/","/images/","/files/","/backup/","/css/","/js/"]:
        r = req(normalize_url(url) + p, timeout=4)
        if r and r.status_code == 200 and "index of" in r.text.lower():
            console.print(f"[red]⚠ Directory Listing:[/red] {p}")


def f037(url, R):
    section(37, "HTTP/2 Support", "⚡")
    try:
        r = requests.get(url, headers=HEADERS, timeout=6, verify=False)
        ver = r.raw.version
        console.print(f"[yellow]HTTP Version:[/yellow] {ver}")
        R["http_ver"] = ver
    except Exception: pass


def f038(url, R):
    section(38, "Compression", "🗜️")
    r = req(url, headers={**HEADERS, "Accept-Encoding": "gzip, deflate, br"})
    if r:
        enc = r.headers.get("Content-Encoding","none")
        console.print(f"[yellow]Encoding:[/yellow] {enc}")
        R["encoding"] = enc


def f039(url, R):
    section(39, "Cache Headers", "💾")
    r = req(url)
    if r:
        for h in ["Cache-Control","Expires","ETag","Last-Modified","Age"]:
            console.print(f"[cyan]{h}:[/cyan] {r.headers.get(h,'N/A')}")


def f040(url, R):
    section(40, "Content-Type", "📄")
    r = req(url)
    if r:
        console.print(f"[yellow]Content-Type:[/yellow] {r.headers.get('Content-Type','N/A')}")
        R["content_type"] = r.headers.get('Content-Type','')


# ── 41-50: Advanced Web Checks ──
def f041(url, R):
    section(41, "HTML Title", "🏷️")
    r = req(url)
    if not r: return
    m = re.search(r"<title>(.*?)</title>", r.text, re.I|re.S)
    if m: console.print(f"[yellow]Title:[/yellow] {m.group(1).strip()[:100]}")


def f042(url, R):
    section(42, "Meta Tags", "🔖")
    r = req(url)
    if not r: return
    soup = BeautifulSoup(r.text, "html.parser")
    for m in soup.find_all("meta")[:10]:
        n = m.get("name") or m.get("property") or "?"
        v = m.get("content","")[:60]
        console.print(f"[cyan]{n}:[/cyan] {v}")


def f043(url, R):
    section(43, "Favicon Check", "⭐")
    for p in ["/favicon.ico","/favicon.png"]:
        r = req(normalize_url(url) + p, timeout=4)
        if r and r.status_code == 200:
            console.print(f"[green]✓[/green] {p}")


def f044(url, R):
    section(44, "Social Links", "🔗")
    r = req(url)
    if not r: return
    for net in ["facebook","twitter","instagram","linkedin","youtube","github"]:
        if net in r.text.lower():
            console.print(f"[cyan]→[/cyan] {net}")


def f045(url, R):
    section(45, "Analytics Detect", "📊")
    r = req(url)
    if not r: return
    for a in ["google-analytics","gtag","facebook.net","hotjar","mixpanel"]:
        if a in r.text.lower(): console.print(f"[cyan]✓[/cyan] {a}")


def f046(url, R):
    section(46, "Fonts Used", "🔤")
    r = req(url)
    if not r: return
    fonts = set(re.findall(r"font-family:\s*([^;]+)", r.text, re.I))
    for f in list(fonts)[:5]: console.print(f"[cyan]→[/cyan] {f.strip()[:60]}")


def f047(url, R):
    section(47, "Image Count", "🖼️")
    r = req(url)
    if not r: return
    imgs = BeautifulSoup(r.text, "html.parser").find_all("img")
    console.print(f"[yellow]Total images:[/yellow] {len(imgs)}")


def f048(url, R):
    section(48, "Video/Audio", "🎬")
    r = req(url)
    if not r: return
    soup = BeautifulSoup(r.text, "html.parser")
    v = len(soup.find_all("video")) + len(soup.find_all("audio"))
    console.print(f"[yellow]Media elements:[/yellow] {v}")


def f049(url, R):
    section(49, "CSS Files", "🎨")
    r = req(url)
    if not r: return
    css = BeautifulSoup(r.text, "html.parser").find_all("link", rel="stylesheet")
    for c in css[:10]: console.print(f"[cyan]→[/cyan] {c.get('href','')[:90]}")


def f050(url, R):
    section(50, "Inline Scripts", "📜")
    r = req(url)
    if not r: return
    scripts = BeautifulSoup(r.text, "html.parser").find_all("script", src=False)
    console.print(f"[yellow]Inline scripts:[/yellow] {len(scripts)}")


# ── 51-60: Vulnerability Checks ──
def f051(url, R):
    section(51, "HTTP→HTTPS Redirect", "🔐")
    if url.startswith("http://"):
        https = "https://" + url[7:]
        r = req(https, timeout=5)
        if r: console.print("[green]✓ HTTPS tersedia[/green]")
        else: console.print("[red]⚠ Tidak ada HTTPS[/red]")


def f052(url, R):
    section(52, "Directory Traversal", "🚪")
    payloads = ["/../../../etc/passwd","/%2e%2e/%2e%2e/etc/passwd",
                "/..%2f..%2fetc%2fpasswd"]
    for p in payloads:
        r = req(normalize_url(url) + p, timeout=4)
        if r and "root:" in r.text:
            console.print(f"[red]⚠ Traversal:[/red] {p}")


def f053(url, R):
    section(53, "LFI Check", "📂")
    p = urlparse(url)
    if not p.query: return
    for prm in parse_qs(p.query):
        test = f"{p.scheme}://{p.netloc}{p.path}?{prm}=/etc/passwd"
        r = req(test, timeout=4)
        if r and "root:" in r.text:
            console.print(f"[red]⚠ LFI:[/red] {prm}")


def f054(url, R):
    section(54, "Host Header Injection", "🎩")
    r = req(url, headers={**HEADERS, "Host": "evil.example.com"})
    if r and "evil.example.com" in r.text:
        console.print("[red]⚠ Host Header Injection[/red]")


def f055(url, R):
    section(55, "CRLF Injection", "↩️")
    payload = "%0d%0aSet-Cookie:evil=1"
    r = req(normalize_url(url) + "/" + payload, timeout=4)
    if r and "evil=1" in str(r.headers):
        console.print("[red]⚠ CRLF Injection[/red]")


def f056(url, R):
    section(56, "SSRF Check", "🌐")
    p = urlparse(url)
    if not p.query: return
    for prm in parse_qs(p.query):
        test = f"{p.scheme}://{p.netloc}{p.path}?{prm}=http://127.0.0.1"
        r = req(test, timeout=4)
        if r and ("localhost" in r.text.lower() or "127.0.0.1" in r.text):
            console.print(f"[yellow]⚠ Possible SSRF:[/red] {prm}")


def f057(url, R):
    section(57, "XXE Check", "📦")
    r = req(url)
    if r and ("xml" in r.headers.get("Content-Type","") or "xml" in r.text.lower()[:200]):
        console.print("[yellow]⚠ XML detected - potential XXE[/yellow]")


def f058(url, R):
    section(58, "Weak TLS Cipher", "🔓")
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((get_host(url), 443), timeout=5) as s:
            with ctx.wrap_socket(s) as ss:
                c = ss.cipher()
                if c and any(w in c[0] for w in ["RC4","DES","MD5","NULL"]):
                    console.print(f"[red]⚠ Weak:[/red] {c[0]}")
                else:
                    console.print(f"[green]✓ Strong:[/green] {c[0]}")
    except Exception: pass


def f059(url, R):
    section(59, "HTTP Strict Transport", "🔒")
    r = req(url)
    if r:
        hsts = r.headers.get("Strict-Transport-Security","")
        if hsts: console.print(f"[green]✓ HSTS:[/green] {hsts}")
        else: console.print("[red]✗ HSTS tidak ada[/red]")


def f060(url, R):
    section(60, "Content Security Policy", "🛡️")
    r = req(url)
    if r:
        csp = r.headers.get("Content-Security-Policy","")
        if csp:
            console.print(f"[green]✓ CSP ditemukan[/green] ({len(csp)} chars)")
        else: console.print("[red]✗ CSP tidak ada[/red]")


# ── 61-70: Fingerprint & Info ──
def f061(url, R):
    section(61, "PHP Version", "🐘")
    r = req(url)
    if r:
        m = re.search(r"PHP/([\d\.]+)", str(r.headers))
        if m: console.print(f"[yellow]PHP:[/yellow] {m.group(1)}")


def f062(url, R):
    section(62, "Apache Version", "🪶")
    r = req(url)
    if r:
        m = re.search(r"Apache/([\d\.]+)", str(r.headers))
        if m: console.print(f"[yellow]Apache:[/yellow] {m.group(1)}")


def f063(url, R):
    section(63, "Nginx Version", "🌿")
    r = req(url)
    if r:
        m = re.search(r"nginx/([\d\.]+)", str(r.headers), re.I)
        if m: console.print(f"[yellow]Nginx:[/yellow] {m.group(1)}")


def f064(url, R):
    section(64, "Generator Meta", "🏷️")
    r = req(url)
    if r:
        m = re.search(r'<meta[^>]+name=["\']generator["\'][^>]+content=["\']([^"\']+)', r.text, re.I)
        if m: console.print(f"[yellow]Generator:[/yellow] {m.group(1)}")


def f065(url, R):
    section(65, "Charset", "🔤")
    r = req(url)
    if r:
        m = re.search(r"charset=([\w-]+)", str(r.headers.get("Content-Type","")), re.I)
        if m: console.print(f"[yellow]Charset:[/yellow] {m.group(1)}")


def f066(url, R):
    section(66, "Language Detection", "🌐")
    r = req(url)
    if r:
        m = re.search(r'<html[^>]+lang=["\']([^"\']+)', r.text, re.I)
        if m: console.print(f"[yellow]Lang:[/yellow] {m.group(1)}")


def f067(url, R):
    section(67, "Viewport Check", "📱")
    r = req(url)
    if r and "viewport" in r.text.lower():
        console.print("[green]✓ Mobile-friendly meta[/green]")
    else:
        console.print("[yellow]⚠ Tidak ada viewport[/yellow]")


def f068(url, R):
    section(68, "PWA Manifest", "📲")
    r = req(url + "/manifest.json", timeout=4)
    if r and r.status_code == 200:
        console.print("[green]✓ manifest.json ditemukan[/green]")
    else: console.print("[yellow]⚠ Tidak ada[/yellow]")


def f069(url, R):
    section(69, "Service Worker", "⚙️")
    r = req(url)
    if r and "serviceworker" in r.text.lower().replace(" ",""):
        console.print("[green]✓ Service Worker terdeteksi[/green]")
    else: console.print("[yellow]⚠ Tidak ada[/yellow]")


def f070(url, R):
    section(70, "AMP Support", "⚡")
    r = req(url)
    if r and "amphtml" in r.text.lower():
        console.print("[green]✓ AMP tersedia[/green]")
    else: console.print("[yellow]⚠ Tidak ada AMP[/yellow]")


# ── 71-80: Extra Recon ──
def f071(url, R):
    section(71, "Subdomain Brute", "🔎")
    subs = ["www","mail","api","dev","test","admin","blog","shop","cdn",
            "static","secure","vpn","login","app","m","mobile","ftp","smtp"]
    host = get_host(url).replace("www.","")
    found = []
    def _c(s):
        try:
            socket.gethostbyname(f"{s}.{host}"); return s
        except Exception: return None
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as ex:
        for f in concurrent.futures.as_completed([ex.submit(_c, s) for s in subs]):
            r = f.result()
            if r: found.append(r); console.print(f"[green]✓[/green] {r}.{host}")
    R["subdomains"] = found


def f072(url, R):
    section(72, "DNS Zone Transfer", "📤")
    try:
        import dns.query, dns.zone
        for ns in dns.resolver.resolve(get_host(url), "NS", lifetime=4):
            try:
                dns.zone.from_xfr(dns.query.xfr(str(ns), get_host(url), timeout=4))
                console.print(f"[red]⚠ Zone transfer dari {ns}[/red]")
            except Exception: pass
    except Exception: pass


def f073(url, R):
    section(73, "CAA Record", "🔐")
    try:
        for r in dns.resolver.resolve(get_host(url), "CAA", lifetime=4):
            console.print(f"[cyan]→[/cyan] {r}")
    except Exception: console.print("[yellow]⚠ Tidak ada CAA[/yellow]")


def f074(url, R):
    section(74, "SPF Record", "📧")
    try:
        for r in dns.resolver.resolve(get_host(url), "TXT", lifetime=4):
            if "spf" in str(r).lower():
                console.print(f"[cyan]→[/cyan] {str(r)[:200]}")
    except Exception: console.print("[yellow]⚠ Tidak ada SPF[/yellow]")


def f075(url, R):
    section(75, "DMARC Record", "🛡️")
    try:
        for r in dns.resolver.resolve(f"_dmarc.{get_host(url)}", "TXT", lifetime=4):
            console.print(f"[cyan]→[/cyan] {str(r)[:200]}")
    except Exception: console.print("[yellow]⚠ Tidak ada DMARC[/yellow]")


def f076(url, R):
    section(76, "DKIM Check", "🔑")
    console.print("[yellow]⚠ DKIM butuh selector spesifik[/yellow]")


def f077(url, R):
    section(77, "MX Records", "📮")
    try:
        for r in dns.resolver.resolve(get_host(url), "MX", lifetime=4):
            console.print(f"[cyan]→[/cyan] {r.preference} {r.exchange}")
    except Exception: pass


def f078(url, R):
    section(78, "NS Records", "🌐")
    try:
        for r in dns.resolver.resolve(get_host(url), "NS", lifetime=4):
            console.print(f"[cyan]→[/cyan] {r}")
    except Exception: pass


def f079(url, R):
    section(79, "TXT Records", "📝")
    try:
        for r in dns.resolver.resolve(get_host(url), "TXT", lifetime=4):
            console.print(f"[cyan]→[/cyan] {str(r)[:150]}")
    except Exception: pass


def f080(url, R):
    section(80, "ASN Lookup", "🆔")
    try:
        ip = socket.gethostbyname(get_host(url))
        r = requests.get(f"https://api.hackertarget.com/aslookup/?q={ip}", timeout=10)
        console.print(r.text[:300])
    except Exception: pass


# ── 81-90: Advanced ──
def f081(url, R):
    section(81, "HTTP Parameter Pollution", "🌀")
    p = urlparse(url)
    if not p.query: return
    for prm in parse_qs(p.query):
        test = f"{p.scheme}://{p.netloc}{p.path}?{prm}=A&{prm}=B"
        r = req(test, timeout=4)
        if r and r.status_code == 200:
            console.print(f"[yellow]⚠ Parameter '{prm}' duplikat OK[/yellow]")


def f082(url, R):
    section(82, "Cookie Flags", "🍪")
    r = req(url)
    if r and r.cookies:
        for c in r.cookies:
            flags = []
            if c.secure: flags.append("Secure")
            if c.has_nonstandard_attr("HttpOnly"): flags.append("HttpOnly")
            console.print(f"[cyan]{c.name}:[/cyan] {', '.join(flags) or 'NO FLAGS'}")


def f083(url, R):
    section(83, "Session Fixation", "🎫")
    r = req(url)
    if r and "session" in str(r.cookies).lower():
        console.print("[yellow]⚠ Session cookie detected - check fixation[/yellow]")
    else: console.print("[green]✓ Tidak ada session di cookie[/green]")


def f084(url, R):
    section(84, "Sensitive Data in HTML", "🔍")
    r = req(url)
    if not r: return
    patterns = {
        "API Key": r"api[_-]?key[\"'\s:=]+([a-zA-Z0-9]{20,})",
        "Password": r"password[\"'\s:=]+([^\"'\s<>]{8,})",
        "AWS Key": r"AKIA[0-9A-Z]{16}",
        "Private Key": r"-----BEGIN [A-Z ]+PRIVATE KEY-----",
        "Google API": r"AIza[0-9A-Za-z_-]{35}",
    }
    for name, pat in patterns.items():
        m = re.findall(pat, r.text, re.I)
        if m: console.print(f"[red]⚠ {name}:[/red] {str(m[0])[:50]}")


def f085(url, R):
    section(85, "Comments in Source", "💬")
    r = req(url)
    if not r: return
    comments = re.findall(r"<!--(.*?)-->", r.text, re.S)
    for c in comments[:5]:
        if len(c.strip()) > 10:
            console.print(f"[dim]→[/dim] {c.strip()[:80]}")


def f086(url, R):
    section(86, "TODO/FIXME Check", "📌")
    r = req(url)
    if r:
        todos = re.findall(r"(TODO|FIXME|XXX|HACK):\s*([^\n<]{5,})", r.text, re.I)
        for t in todos[:10]: console.print(f"[yellow]→[/yellow] {t[0]}: {t[1][:80]}")


def f087(url, R):
    section(87, "Debug Info Leak", "🐛")
    for p in ["/debug","/test.php","/phpinfo.php","/info.php","/server-status"]:
        r = req(normalize_url(url) + p, timeout=4)
        if r and r.status_code == 200:
            if any(x in r.text.lower() for x in ["phpinfo","server status","debug"]):
                console.print(f"[red]⚠ Debug info:[/red] {p}")


def f088(url, R):
    section(88, "Stack Trace Check", "📉")
    r = req(url + "/nonexistent_" + "".join(random.choices(string.ascii_lowercase, k=8)))
    if r and any(x in r.text.lower() for x in ["stack trace","traceback","at line","syntax error"]):
        console.print("[red]⚠ Stack trace ter-expose[/red]")
    else: console.print("[green]✓ Tidak ada[/green]")


def f089(url, R):
    section(89, "Error Page Info", "❌")
    r = req(url + "/nonexistent_page_" + str(random.randint(1000,9999)))
    if r:
        console.print(f"[yellow]Status:[/yellow] {r.status_code}")
        if "server" in str(r.headers).lower():
            console.print(f"[cyan]Server:[/cyan] {r.headers.get('Server')}")


def f090(url, R):
    section(90, "Robots Sitemap Cross", "🔀")
    r = req(url + "/robots.txt")
    if r and "sitemap" in r.text.lower():
        for line in r.text.splitlines():
            if "sitemap" in line.lower():
                console.print(f"[cyan]→[/cyan] {line}")


# ── 91-100: Final Summary ──
def f091(url, R):
    section(91, "Response Time", "⏱️")
    t0 = time.time()
    req(url)
    elapsed = (time.time() - t0) * 1000
    console.print(f"[yellow]Response:[/yellow] {elapsed:.0f}ms")
    R["response_ms"] = elapsed


def f092(url, R):
    section(92, "Payload Size", "📦")
    r = req(url)
    if r:
        size = len(r.content)
        console.print(f"[yellow]Size:[/yellow] {size/1024:.2f} KB")
        R["size_kb"] = size/1024


def f093(url, R):
    section(93, "HTTP/1.0 Test", "🕰️")
    try:
        s = socket.socket(); s.settimeout(5)
        host = get_host(url)
        s.connect((host, 80))
        s.send(b"GET / HTTP/1.0\r\nHost: " + host.encode() + b"\r\n\r\n")
        resp = s.recv(200).decode(errors="ignore")
        s.close()
        if "HTTP/1.0" in resp or "HTTP/1.1" in resp:
            console.print(f"[green]✓ Support HTTP/1.0[/green]")
    except Exception: pass


def f094(url, R):
    section(94, "HTTP/2 Prior Knowledge", "⚡")
    console.print("[yellow]⚠ HTTP/2 detection via headers[/yellow]")


def f095(url, R):
    section(95, "CNAME Chain", "🔗")
    try:
        for r in dns.resolver.resolve(get_host(url), "CNAME", lifetime=4):
            console.print(f"[cyan]→[/cyan] {r}")
    except Exception: console.print("[yellow]⚠ Tidak ada CNAME[/yellow]")


def f096(url, R):
    section(96, "PTR Lookup", "🔄")
    try:
        ip = socket.gethostbyname(get_host(url))
        parts = ip.split(".")
        ptr = ".".join(reversed(parts)) + ".in-addr.arpa"
        for r in dns.resolver.resolve(ptr, "PTR", lifetime=4):
            console.print(f"[cyan]→[/cyan] {r}")
    except Exception: console.print("[yellow]⚠ Tidak ada PTR[/yellow]")


def f097(url, R):
    section(97, "Cert SAN Domains", "🏷️")
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((get_host(url), 443), timeout=5) as s:
            with ctx.wrap_socket(s, server_hostname=get_host(url)) as ss:
                cert = ss.getpeercert()
                sans = cert.get("subjectAltName", [])
                for t, v in sans[:10]:
                    console.print(f"[cyan]→[/cyan] {v}")
    except Exception: pass


def f098(url, R):
    section(98, "Cert Expiry Check", "📅")
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((get_host(url), 443), timeout=5) as s:
            with ctx.wrap_socket(s, server_hostname=get_host(url)) as ss:
                cert = ss.getpeercert()
                exp = cert.get("notAfter","")
                console.print(f"[yellow]Expires:[/yellow] {exp}")
    except Exception: pass


def f099(url, R):
    section(99, "Gzip Compression", "🗜️")
    r = req(url, headers={**HEADERS, "Accept-Encoding": "gzip"})
    if r:
        enc = r.headers.get("Content-Encoding","")
        if "gzip" in enc.lower():
            console.print("[green]✓ Gzip aktif[/green]")
        else: console.print("[yellow]⚠ Gzip tidak aktif[/yellow]")


def f100(url, R):
    section(100, "VULNERABILITY SUMMARY", "📊")
    issues = []
    if R.get("missing_sec_headers"):
        issues.append(("MEDIUM", f"Missing headers: {', '.join(R['missing_sec_headers'][:3])}"))
    if R.get("xss_vulns"):
        issues.append(("HIGH", f"XSS params: {', '.join(R['xss_vulns'])}"))
    if R.get("sqli_vulns"):
        issues.append(("CRITICAL", f"SQLi params: {', '.join(R['sqli_vulns'])}"))
    if R.get("waf"):
        issues.append(("INFO", f"WAF: {', '.join(R['waf'])}"))
    for p in R.get("ports", []):
        if p in (21,23,3306,5432,6379,27017,9200,11211):
            issues.append(("HIGH", f"Exposed service port {p}"))
    if not issues:
        console.print("[bold green]✓ Tidak ada isu kritis[/bold green]")
    else:
        t = Table(title="Security Findings", border_style="red")
        t.add_column("Severity", style="bold red")
        t.add_column("Description", style="white")
        colors = {"CRITICAL":"bold red","HIGH":"red","MEDIUM":"yellow","INFO":"cyan"}
        for s, d in issues:
            t.add_row(f"[{colors[s]}]{s}[/{colors[s]}]", d)
        console.print(t)
    R["issues"] = issues


# ═══════════════════════════════════════════════
# DAFTAR 100 FITUR
# ═══════════════════════════════════════════════
FEATURES = [
    ("HTTP Headers", f001), ("Status Code", f002), ("SSL/TLS", f003),
    ("Port Scanner", f004), ("DNS Enum", f005), ("WHOIS", f006),
    ("Robots.txt", f007), ("Sitemap", f008), ("Security Headers", f009),
    ("Cookie Audit", f010), ("HTTP Methods", f011), ("Server Info", f012),
    ("Redirect Chain", f013), ("Tech Fingerprint", f014), ("CMS Detector", f015),
    ("XSS Scanner", f016), ("SQLi Scanner", f017), ("Open Redirect", f018),
    ("CORS Check", f019), ("Clickjacking", f020), ("Email Extractor", f021),
    ("Form Finder", f022), ("JS Analyzer", f023), ("Link Crawler", f024),
    ("WAF Detector", f025), ("Favicon Hash", f026), ("IP Info", f027),
    ("Reverse DNS", f028), ("Traceroute", f029), ("Ping Test", f030),
    ("Path Discovery", f031), ("Sensitive Files", f032), ("Admin Panels", f033),
    ("Backup Files", f034), ("Config Files", f035), ("Directory Listing", f036),
    ("HTTP/2 Support", f037), ("Compression", f038), ("Cache Headers", f039),
    ("Content-Type", f040), ("HTML Title", f041), ("Meta Tags", f042),
    ("Favicon Check", f043), ("Social Links", f044), ("Analytics Detect", f045),
    ("Fonts Used", f046), ("Image Count", f047), ("Video/Audio", f048),
    ("CSS Files", f049), ("Inline Scripts", f050), ("HTTP→HTTPS", f051),
    ("Dir Traversal", f052), ("LFI Check", f053), ("Host Header", f054),
    ("CRLF Injection", f055), ("SSRF Check", f056), ("XXE Check", f057),
    ("Weak TLS", f058), ("HSTS Check", f059), ("CSP Check", f060),
    ("PHP Version", f061), ("Apache Version", f062), ("Nginx Version", f063),
    ("Generator Meta", f064), ("Charset", f065), ("Language", f066),
    ("Viewport", f067), ("PWA Manifest", f068), ("Service Worker", f069),
    ("AMP Support", f070), ("Subdomain Brute", f071), ("Zone Transfer", f072),
    ("CAA Record", f073), ("SPF Record", f074), ("DMARC Record", f075),
    ("DKIM Check", f076), ("MX Records", f077), ("NS Records", f078),
    ("TXT Records", f079), ("ASN Lookup", f080), ("HTTP Param Poll", f081),
    ("Cookie Flags", f082), ("Session Fixation", f083), ("Data in HTML", f084),
    ("Comments", f085), ("TODO/FIXME", f086), ("Debug Info", f087),
    ("Stack Trace", f088), ("Error Page", f089), ("Robots Sitemap", f090),
    ("Response Time", f091), ("Payload Size", f092), ("HTTP/1.0", f093),
    ("HTTP/2 Prior", f094), ("CNAME Chain", f095), ("PTR Lookup", f096),
    ("Cert SAN", f097), ("Cert Expiry", f098), ("Gzip Check", f099),
    ("SUMMARY", f100),
]


# ═══════════════════════════════════════════════
# AUTO SCAN ENGINE
# ═══════════════════════════════════════════════
def auto_scan(target):
    url = normalize_url(target)
    R = {}

    console.clear()
    console.print(BANNER)
    console.print(Panel(
        f"[bold yellow]🎯 TARGET:[/bold yellow] [cyan]{url}[/cyan]\n"
        f"[bold yellow]🕐 START :[/bold yellow] [white]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/white]\n"
        f"[bold yellow]⚡ MODE  :[/bold yellow] [green]AUTO SCAN (100 Fitur)[/green]",
        border_style="bold magenta", box=box.DOUBLE_EDGE
    ))

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"=== WEBSCAN PRO v{VERSION} ===\n")
        f.write(f"Developer: {DEVELOPER}\nTarget   : {url}\n")
        f.write(f"Time     : {datetime.now()}\n\n")

    start = time.time()

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(bar_width=None),
        TextColumn("[green]{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        master = progress.add_task("Total Progress", total=len(FEATURES))
        for i, (name, fn) in enumerate(FEATURES, 1):
            progress.update(master, description=f"[{i}/100] {name}")
            try:
                fn(url, R)
                log(f"✓ {name} - OK", "ok")
            except KeyboardInterrupt:
                console.print("\n[red]⚠ Dibatalkan[/red]")
                break
            except Exception as e:
                log(f"✗ {name}: {e}", "error")
            progress.advance(master)

    duration = time.time() - start
    report_file = f"report_{get_host(url)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(R, f, indent=2, default=str)
    except Exception:
        report_file = "N/A"

    console.print()
    console.print(Rule("[bold green]✓ SCAN SELESAI[/bold green]", style="green"))
    console.print(Panel(
        f"[bold]Target   :[/bold] [cyan]{url}[/cyan]\n"
        f"[bold]Durasi   :[/bold] [yellow]{duration:.2f} detik[/yellow]\n"
        f"[bold]Fitur    :[/bold] [green]100/100 selesai[/green]\n"
        f"[bold]Log      :[/bold] [white]{LOG_FILE}[/white]\n"
        f"[bold]JSON     :[/bold] [white]{report_file}[/white]\n"
        f"[bold]Developer:[/bold] [bold yellow]{DEVELOPER}[/bold yellow]",
        title="[bold green]📋 LAPORAN AKHIR[/bold green]",
        border_style="green", box=box.DOUBLE_EDGE
    ))


# ═══════════════════════════════════════════════
# MENU INTERAKTIF
# ═══════════════════════════════════════════════
def interactive_menu():
    console.clear()
    console.print(BANNER)
    console.print(Panel(
        "[bold cyan]Selamat datang di WebScan Pro ULTIMATE[/bold cyan]\n\n"
        "[yellow]• 100 Fitur Pentest otomatis[/yellow]\n"
        "[yellow]• Cukup masukkan target URL/domain[/yellow]\n\n"
        "[dim]Contoh: example.com atau https://example.com[/dim]",
        title="[bold magenta]⚡ AUTO SCAN MODE ⚡[/bold magenta]",
        border_style="magenta", box=box.DOUBLE_EDGE
    ))

    target = Prompt.ask("\n[bold yellow]🎯 Masukkan target[/bold yellow]")
    if not target.strip():
        console.print("[red]✗ Target kosong![/red]")
        return
    auto_scan(target.strip())


# ═══════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(
        description=f"WebScan Pro v{VERSION} - Developer: {DEVELOPER}")
    parser.add_argument("-t", "--target", help="Target URL/domain")
    args = parser.parse_args()

    try:
        if args.target:
            auto_scan(args.target)
        else:
            interactive_menu()
    except KeyboardInterrupt:
        console.print("\n[red]⚠ Dibatalkan[/red]")
        sys.exit(0)


if __name__ == "__main__":
    main()