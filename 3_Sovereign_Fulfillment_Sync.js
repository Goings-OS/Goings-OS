/**
 * ============================================================================
 * VICTORY GHL | 3_Sovereign_Fulfillment_Sync.gs
 * Role: Advanced GHL Custom Field Sync & Binary Asset Ingestion Claw
 * Core Component: I_SOVEREIGNTY Downstream Sync Layer
 * ============================================================================
 */

/**
 * THE ASSET INGESTION CLAW
 * Downloads files from GHL temporary links and places them directly into the Drive Vault
 */
function downloadGHLAnaFilesToVault(fileUrlArray, targetFolderId, baseFileName) {
  if (!fileUrlArray || fileUrlArray.length === 0) {
    Logger.log("ℹ [CLAW] No document attachment links detected in this payload string.");
    return;
  }
  
  const targetFolder = DriveApp.getFolderById(targetFolderId);
  Logger.log(`📡 [CLAW] Ingesting ${fileUrlArray.length} external binary files to secure partition...`);

  fileUrlArray.forEach((url, index) => {
    try {
      if (!url || url.trim() === "") return;
      
      // Fetch the raw file binary data from the secure GHL server path
      const response = UrlFetchApp.fetch(url.trim());
      const blob = response.getBlob();
      
      // Assign an enterprise naming convention based on document type
      const extension = blob.getContentType().split("/")[1] || "pdf";
      blob.setName(`${baseFileName}_Asset_${index + 1}.${extension}`);
      
      // Commit file directly to the physical storage partition
      const physicalFile = targetFolder.createFile(blob);
      Logger.log(`📁 [CLAW SUCCESS] Document securely stamped to drive: ${physicalFile.getName()}`);
    } catch (err) {
      Logger.log(`🚨 [CLAW FAULT] Failed to download file from link [${url}]: ${err.toString()}`);
    }
  });
}

/**
 * THE OUTBOUND FEEDBACK LOOP
 * Uses your GHL_API_KEY to update a custom field directly inside your GHL Contact Dashboard
 */
function syncDriveFolderLinkBackToGHL(contactId, googleDriveFolderUrl) {
  const vault = PropertiesService.getScriptProperties();
  const apiKey = vault.getProperty('GHL_API_KEY');
  
  // Hardcoded Custom Field ID mapping for your "Google Drive Folder" link box in GHL
  // Replace this placeholder string with your real custom field ID from GHL Settings if needed
  const CUSTOM_FIELD_ID = "google_drive_vault_link"; 

  if (!apiKey || !contactId) {
    Logger.log("⚠️ [GHL SYNC] Bypassing field sync. Missing API authorization tokens or Contact ID.");
    return false;
  }

  const url = `https://services.leadconnectorhq.com/contacts/${contactId}`;
  
  const payload = {
    "customFields": [
      {
        "id": CUSTOM_FIELD_ID,
        "value": googleDriveFolderUrl
      }
    ]
  };

  const options = {
    "method": "put",
    "contentType": "application/json",
    "headers": {
      "Authorization": "Bearer " + apiKey,
      "Version": "2021-04-15" // Locked GoHighLevel API Version Gateway
    },
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };

  try {
    Logger.log(`⚡ [GHL SYNC] Dispatching outbound PUT request to sync Drive Link for Contact ID: ${contactId}`);
    const response = UrlFetchApp.fetch(url, options);
    const responseCode = response.getResponseCode();
    
    if (responseCode === 200 || responseCode === 201) {
      Logger.log("✅ [GHL SYNC SUCCESS] GHL Contact profile card successfully stamped with your Drive Vault URL.");
      return true;
    } else {
      Logger.log(`🚨 [GHL SYNC REFUSED] Status Code: ${responseCode} | Details: ${response.getContentText()}`);
      return false;
    }
  } catch (syncErr) {
    Logger.log(`🚨 [GHL SYNC CRITICAL FAULT] Infrastructure connection timeout: ${syncErr.toString()}`);
    return false;
  }
}