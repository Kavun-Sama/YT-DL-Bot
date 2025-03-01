# 📺 YouTube Downloader Telegram Bot

A feature-rich Telegram bot for downloading videos and audio from YouTube with an intuitive inline interface.

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/license-AGPL--3.0-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Telegram-Bot-blue?logo=telegram" alt="Telegram">
</p>

## ✨ Features

- 🌐 Multilingual interface (English/Russian)
- ⌨ Interactive inline keyboard interface
- 🎬 Video quality selection (from 144p to 4K)
- 🔊 Audio extraction with various quality options
- 📁 Upload files up to 2GB via local Telegram API server
- 👥 Works in groups
- 📱 Supports YouTube Shorts
- ⚡ Optimized for high user load

## 🚀 Installation

### Prerequisites

- Python 3.9 or higher
- FFmpeg for media conversion

### Setup

1. **Clone the repository**

```bash
git clone git@github.com:Kavun-Sama/YT-DL-Bot.git
cd YT-DL-Bot
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Create an environment file**

Create a `.env` file with the following configuration:

```env
BOT_TOKEN=your_bot_token
LOCAL_API_URL=http://localhost:8081
```

4. **Launch the bot**

```bash
python bot.py
```

## 📖 Usage

1. 🔗 Send a YouTube video link to the bot
2. 📊 Select format (video or audio)
3. 🔍 For video, choose the desired quality
4. ⏳ Wait for the download to complete
5. 📤 Receive your file

## 💻 Commands

- `/start` - Start the bot
- `/help` - Show help information
- `/language` - Change language


## 🔧 Advanced Configuration

For more advanced settings, you can modify these additional environment variables:

```env
LOG_LEVEL=INFO
MAX_DOWNLOADS=5
DOWNLOAD_TIMEOUT=300
```

## 📋 Requirements

- Python 3.9+
- FFmpeg
- pytube
- aiogram
- python-dotenv

## 📜 License

<img src="https://www.gnu.org/graphics/agplv3-with-text-100x42.png" alt="AGPL Logo" align="right" />

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0) - see the LICENSE file for details.

## 👨‍💻 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
