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
  💎  nitro status — active / expired recently / expired old / never had
  📅  card age detection — shows how old each payment method is
  🔄  multi-threaded — run hundreds of tokens in parallel
  🌐  proxy support — random proxy rotation per request
  🎭  fake user-agent rotation — looks more human
  📁  auto-sorted output — results split into dedicated files
  🖥️  live stats header — updates in real time as tokens are checked
```

---

## 📦 installation

```bash
pip install requests fake-useragent colorama
```

---

## 📁 file structure

```
📂 token-checker/
 ├── 🐍 checker.py          ← main script
 ├── 🪙 tokens.txt          ← tokens to check (one per line)
 ├── 🌐 proxies.txt         ← proxies (one per line, optional)
 │
 └── 📂 output/             ← auto-generated results folder
      ├── 💳 valid_cards.txt         ← tokens with valid payment methods
      ├── ⛔ invalid_cards.txt       ← tokens with expired/invalid cards
      ├── 🚫 no_payment.txt          ← tokens with no payment on file
      ├── 💎 has_nitro.txt           ← tokens with active nitro
      ├── 🕒 nitro_expired_recent.txt← nitro expired within ~18 months
      ├── 📦 had_nitro_old.txt       ← nitro expired long ago
      ├── ❌ never_had_nitro.txt     ← never had nitro
      ├── 🔑 invalid_tokens.txt      ← dead / banned tokens
      ├── ⚠️  http_errors.txt         ← unexpected status codes
      └── 💥 exceptions.txt          ← connection/proxy failures
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
user:pass@host:port
```

one proxy per line in `proxies.txt`. if the file is missing or empty, requests go direct.

---

## 🚀 usage

```bash
python main.py
```

you'll be asked for one thing at startup:

| prompt | description |
|--------|-------------|
| `Threads` | how many tokens to check at the same time |

higher threads = faster but more likely to hit rate limits. `50–100` is a safe range.

---

## 📊 what gets checked

### 💳 payment sources
checks each payment method on the account and reports:

```
brand       →  Visa, Mastercard, Amex, etc.
last 4      →  last 4 digits of the card
validity    →  whether discord considers it valid
expiry      →  expiry month / year if available
age         →  how long the card has been on the account
```

### 💎 nitro status

| status | meaning |
|--------|---------|
| `Active` | currently has nitro — shows type (Classic / Nitro / Basic) |
| `Expired recently` | had nitro, ended within ~18 months |
| `Had Nitro (old)` | had nitro but ended a long time ago |
| `Never had Nitro` | never subscribed |

---

## 🖥️ live console output

the header updates in real time showing:

```
[Checked: 142 ] [Valid: 23 ] [Invalid: 89 ] [💎 Active: 4 ] [Had: 11 ] [Never: 18 ]
```

each result is logged with a timestamp and color-coded badge:

```
[12:34:56] [✓ VALID  ] Visa ****4242 (2y 3mo old) Exp: 12/2027 | ab***@gmail.com | tok123...
[12:34:56] [💎 NITRO ] Active subscription | Nitro | ab***@gmail.com | tok123...
[12:34:56] [✗ ERROR  ] Invalid token | tok456...
[12:34:56] [⚠ WARN   ] No payment on file | tok789...
```

---

## ⚠️ notes

- up to `3` retries per token before marking as error
- proxies are picked randomly per request — not round-robin
- all output files are appended, not overwritten — safe to run multiple times
- `output/` folder is created automatically if it doesn't exist

---

<div align="center">

---

```
made with 🤍 by @badykarma
```

### 🔗 [t.me/cheaprip](https://t.me/cheaprip)
*join for more tools, tokens and more!*

---

</div>
