# 📊 Salary Bot

This bot helps you manage employee work shifts with ease.
It can generate detailed salary reports on request, giving you clear insights into payroll.
You can also record and track payments directly through the bot for accurate financial records.

---

## ⚙️ Technical stack

- 🤖 Aiogram 3 for async Telegram bot
- 🗄️ Async SQLAlchemy (2.0 style)
- 🔧 Configuration via Pydantic
- 🧪 Modular, extensible architecture (basic DDD)

---

## ⚒️ Quick start

1. **Clone the repository:**
    
    ```bash
    git clone https://github.com/SaidKamol0612/Salary-Bot.git
    ```

2. **Create and activate `venv`:**

    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables to `env` file:**

    ```txt
    # Bot token
    BOT__BOT__TOKEN="your_token"

    # Database url
    BOT__DB__URL="sqlite+aiosqlite:///db.sqlite3"

    # Admins Telegram IDs
    BOT__ADMIN__ADMIN_IDS=[]
    ```

5. **Run the server:**

   ```bash
   # .\venv\Scripts\activate
   .\run.bat # for Windows

   # or
   cd src
   python run.py
   ```



## 🔓 License and Contribution

This project is open and free to extend, suitable for both beginners and experienced developers who want to quickly set up a Telegram bot and focus on building its functionality. You may use it in commercial or personal projects with minimal restrictions — attribution is appreciated but not required.

> 💡 Contributions and forks are welcome!