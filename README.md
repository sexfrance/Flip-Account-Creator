<div align="center">
  <h2 align="center">Flip Account Creator</h2>
  <p align="center">
   An automated tool for creating Flip accounts with email verification support, proxy handling, and multi-threading capabilities.
    <br />
    <br />
    <a href="https://discord.cyberious.xyz">💬 Discord</a>
    ·
    <a href="#-changelog">📜 ChangeLog</a>
    ·
    <a href="https://github.com/sexfrance/Flip-Account-Creator/issues">⚠️ Report Bug</a>
    ·
    <a href="https://github.com/sexfrance/Flip-Account-Creator/issues">💡 Request Feature</a>
  </p>
</div>

---

### ⚙️ Installation

- Requires: `Python 3.7+`
- Make a python virtual environment: `python3 -m venv venv`
- Source the environment: `venv\Scripts\activate` (Windows) / `source venv/bin/activate` (macOS, Linux)
- Install the requirements: `pip install -r requirements.txt`

---

### 🔥 Features

- Automated Flip account creation
- Email verification support using temporary email service
- Proxy support for avoiding rate limits
- Multi-threaded account generation
- Real-time creation tracking
- Configurable thread count
- Debug mode for troubleshooting
- Proxy/Proxyless mode support
- Automatic CSRF token handling
- Custom password support

---

### 📝 Usage

1. **Configuration**:
   Edit `input/config.toml`:

   ```toml
   [dev]
   Debug = false
   Proxyless = false
   Threads = 1

   [captcha]
   NextCaptcha_Key = "your_nextcaptcha_key"

   [data]
   useBio = true
   password = "your_custom_password"
   ```

2. **Proxy Setup** (Optional):

   - Add proxies to `input/proxies.txt` (one per line)
   - Format: `ip:port` or `user:pass@ip:port`

3. **Running the script**:

   ```bash
   python main.py
   ```

4. **Output**:
   - Created accounts are saved to `output/accounts.txt`
   - Format: `email:password`
   - Full capture accounts are saved to `output/accounts_full_capture.txt`
   - Format: `username:email:password:AccessToken:deviceFingerprint`

---

### 📹 Preview

[preview](https://i.imgur.com/EXlGYAB.gif)

---

### ❗ Disclaimers

- This project is for educational purposes only
- The author is not responsible for any misuse of this tool
- Use responsibly and in accordance with Flip's terms of service

---

### 📜 ChangeLog

```diff
v0.0.1 ⋮ 12/26/2024
! Initial release.
```

<p align="center">
  <img src="https://img.shields.io/github/license/sexfrance/Flip-Account-Creator.svg?style=for-the-badge&labelColor=black&color=f429ff&logo=IOTA"/>
  <img src="https://img.shields.io/github/stars/sexfrance/Flip-Account-Creator.svg?style=for-the-badge&labelColor=black&color=f429ff&logo=IOTA"/>
  <img src="https://img.shields.io/github/languages/top/sexfrance/Flip-Account-Creator.svg?style=for-the-badge&labelColor=black&color=f429ff&logo=python"/>
</p>
