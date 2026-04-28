# 🧩 Browser Extension Backup & Restore (Fun Edition)

> **«افزونه‌هایت را مثل آب خوردن بکاپ بگیر و برگردان!»**  
> ابزاری جذاب، cross‑platform و کاملاً رایگان برای **بکاپ‌گیری** و **بازگردانی** افزونه‌های مرورگرهای محبوب: **Chrome**، **Firefox** و **Edge**.

![Python](https://img.shields.io/badge/Python-3.6+-blue.svg) ![Platform](https://img.shields.io/badge/Platform-Windows%20|%20macOS%20|%20Linux-lightgrey) ![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ ویژگی‌های شاخص

- 🖥️ **پشتیبانی از سه مرورگر اصلی** – Chrome (🌐)، Firefox (🦊) و Edge (🧭)
- 💻 **Cross‑Platform کامل** – روی ویندوز، macOS و لینوکس بدون هیچ تغییری اجرا می‌شود
- 🎨 **رابط کاربری رنگی و انیمیشنی** – منوی تعاملی با هدرهای ASCII، اسپینرهای زنده و پیام‌های رنگی
- 🛡️ **بکاپ مقاوم** – ابتدا با خود مرورگر بسته‌بندی می‌کند؛ در صورت خطا، فایل ZIP کامل تهیه می‌شود
- 🔄 **بازگردانی هوشمند** – برای Chrome/Edge به‌صورت Unpacked آماده‌ی بارگذاری دستی، برای Firefox مستقیماً به پروفایل کپی می‌شود
- 📦 **بدون وابستگی خارجی** – فقط پایتون استاندارد (هیچ pip نیازی نیست!)
- 📁 **ساختار قابل‌حمل** – کل پوشه‌ی ابزار را می‌توان با فلش یا شبکه به سیستم دیگر منتقل کرد

---

## 📋 پیش‌نیاز

- **Python 3.6 یا جدیدتر**  
  اگر پایتون را نصب ندارید، از [python.org](https://www.python.org/downloads/) دریافت کنید.  
  برای بررسی نسخه‌ی نصب‌شده:

```bash
  python --version
  # یا
  python3 --version
```

---
## 🚀 شروع سریع

### 1. دریافت ابزار

```bash
git clone https://github.com/your-username/browser-extension-backup.git
cd browser-extension-backup
```

یا فایل‌های `pack_browser_extensions.py` و `restore_browser_extensions.py` را به‌صورت دستی در یک پوشه قرار دهید.

### 2. بکاپ گرفتن از افزونه‌ها
**مهم:** پیش از شروع، مرورگر مربوطه را **کاملاً ببندید** (مخصوصاً برای Firefox).

```bash
python pack_browser_extensions.py
```

منوی جذاب زیر نمایش داده می‌شود:

```text
============================================================
🎒  BROWSER EXTENSION PACKER  🎒
Backup your extensions with a touch of fun!
============================================================

Select the browser to backup:
  [1] 🌐 Google Chrome
  [2] 🦊 Mozilla Firefox
  [3] 🧭 Microsoft Edge

👉 Enter number (1-3):
```

ا انتخاب مرورگر، عملیات بکاپ شروع می‌شود. پس از پایان، پوشه‌ای با نام `[browser]_extensions_backup` در کنار اسکریپت ایجاد می‌شود:

- `chrome_extensions_backup/`
    
- `firefox_extensions_backup/`
    
- `edge_extensions_backup/`

### 3. انتقال به سیستم مقصد

کل **پوشه‌ی اصلی** (شامل اسکریپت‌ها + پوشه‌ی بکاپ) را به رایانه‌ی دیگر کپی کنید.

### 4. بازگردانی افزونه‌ها

```bash
python restore_browser_extensions.py
```

دوباره مرورگر مقصد را انتخاب کنید:

```text
============================================================
🔄  BROWSER EXTENSION RESTORE  🔄
Bring back your beloved extensions!
============================================================

Select the browser to restore extensions for:
  [1] 🌐 Google Chrome
  [2] 🦊 Mozilla Firefox
  [3] 🧭 Microsoft Edge

👉 Enter number (1-3):
```

####  برای Chrome / Edge:

- یک پوشه‌ی `restored_extensions` ساخته می‌شود که داخل آن پوشه‌های جداگانه‌ی هر افزونه قرار دارد.
    
- مرورگر را باز کنید و به `chrome://extensions` (برای Edge: `edge://extensions`) بروید.
    
- **Developer mode** (حالت توسعه‌دهنده) را فعال کنید.
    
- روی **Load unpacked** کلیک کرده و پوشه‌ی افزونه‌ی مورد نظر را انتخاب کنید.
    

#### 🔸 برای Firefox:

- افزونه‌ها مستقیماً به پوشه‌ی پروفایل پیش‌فرض Firefox کپی می‌شوند.
    
- **حتماً Firefox بسته باشد** وگرنه خطا رخ می‌دهد!
    
- پس از اتمام، Firefox را باز کنید – افزونه‌ها به‌طور خودکار ظاهر می‌شوند.

---
## 📁 ساختار پوشه‌ها پس از اجرا

```text
CrxExtractor/
├── pack_browser_extensions.py       # اسکریپت بکاپ
├── restore_browser_extensions.py    # اسکریپت بازگردانی
├── chrome_extensions_backup/        # بکاپ Chrome (ساخته می‌شود)
│   ├── ahmpjcflkgiildlgicmcieglgoilbfdp.crx
│   └── ...
├── firefox_extensions_backup/       # بکاپ Firefox (ساخته می‌شود)
│   ├── uBlock0@raymondhill.net.xpi
│   └── ...
├── edge_extensions_backup/          # بکاپ Edge (ساخته می‌شود)
└── restored_extensions/             # پوشه‌ی بازگردانی (ساخته می‌شود)
    ├── ahmpjcflkgiildlgicmcieglgoilbfdp/
    └── ...
```

---
## ❓ سوال‌های رایج
<details> <summary><b>چرا بعضی افزونه‌های Chrome/Edge به‌جای فایل .crx، بکاپ .zip می‌گیرند؟</b></summary>

فرایند بسته‌بندی داخلی کروم (`--pack-extension`) ممکن است به دلایل امنیتی یا محدودیت‌های نسخه‌ی کروم شکست بخورد. اسکریپت در این حالت خودکار یک نسخه‌ی ZIP کامل از افزونه تهیه می‌کند که هنگام بازگردانی دقیقاً به همان شکل Load unpacked در مرورگر بارگذاری می‌شود.

</details><details> <summary><b>چرا افزونه‌ها بعد از بازگردانی Chrome/Edge شناسه (ID) جدیدی می‌گیرند؟</b></summary>

بکاپ بدون کلید خصوصی توسعه‌دهنده انجام می‌شود. در نتیجه هنگام بارگذاری مجدد، افزونه یک ID تصادفی جدید دریافت می‌کند. این روی کارکرد افزونه تأثیر نمی‌گذارد، اما داده‌های ذخیره‌شده‌ی محلی (مانند تنظیمات) که به ID قدیمی وابسته‌اند، منتقل نمی‌شوند.

</details><details> <summary><b>پیغام «No Firefox extensions found» می‌گیرم، ولی افزونه دارم!</b></summary>

- مطمئن شوید Firefox کاملاً بسته باشد.
    
- پروفایل پیش‌فرض را بررسی کنید: در نوار آدرس `about:profiles` را باز کنید و ببینید کدام پروفایل «Default Profile» است.
    
- اسکریپت از فایل `extensions.json` داخل پوشه‌ی پروفایل می‌خواند. اگر افزونه‌ی شما در آن لیست نیست (مثلاً افزونه‌ی موقتی از `about:debugging`)، آن را یک‌بار از فروشگاه افزونه نصب کنید تا در لیست ثبت شود.
    

</details><details> <summary><b>آیا می‌توانم مسیر بکاپ را تغییر دهم؟</b></summary>

به‌طور پیش‌فرض پوشه‌ی بکاپ کنار اسکریپت ساخته می‌شود. اگر می‌خواهید مسیر دلخواه تنظیم کنید، ثابت `BACKUP_DIR` را در تابع مربوطه تغییر دهید (خطوط ابتدایی توابع `pack_chromium` و `pack_firefox` و ...).  
در نسخه‌های بعدی ممکن است قابلیت انتخاب مسیر به منو اضافه شود.

</details><details> <summary><b>آیا با Brave یا سایر مرورگرهای مبتنی بر Chromium کار می‌کند؟</b></summary>

در حال حاضر سه مرورگر پشتیبانی می‌شوند، اما با کمی تغییر در مسیرها می‌توان آن را برای مرورگرهای Chromium‑based دیگر نیز استفاده کرد. لطفاً Issue ثبت کنید تا در نسخه‌های بعدی اضافه شود.

</details>

---
## 🛠️ رفع مشکلات احتمالی

|خطا|دلیل احتمالی|راه‌حل|
|---|---|---|
|`FileNotFoundError: Chrome executable not found`|مسیر نصب مرورگر استاندارد نیست|مسیر صحیح را در تابع `get_browser_exe` اضافه کنید یا مرورگر را از مسیر پیش‌فرض نصب کنید.|
|`Extensions folder not found`|پوشه‌ی پروفایل یافت نشد یا مرورگر نصب نیست|مرورگر را یک‌بار اجرا کرده تا پروفایل ساخته شود.|
|بازگردانی Firefox خطا می‌دهد|Firefox باز است|حتماً Firefox را کاملاً ببندید (حتی فرایندهای پس‌زمینه را در Task Manager بررسی کنید).|
|پس از بازگردانی Chrome/Edge افزونه کار نمی‌کند|پوشه ناقص استخراج شده|دوباره restore را اجرا کنید. یا پوشه را دستی زیپ/آنزیپ کنید.|

---

## 🤝 مشارکت

پیشنهادات، بهبودها و گزارش باگ‌ها را با آغوش باز می‌پذیریم!  
لطفاً از طریق [Issues](https://github.com/your-username/browser-extension-backup/issues) یا فرستادن Pull Request مشارکت کنید.

---

## 📄 مجوز

این پروژه تحت مجوز MIT منتشر شده است. جزئیات در فایل [LICENSE](https://license/).

<div align="center"> <br> <b>ساخته شده با ❤️ و پایتون</b><br> <sub>افزونه‌هایتان را امن نگه دارید!</sub> </div> ```
