# AgriSmartBot

This project is a simple Telegram bot for agricultural guidance.

## Getting Started

Follow these steps to run the project on your local machine or VM.

### 1. Clone the repository

```bash
git clone https://github.com/USERNAME/REPO_NAME.git
cd REPO_NAME
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

On Windows:

```bash
venv\Scripts\activate
```

On Linux/Mac:

```bash
source venv/bin/activate
```

### 4. Install required libraries

```bash
pip install -r requirements.txt
```

### 5. Run the bot

```bash
python AgriSmartBot.py
```

### 6. Updating the environment

If you add new libraries, update requirements.txt:

```bash
pip freeze > requirements.txt
```

#### Notes

- Do not push the venv folder to GitHub. It is already included in .gitignore.
- Make sure you have Python 3.8+ installed.
- This setup works for both local machines and VMs provided for this project.
