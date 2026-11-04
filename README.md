# AgriSmartBot

AgriSmartBot is an Arabic-language Telegram bot for agricultural guidance. It
combines crop recommendations, weather data, investment estimates, and an
Azure OpenAI assistant in one conversational interface.

## Features

- Crop information and practical cultivation advice
- Current weather and three-day forecasts from OpenWeather
- Location-aware responses using Telegram location messages
- Crop investment and profit estimates
- Optional daily notification subscriptions
- Arabic agricultural Q&A through Azure OpenAI

## Requirements

- Python 3.10 or newer
- A Telegram bot token
- An OpenWeather API key for weather features
- An Azure OpenAI deployment and API key for the AI assistant

The project is intended to run as a Telegram bot process. It does not include
a web server or a separate database.

## Installation

```powershell
git clone <repository-url>
cd AgriSmartBot
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

On Linux or macOS, activate the environment with:

```bash
source .venv/bin/activate
```

## Configuration

Create a `.env` file in the project root. Do not commit this file or place
real credentials in documentation.

```dotenv
TELEGRAM_TOKEN=your_telegram_bot_token
OPENWEATHER_API_KEY=your_openweather_api_key
AZURE_OPENAI_API_KEY=your_azure_openai_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_DEPLOYMENT=your_deployment_name
```

`AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_VERSION`, and
`AZURE_OPENAI_DEPLOYMENT` have defaults in the source, but setting them
explicitly makes deployments reproducible.

## Run

```powershell
python bot.py
```

Send `/start` to the bot and use the reply keyboard to access the available
features. Weather requests require the user to share a location.

## Project structure

```text
AgriSmartBot/
├── bot.py                 # Telegram application and message handlers
├── advice.py              # Crop catalogue and cultivation advice
├── weather.py             # OpenWeather API integration
├── ai_helper.py           # Azure OpenAI integration
├── investment_data.py     # Investment examples and crop data
├── investment_helper.py   # Profit-estimation logic
├── ui.py                  # Reusable Telegram keyboards
├── requirements.txt       # Python dependencies
├── logo/                  # Project media
└── README.md
```

## Development notes

- Keep secrets in environment variables; never commit `.env` or API keys.
- The bot stores subscribers in process memory, so subscriptions are lost when
  the process restarts.
- Validate API responses and user input before adding new handlers.
- Update `requirements.txt` deliberately when dependencies change.

## License

See [LICENSE](./LICENSE).
