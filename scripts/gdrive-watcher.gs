/**
 * gdrive-watcher.gs — Google Apps Script for Auto-Triggering KAPE Cloud Video Pipeline.
 *
 * HOW IT WORKS:
 * Whenever you drop a voiceover audio file (.mp3 or .wav) into your Google Drive folder
 * "01-Audio-Intake" from your Android phone, this script triggers your GitHub Actions cloud runner.
 *
 * SETUP (Takes 2 minutes):
 * 1. Open Google Drive (drive.google.com) on your computer or phone browser.
 * 2. Click "+ New" -> "More" -> "Google Apps Script" (or go to script.google.com).
 * 3. Paste this entire code.
 * 4. Replace GITHUB_PAT with a GitHub Personal Access Token (with 'repo' scope).
 * 5. Run setupTrigger() once.
 * Done! Now any audio file saved to 01-Audio-Intake triggers the cloud video render!
 */

const CONFIG = {
  GITHUB_OWNER: "alvinjtubtub",
  GITHUB_REPO: "futurism-tech",
  // Create a PAT with 'repo' scope at: https://github.com/settings/tokens
  GITHUB_PAT: "PASTE_YOUR_GITHUB_TOKEN_HERE",
  
  // Google Drive Folder IDs
  INTAKE_FOLDER_ID: "1BZcjqcHBWL64o1CC26tjdIFMu8nwjqoz", // 01-Audio-Intake
  PROCESSED_FOLDER_NAME: "processed"
};

function checkIntakeAndTrigger() {
  const folder = DriveApp.getFolderById(CONFIG.INTAKE_FOLDER_ID);
  const files = folder.getFiles();

  // Ensure processed/ subfolder exists
  let processedFolder;
  const subfolders = folder.getFoldersByName(CONFIG.PROCESSED_FOLDER_NAME);
  if (subfolders.hasNext()) {
    processedFolder = subfolders.next();
  } else {
    processedFolder = folder.createFolder(CONFIG.PROCESSED_FOLDER_NAME);
  }

  while (files.hasNext()) {
    const file = files.next();
    const name = file.getName();
    
    // Only process audio files
    if (name.match(/\.(mp3|wav|m4a)$/i)) {
      const slug = name.replace(/\.[^/.]+$/, "").toLowerCase().replace(/[^a-z0-9_-]/g, "-");
      Logger.log("Found new narration audio: " + name + " -> Slug: " + slug);

      const success = triggerGitHubAction(slug, file.getId(), name);
      if (success) {
        // Move file to processed folder
        file.moveTo(processedFolder);
        Logger.log("Moved " + name + " to processed folder.");
      }
    }
  }
}

function triggerGitHubAction(slug, fileId, fileName) {
  const url = `https://api.github.com/repos/${CONFIG.GITHUB_OWNER}/${CONFIG.GITHUB_REPO}/dispatches`;
  const payload = {
    event_type: "drive_audio_upload",
    client_payload: {
      slug: slug,
      file_id: fileId,
      file_name: fileName
    }
  };

  const options = {
    method: "post",
    contentType: "application/json",
    headers: {
      "Authorization": "Bearer " + CONFIG.GITHUB_PAT,
      "Accept": "application/vnd.github.v3+json",
      "User-Agent": "Google-Apps-Script-KAPE-Pipeline"
    },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };

  const response = UrlFetchApp.fetch(url, options);
  const code = response.getResponseCode();

  if (code === 204) {
    Logger.log("Successfully triggered GitHub Actions cloud render for: " + slug);
    return true;
  } else {
    Logger.log("Failed to trigger GitHub Actions (Status " + code + "): " + response.getContentText());
    return false;
  }
}

/**
 * Run this function once to check the folder automatically every 5 minutes.
 */
function setupTrigger() {
  // Delete existing triggers
  const triggers = ScriptApp.getProjectTriggers();
  for (let i = 0; i < triggers.length; i++) {
    ScriptApp.deleteTrigger(triggers[i]);
  }

  // Create new timer-based trigger running every 5 minutes
  ScriptApp.newTrigger("checkIntakeAndTrigger")
    .timeBased()
    .everyMinutes(5)
    .create();

  Logger.log("Automatic 5-minute trigger created successfully!");
}
