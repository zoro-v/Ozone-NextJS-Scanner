# Ozone Next.js Scanner ⚛️

![Ozone](https://img.shields.io/badge/Tool-Ozone-cyan?style=for-the-badge)

**Ozone Next.js Scanner** is a specialized reconnaissance tool designed to audit websites built with the **Next.js** framework.

It uses **Selenium** to render the page, extracts the unique `buildId`, and then constructs hidden JSON API endpoints (`/_next/data/...`) to reveal backend data that is not visible in the source code.
---
⚠️ Disclaimer
This tool is developed by Ozone for educational purposes and security research only.
---

## ⚡ Features

* **BuildId Extraction:** Automatically hunts for the Next.js build identifier.
* **Data Mining:** Reconstructs `_next/data` JSON URLs to find hidden content.
* **Route Discovery:** Parses internal routing maps from the initial HTML.
* **Ozone Quality:** Robust error handling and CLI support.

---

## 📦 Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/zoro-v/Ozone-NextJS-Scanner.git](https://github.com/zoro-v/Ozone-NextJS-Scanner.git)
    cd Ozone-NextJS-Scanner
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

> **Note for Linux/WSL Users:** You might need to install Chromium manually if Selenium fails to start:
> `sudo apt install chromium-browser`

---

## 🚀 Usage

### 1. Scan a Single Target
```bash
python3 nextjs_scanner.py -u [https://example.com](https://example.com)
