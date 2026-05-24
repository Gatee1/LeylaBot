#!/bin/bash

echo "🚀 Starting Leyla Bot + API..."

# Запускаем API сервер в фоне
python bot/api_server.py &

# Запускаем бота
python bot/main.py