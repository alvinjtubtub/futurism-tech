#!/usr/bin/env bash
# setup-gdrive.sh — Generates Google Drive credentials for GitHub Actions auto-delivery.
# Supports Option 1 (Google Drive User OAuth Token via Rclone) and Option 2 (Google Service Account).

set -e

echo "=== Google Drive Setup for GitHub Actions KAPE Pipeline ==="
echo ""
echo "Select authentication method for your Google Drive:"
echo "1) Rclone OAuth Token (Recommended for personal Gmail / Google Workspace)"
echo "2) Google Cloud Service Account JSON (Recommended for permanent, non-expiring server auth)"
read -p "Enter choice [1 or 2]: " choice

if [ "$choice" = "1" ]; then
  echo ""
  echo "--- Option 1: Rclone OAuth Token ---"
  
  if ! command -v rclone &> /dev/null; then
    echo "Rclone not found on this Mac. Installing via brew..."
    if command -v brew &> /dev/null; then
      brew install rclone
    else
      echo "Homebrew not found. Please install rclone from https://rclone.org/downloads/ or run:"
      echo "  sudo -v ; curl https://rclone.org/install.sh | sudo bash"
      exit 1
    fi
  fi

  echo ""
  echo "Opening browser to authorize Google Drive..."
  echo "Sign in to the Google account that owns your Tech Explanasyon Google Drive folder."
  echo ""
  
  TOKEN_OUTPUT=$(rclone authorize "drive" "scope=drive")
  
  echo ""
  echo "==================== COPY YOUR SECRET BELOW ===================="
  TOKEN_JSON=$(echo "$TOKEN_OUTPUT" | sed -n '/^{.*}$/p')
  if [ -n "$TOKEN_JSON" ]; then
    echo "$TOKEN_JSON"
  else
    echo "$TOKEN_OUTPUT"
  fi
  echo "================================================================"
  echo ""
  echo "Next Steps:"
  echo "1. Go to: https://github.com/alvinjtubtub/futurism-tech/settings/secrets/actions"
  echo "2. Click 'New repository secret'"
  echo "3. Name: RCLONE_GDRIVE_TOKEN"
  echo "4. Value: (paste the single JSON line above)"
  echo "5. Click 'Add secret'"
  echo ""
  echo "Done! GitHub Actions will now automatically upload all completed videos directly to Google Drive!"

elif [ "$choice" = "2" ]; then
  echo ""
  echo "--- Option 2: Google Cloud Service Account ---"
  echo "1. Open Google Cloud Console -> IAM & Admin -> Service Accounts"
  echo "2. Create a service account (e.g. 'kape-video-publisher@...')"
  echo "3. Click on the Service Account -> Keys -> Add Key -> Create new key -> JSON."
  echo "4. Share your Google Drive folder '03-Completed-Videos' (ID: 1z5082Iq5JgOC4vYgirMim9vOYMcUhDRe)"
  echo "   with the service account email (give Editor access)."
  echo "5. Go to: https://github.com/alvinjtubtub/futurism-tech/settings/secrets/actions"
  echo "6. Add secret: GDRIVE_SA_KEY with the contents of your downloaded JSON file."
  echo ""
fi
