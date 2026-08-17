#!/bin/sh
set -eu

: "${RED_TOKEN:?RED_TOKEN is required}"
: "${RED_OWNER:?RED_OWNER is required}"

mkdir -p /data

# Web Service support: Render requires an HTTP listener on $PORT.
python /app/docker/render-health.py &
HEALTH_PID=$!

# Optional Render free-tier keepalive. Render supplies RENDER_EXTERNAL_URL
# automatically for web services. This does not replace Render's lifecycle
# controls; it simply requests /health while the service is already running.
python /app/docker/render-keepalive.py &
KEEPALIVE_PID=$!

cleanup() {
    kill "$KEEPALIVE_PID" "$HEALTH_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

if [ ! -f "$HOME/.config/Red-DiscordBot/config.json" ]; then
    redbot-setup --no-prompt \
        --instance-name "$RED_INSTANCE" \
        --data-path "$RED_DATA_DIR" \
        --backend json
fi

redbot "$RED_INSTANCE" \
    --token "$RED_TOKEN" \
    --owner "$RED_OWNER" &
BOT_PID=$!

wait "$BOT_PID"
