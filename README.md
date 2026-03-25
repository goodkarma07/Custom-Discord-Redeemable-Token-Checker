<div align="center">

# 💳 token checker 💳

> *check tokens. find cards. know your nitro.*

[![Telegram](https://img.shields.io/badge/channel-t.me%2Fcheaprip-blue?style=for-the-badge&logo=telegram&logoColor=white&color=7289da)](https://t.me/cheaprip)
[![Author](https://img.shields.io/badge/author-%40badykarma-pink?style=for-the-badge&logo=telegram&logoColor=white&color=ff69b4)](https://t.me/badykarma)
[![Language](https://img.shields.io/badge/python-3.10%2B-purple?style=for-the-badge&logo=python&logoColor=white&color=9b59b6)](https://python.org)
[![License](https://img.shields.io/badge/license-custom%20%40badykarma-red?style=for-the-badge&color=e74c3c)](LICENSE)

---

*multi-threaded discord token checker — nitro status, payment sources & card validity*

</div>

---

## ✨ features

```
  💳  detects valid & invalid payment cards with brand + last 4 digits
  💎  nitro status — active / had nitro / never had
  📅  card age detection — shows how old each payment method is
  🚀  boost tracking — shows available boosts on active nitro accounts
  🔄  multi-threaded — ThreadPoolExecutor for zero CPU spinning
  🌐  proxy support — round-robin proxy rotation per request
  🎭  tls_client fingerprinting — bypasses discord bot detection
  📁  auto-sorted output — results split into dedicated files
  🖥️  beautiful live stats — gradient header updates every 30 checks
  ⚡  two modes — nitro-only (fast) or full check (cards + nitro)
```

---

## 🔧 recent updates

```diff
+ switched to tls_client — chrome TLS fingerprinting, bypasses bot detection
+ ThreadPoolExecutor — no more CPU spinning, efficient parallel processing
+ two checking modes — nitro-only for speed, full for complete analysis
+ boost detection — shows available boosts on active nitro accounts
+ beautiful logging — gradient lines, timestamps, thread names, runtime
+ round-robin proxies — better distribution than random selection
+ exponential backoff — smarter retries on rate limits
+ locked token detection — identifies 403 locked accounts separately
```

---

## 📦 installation

```bash
pip install tls_client colorama
```

---

## 📁 file structure

```
📂 token-checker/
 ├── 🐍 main.py             ← main script
 ├── 🪙 tokens.txt          ← tokens to check (one per line)
 ├── 🌐 proxies.txt         ← proxies (one per line, optional)
 │
 └── 📂 output/             ← auto-generated results folder
      ├── 💳 valid_cards.txt         ← tokens with valid payment methods
      ├── ⛔ invalid_cards.txt       ← tokens with expired/invalid cards
      ├── 🚫 no_payment.txt          ← tokens with no payment on file
      ├── 💎 nitro_active.txt        ← tokens with active nitro + boost count
      ├── 🕒 nitro_had.txt           ← tokens that had nitro before
      ├── ❌ nitro_never.txt         ← never had nitro
      ├── 🔑 invalid.txt             ← dead / banned tokens
      ├── 🔒 locked.txt              ← locked tokens (403)
      └── ⚠️  errors.txt              ← connection/proxy failures
```

---

## 🪙 token formats

all formats supported in `tokens.txt`:

```
TOKEN
email@example.com:password:TOKEN
email@example.com:TOKEN
```

emails are automatically masked in logs for privacy.

---

## 🌐 proxy format

```
host:port
host:port:user:pass
user:pass@host:port
http://user:pass@host:port
```

one proxy per line in `proxies.txt`. if the file is missing or empty, requests go direct.

---

## 🚀 usage

```bash
python main.py
```

you'll be asked at startup:

| prompt | description |
|--------|-------------|
| `Mode` | 1 = Nitro Only (fast), 2 = Full Check (cards + nitro) |
| `Threads` | how many tokens to check at the same time (1-500) |

higher threads = faster but more likely to hit rate limits. `50–100` is a safe range.

---

## 🎯 checking modes

### ⚡ mode 1: nitro only
fast check — only checks if token ever had nitro subscription.

```
outputs: nitro_active.txt, nitro_had.txt, nitro_never.txt
```

### 💳 mode 2: full check
complete check — nitro status + all payment methods + card details.

```
outputs: all nitro files + valid_cards.txt, invalid_cards.txt, no_payment.txt
```

---

## 📊 what gets checked

### 💳 payment sources (full mode)

| field | description |
|-------|-------------|
| `brand` | Visa, Mastercard, Amex, etc. |
| `last 4` | last 4 digits of the card |
| `validity` | whether discord considers it valid |
| `expiry` | expiry month / year if available |
| `age` | how long the card has been on the account |

### 💎 nitro status

| status | meaning |
|--------|---------|
| `Active` | currently has nitro — shows type + days remaining + boost count |
| `Had Nitro` | had nitro before — shows when it expired |
| `Never had` | never subscribed |

---

## 🖥️ live console output

### startup banner

```
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱

    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                                                                              ║
    ║   ████████╗ ██████╗ ██╗  ██╗███████╗███╗   ██╗     ██████╗██╗  ██╗██╗  ██╗   ║
    ║   ╚══██╔══╝██╔═══██╗██║ ██╔╝██╔════╝████╗  ██║    ██╔════╝██║  ██║██║ ██╔╝   ║
    ║      ██║   ██║   ██║█████╔╝ █████╗  ██╔██╗ ██║    ██║     ███████║█████╔╝    ║
    ║      ██║   ██║   ██║██╔═██╗ ██╔══╝  ██║╚██╗██║    ██║     ██╔══██║██╔═██╗    ║
    ║      ██║   ╚██████╔╝██║  ██╗███████╗██║ ╚████║    ╚██████╗██║  ██║██║  ██╗   ║
    ║      ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝     ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ║
    ║                                                                              ║
    ║                      ⚡ LIGHTNING FAST TOKEN CHECKER ⚡                       ║
    ╚══════════════════════════════════════════════════════════════════════════════╝

▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱
```

### live stats header (updates every 30 checks)

```
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱
                         ✨ TOKEN CHECKER LIVE STATUS ✨
──────────────────────────────────────────────────────────────────────────────────────
💳 VALID CARDS      │     23 ████████████████████
💎 NITRO ACTIVE     │      4 ████
⏳ HAD NITRO        │     11 ███████████
○ NEVER HAD        │     18
✗ INVALID          │     89
──────────────────────────────────────────────────────────────────────────────────────
📊 TOTAL CHECKED    │    142
🎯 VALID CARD RATE  │  16.2%
⚡ RUNTIME          │  45.3s
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱
```

### log entries

```
╭─ ⏰ 12:34:56.789 │ 💎 NITRO    │ 🧵 Worker-42   │ ⚡ 12.3s ╰─▶ 🏆 ACTIVE: Nitro (23 days) | Boosts: 2 | ab***@gmail.com
╭─ ⏰ 12:34:56.891 │ 💳 CARD     │ 🧵 Worker-17   │ ⚡ 12.4s ╰─▶ 💳 Valid: Visa ****4242 (2y 3mo old) Exp: 12/2027
╭─ ⏰ 12:34:57.012 │ 🔥 ERROR    │ 🧵 Worker-8    │ ⚡ 12.5s ╰─▶ ❌ Invalid token | tok456...
╭─ ⏰ 12:34:57.134 │ ⚠️ WARNING  │ 🧵 Worker-23   │ ⚡ 12.6s ╰─▶ 💸 No payment methods | tok789...
╭─ ⏰ 12:34:57.256 │ 💎 NITRO    │ 🧵 Worker-5    │ ⚡ 12.7s ╰─▶ ⏳ HAD NITRO: 3mo ago | ab***@outlook.com
```

---

## ⚠️ notes

- uses `tls_client` for chrome TLS fingerprinting — bypasses discord bot detection
- `ThreadPoolExecutor` threading — zero CPU spinning, efficient parallelism
- up to `3` retries per token with exponential backoff
- proxies rotate round-robin per request
- all output files are appended, not overwritten — safe to run multiple times
- `output/` folder is created automatically if it doesn't exist
- console title updates live with current stats (Windows)

---

<div align="center">

```
made with 🤍 by @badykarma
```

### 🔗 [t.me/cheaprip](https://t.me/cheaprip)
*join for more tools, tokens and more!*

</div>
