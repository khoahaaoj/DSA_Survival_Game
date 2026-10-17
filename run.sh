#!/usr/bin/env bash
# Script khoi dong DSA Survival Game cho Linux / macOS

set -e

echo "========================================================"
echo "       ⚔️  DSA SURVIVAL GAME - UIT  ⚔️"
echo "========================================================"
echo ""

# 1. Kiem tra Python 3
if ! command -v python3 &> /dev/null; then
    echo "[LỖI] Không tìm thấy python3 trên hệ thống của bạn!"
    echo "Vui lòng cài đặt Python 3 (khuyến nghị >= 3.10) trước khi chạy."
    exit 1
fi

# Chuyen den thu muc chua script
cd "$(dirname "$0")"

# 2. Tao/Kich hoat Virtual Environment
if [ ! -d "venv" ]; then
    echo "[*] Đang khởi tạo môi trường ảo (venv)..."
    python3 -m venv venv
fi

source venv/bin/activate

# 3. Kiem tra thu vien
if ! python -c "import pygame" &> /dev/null; then
    echo "[*] Đang cài đặt thư viện từ requirements.txt..."
    pip install -r requirements.txt
fi

# 4. Khoi dong game
echo "[*] Đang khởi động game..."
python main.py
