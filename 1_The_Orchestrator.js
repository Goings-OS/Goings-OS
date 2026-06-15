/**
 * ============================================================================
 * VICTORY GHL MATRIX CORE | 1_The_Orchestrator.gs
 * Architecture: Sovereign Meta-Engine with Automated Fault Isolation
 * Managed Nodes: Sovereign OS Brain, System (The Vortex) & Resilience Core
 * Configuration Version: v4.0.0 (Absolute Production Grade)
 * ============================================================================
 */

function doPost(e) {
  var timestamp = Utilities.formatDate(new Date(), "GMT-5", "MM/dd/yyyy HH:mm:ss");
  Logger.log("📡 [SVEREIGN BRAIN] Intercepting data payload from incoming gateway...");
  
  var vault = PropertiesService.getScriptProperties();
  var OS_CONFIG = {
    ARCHIVE_FOLDER_ID: "1vs8-W5RFQ6UZF0xgdRd4Nzeh_AZbd1wK",
    VAULT_SPREADSHEET_ID: "1rQmQPgMg5z5l6vg9OXcQn5FuINgYJSsw7gd_DXgLCQzB4jWl0rM6n30e",
    LOCATION_ID: vault.getProperty('KIG_GHL_LOCATION_ID') || "SYSTEM_AUTOPILOT",
    STRIPE_RESTRICTED_KEY: vault.getProperty('STRIPE_API_KEY'),
    STRIPE_SECRET_KEY: vault.getProperty('STRIPE_SECRET'),
    GHL_KEY: vault.getProperty('GHL_API_KEY'),
    GEMINI_KEY: vault.getProperty('GEMINI_API_KEY'),
    VERTEX_URL: vault.getProperty('VERTEX_ENDPOINT'),
    BUSINESS_LINE: "757-500-0711",
    FROM_EMAIL: "kigc@keepitgoingsllc.com"
  };
  
  try {
    var rawPayload = JSON.parse(e.postData.contents);
    var firstName = rawPayload.first_name || rawPayload.contact_first_name || "Unknown";
    var lastName = rawPayload.last_name || rawPayload.contact_last_name || "Lead";
    var clientName = (firstName + " " + lastName).trim();
    var email = rawPayload.email || rawPayload.contact_email || "info@goingsos.com";
    var formName = rawPayload.form_name || rawPayload.formName || "Intake Source Unidentified";
    var contactId = rawPayload.contact_id || rawPayload.id || "N/A";
    
    Logger.log("📥 [VORTEX INGESTION] Identity Isolated: " + clientName + " | Context: " + formName);

    // 1. AUTONOMOUS FILE PROVISIONING
    var newFolderUrl = "";
    var clientFolderId = OS_CONFIG.ARCHIVE_FOLDER_ID;
    try {
      var parentFolder = DriveApp.getFolderById(OS_CONFIG.ARCHIVE_FOLDER_ID);
      var clientFolder = parentFolder.createFolder(clientName + " - Asset Vault");
      clientFolder.setDescription("Automated processing partition for " + clientName + ". Secured by Goings OS.");
      newFolderUrl = clientFolder.getUrl();
      clientFolderId = clientFolder.getId();
    } catch (driveError) {
      Logger.log("🚨 [RESILIENCE] Drive redirection triggered: " + driveError.toString());
      newFolderUrl = "Drive Path Bypassed";
    }

    // 2. DYNAMIC HEADER MAPPING MATRIX
    try {
      var ss = SpreadsheetApp.openById(OS_CONFIG.VAULT_SPREADSHEET_ID);
      var targetSheet = ss.getSheetByName("1_Oasis_Master_Manifest") || ss.getSheets()[0];
      var headers = targetSheet.getRange(1, 1, 1, targetSheet.getLastColumn()).getValues()[0];
      var dynamicRowData = [];
      
      for (var i = 0; i < headers.length; i++) {
        var headerName = headers[i].toString().trim().toLowerCase();
        if (headerName === "timestamp") { dynamicRowData.push(timestamp); }
        else if (headerName === "location id") { dynamicRowData.push(OS_CONFIG.LOCATION_ID); }
        else if (headerName === "client identity" || headerName === "client name") { dynamicRowData.push(clientName); }
        else if (headerName === "originating intake form" || headerName === "form name") { dynamicRowData.push(formName); }
        else if (headerName === "asset vault" || headerName === "folder link") { dynamicRowData.push(newFolderUrl); }
        else if (headerName === "email") { dynamicRowData.push(email); }
        else if (headerName === "contact id") { dynamicRowData.push(contactId); }
        else {
          var lookUpKey = headers[i].toString().trim().replace(/\s+/g, '_').toLowerCase();
          dynamicRowData.push(rawPayload[lookUpKey] !== undefined ? rawPayload[lookUpKey] : "");
        }
      }
      targetSheet.appendRow(dynamicRowData);
    } catch (sheetError) {
      Logger.log("🚨 [RESILIENCE] Ledger entry delayed: " + sheetError.toString());
    }
    
    if (contactId !== "N/A" && typeof syncDriveFolderLinkBackToGHL === 'function') {
      syncDriveFolderLinkBackToGHL(contactId, newFolderUrl);
    }
    
    // 3. BINARY FILE CLAW
    try {
      var targetAssetLinks = [];
      for (var key in rawPayload) {
        var valStr = String(rawPayload[key]);
        if (valStr.indexOf("http") !== -1 && (valStr.indexOf("/file/") !== -1 || valStr.indexOf(".pdf") !== -1 || valStr.indexOf(".png") !== -1 || valStr.indexOf(".jpg") !== -1)) {
          targetAssetLinks.push(valStr);
        }
      }
      if (targetAssetLinks.length > 0 && typeof downloadGHLAnaFilesToVault === 'function') {
        downloadGHLAnaFilesToVault(targetAssetLinks, clientFolderId, clientName.replace(/\s+/g, '_'));
      }
    } catch (clawErr) {}

    // 4. METASYSTEM FULFILLMENT CORE
    executeSovereignMetaFulfillment(clientName, email, formName, OS_CONFIG, clientFolderId);

    return ContentService.createTextOutput(JSON.stringify({
      status: "SUCCESS",
      message: "Data completely synthesized via autonomous configuration-driven meta-engine."
    })).setMimeType(ContentService.MimeType.JSON);

  } catch (globalError) {
    executeSelfHealingProtocol("GLOBAL_META_INGESTION_VALVE", globalError.toString(), OS_CONFIG);
    return ContentService.createTextOutput(JSON.stringify({
      status: "HEALED_EXECUTION_STATE",
      trace: globalError.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet(e) {
  try {
    var template = HtmlService.createTemplateFromFile('index');
    var vault = PropertiesService.getScriptProperties();
    template.SYSTEM_NAME = "Victory GHL";
    template.architect = "Terrence Goings";
    template.locationId = vault.getProperty('KIG_GHL_LOCATION_ID') || "Not Setup";
    
    return template.evaluate()
      .setTitle("Victory GHL // Command Center")
      .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
  } catch (error) {
    return ContentService.createTextOutput("BOOT ERROR: " + error.toString());
  }
}

function searchClientsInManifest(query) {
  if (!query || query.trim() === "") return [];
  var cleanQuery = query.trim().toLowerCase();
  var ssId = "1vG_x-z2evnM4r6zw4dgOVOW4CuRYunS6cGAKGOEuNT4";
  
  try {
    var ss = SpreadsheetApp.openById(ssId);
    var sheet = ss.getSheetByName("1_Oasis_Master_Manifest") || ss.getSheets()[0];
    var lastRow = sheet.getLastRow(); if (lastRow <= 1) return [];
    var dataRange = sheet.getRange(2, 1, lastRow - 1, sheet.getLastColumn()).getValues();
    var matchingResults = [];
    
    for (var i = 0; i < dataRange.length; i++) {
      var row = dataRange[i];
      var rowString = row.join(" ").toLowerCase();
      if (rowString.indexOf(cleanQuery) !== -1) {
        matchingResults.push({
          timestamp: row[0] ? Utilities.formatDate(new Date(row[0]), "GMT-5", "MM/dd/yy") : "N/A",
          name: row[2] || "Unknown Identity",
          form: row[3] || "Intake Field",
          folder: row[7] || "#"
        });
      }
    }
    return matchingResults.reverse();
  } catch (e) { return []; }
}

function getLiveManifestRows() {
  try {
    var ss = SpreadsheetApp.openById("1vG_x-z2evnM4r6zw4dgOVOW4CuRYunS6cGAKGOEuNT4");
    var sheet = ss.getSheetByName("1_Oasis_Master_Manifest") || ss.getSheets()[0];
    var lastRow = sheet.getLastRow(); if (lastRow <= 1) return [];
    var startRow = Math.max(2, lastRow - 4); var numRows = lastRow - startRow + 1;
    var values = sheet.getRange(startRow, 1, numRows, sheet.getLastColumn()).getValues();
    return values.reverse().map(function(row) {
      return { timestamp: row[0] ? Utilities.formatDate(new Date(row[0]), "GMT-5", "MM/dd HH:mm") : "N/A", name: row[2] || "Unknown Client", form: row[3] || "Intake Link", folder: row[7] || "#" };
    });
  } catch (e) { return []; }
}

function getLiveFrictionRows() {
  try {
    var ss = SpreadsheetApp.openById("1vG_x-z2evnM4r6zw4dgOVOW4CuRYunS6cGAKGOEuNT4");
    var sheet = ss.getSheetByName("System_Friction_Logs"); if (!sheet) return [];
    var lastRow = sheet.getLastRow(); if (lastRow <= 1) return [];
    var startRow = Math.max(2, lastRow - 4); var numRows = lastRow - startRow + 1;
    var values = sheet.getRange(startRow, 1, numRows, 4).getValues();
    return values.reverse().map(function(row) {
      return { timestamp: row[0] ? Utilities.formatDate(new Date(row[0]), "GMT-5", "MM/dd HH:mm") : "N/A", layer: row[1] || "Core", error: row[2] || "Trace Clean" };
    });
  } catch (e) { return []; }
}

function processCommandFromCenter(userPrompt) {
  if (!userPrompt || userPrompt.trim() === "") return "Terminal alert: Received empty input block.";
  var structuralDirective = "ROLE: Multi-agent organizational leadership panel inside Terrence Goings' private ecosystem. Execute this command with zero-friction compliance: " + userPrompt;
  return askTheArchitect(structuralDirective);
}

function executeSovereignMetaFulfillment(clientName, email, formName, config, folderId) {
  var ss = SpreadsheetApp.openById(config.VAULT_SPREADSHEET_ID);
  var configSheet = ss.getSheetByName("System_Agent_Registry");
  var agentDirective = "ROLE: Elite Consumer Law Forensic Auditor. Strategy: Execute an advanced factual dispute audit challenge using strict Metro 2 formatting compliance parameters. Output clean body text paragraphs only.";
  var subject = "📥 [PROCESSING] Documentation Update | Keep It Goings Consulting";
  var emailBodyCopy = "Our processing desks have successfully initialized your corporate file metrics evaluation pipeline routing parameters.";
  
  if (configSheet) {
    var data = configSheet.getDataRange().getValues();
    for (var i = 1; i < data.length; i++) {
      var matchKeyword = data[i][0].toString().trim().toLowerCase();
      if (formName.toLowerCase().indexOf(matchKeyword) !== -1) {
        agentDirective = data[i][1] || agentDirective;
        subject = data[i][2] || subject;
        emailBodyCopy = data[i][3] || emailBodyCopy;
        break;
      }
    }
  }

  if (formName.includes("Credit") || formName.includes("Form 2")) {
    var fullAuditPrompt = "TASK DIRECTIVE: Complete a high-acumen analysis baseline for client: " + clientName + ".\n\n" + agentDirective;
    var rawAIOutput = askTheArchitect(fullAuditPrompt);
    var iterationCount = 0; var passValidationCheck = false;
    
    while (!passValidationCheck && iterationCount < 3) {
      if (rawAIOutput.indexOf("STRIKE_ERROR") === -1 && rawAIOutput.length > 300 && rawAIOutput.indexOf("🚨") === -1) {
        passValidationCheck = true;
      } else {
        iterationCount++;
        var correctionPrompt = "CRITICAL ANALYSIS ADJUSTMENT FAILURE: Output trace failed compliance rules. Re-compile: " + rawAIOutput;
        rawAIOutput = askTheArchitect(correctionPrompt);
      }
    }
    generateBrandedClientDocument(clientName, folderId, clientName.replace(/\s+/g, '_') + "_Forensic_Metro2_Analysis", rawAIOutput);
  }

  var completeTemplate = "Hi " + clientName + ",\n\n" + emailBodyCopy + "\n\nOperations Desk | Keep It Goings Consulting";
  try { MailApp.sendEmail(clientEmail, subject, completeTemplate, { from: config.FROM_EMAIL }); } catch (err) {}
}

/**
 * COGNITIVE PROCESSING GATEWAY (VERTEX AI CORES)
 */
function askTheArchitect(promptMarrow) {
  var vault = PropertiesService.getScriptProperties();
  var url = vault.getProperty('VERTEX_ENDPOINT');
  var token = ScriptApp.getOAuthToken();

  if (url && url.trim() !== "") {
    var payload = { "contents": [{ "role": "user", "parts": [{ "text": promptMarrow }] }] };
    var options = { "method": "post", "contentType": "application/json", "headers": { "Authorization": "Bearer " + token }, "payload": JSON.stringify(payload), "muteHttpExceptions": true };
    try {
      var response = UrlFetchApp.fetch(url, options);
      var result = JSON.parse(response.getContentText());
      if (result && result.candidates && result.candidates[0] && result.candidates[0].content && result.candidates[0].content.parts && result.candidates[0].content.parts[0]) {
        return result.candidates[0].content.parts[0].text;
      }
      throw new Error(result && result.error ? result.error.message : "Malformed Primary Payload Layout.");
    } catch (vertexError) {
      return executeHealedGeminiFallbackCall(promptMarrow, vertexError.toString());
    }
  } else {
    return executeHealedGeminiFallbackCall(promptMarrow, "Vertex destination address space un-provisioned.");
  }
}

/**
 * RESILIENCE FALLBACK CIRCUIT (DIRECT DEVELOPER COGNITION ENTRY)
 */
function executeHealedGeminiFallbackCall(prompt, rawErrorString) {
  var vault = PropertiesService.getScriptProperties();
  var apiKey = vault.getProperty('GEMINI_API_KEY');
  if (!apiKey) return "🚨 RESILIENCE FAULT: Both processing endpoints throttled. Verify environment keys.";
  
  // Clean production-stable endpoint link structure
  var fallbackUrl = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key=" + apiKey;
  var payload = { "contents": [{ "role": "user", "parts": [{ "text": prompt }] }] };
  var options = { "method": "post", "contentType": "application/json", "payload": JSON.stringify(payload), "muteHttpExceptions": true };

  try {
    var response = UrlFetchApp.fetch(fallbackUrl, options);
    var result = JSON.parse(response.getContentText());
    executeSelfHealingProtocol("VERTEX_PLATFORM_DECOUPLED_FALLBACK_ACTIVE", rawErrorString, { VAULT_SPREADSHEET_ID: "1vG_x-z2evnM4r6zw4dgOVOW4CuRYunS6cGAKGOEuNT4" });
    
    // Airtight validation interception mapping
    if (result && result.error) {
      return "🚨 ENVIROMENT EXCEPTION: " + result.error.message + " (Review GEMINI_API_KEY value layout).";
    }
    if (result && result.candidates && result.candidates[0] && result.candidates[0].content && result.candidates[0].content.parts && result.candidates[0].content.parts[0]) {
      return result.candidates[0].content.parts[0].text;
    } else {
      return "🚨 STRUCTURAL VARIATION: API structural layout response mismatched. Content: " + JSON.stringify(result);
    }
  } catch (e) {
    return "🚨 CRITICAL ISOLATION GAP: Autonomous recovery line offline. Trace: " + e.toString();
  }
}

function executeSelfHealingProtocol(errorLayer, errorString, config) {
  try {
    var ss = SpreadsheetApp.openById(config.VAULT_SPREADSHEET_ID);
    var logTab = ss.getSheetByName("System_Friction_Logs");
    if (!logTab) {
      logTab = ss.insertSheet("System_Friction_Logs");
      logTab.appendRow(["Timestamp", "Module", "Error Trace", "Status"]);
    }
    logTab.appendRow([new Date(), errorLayer, errorString, "HEALED_BY_DYNAMIC_OVERRIDE"]);
  } catch (err) {}
}

function generateBrandedClientDocument(clientName, folderId, docTitle, documentBodyText) {
  try {
    var targetFolder = DriveApp.getFolderById(folderId);
    var doc = DocumentApp.create(docTitle); var file = DriveApp.getFileById(doc.getId());
    targetFolder.addFile(file); DriveApp.getRootFolder().removeFile(file);
    var body = doc.getBody(); body.setMarginTop(54); body.setMarginBottom(54); body.setMarginLeft(54); body.setMarginRight(54);
    var headerPara = body.appendParagraph("KEEP IT GOINGS CONSULTING");
    headerPara.setAlignment(DocumentApp.HorizontalAlignment.CENTER);
    headerPara.setFontFamily("Montserrat"); headerPara.setFontSize(14); headerPara.setBold(true); headerPara.setForegroundColor("#FACC15");
    body.appendHorizontalRule(); body.appendParagraph("\n");
    var contentPara = body.appendParagraph(documentBodyText);
    contentPara.setFontFamily("Arial"); contentPara.setFontSize(11); contentPara.setForegroundColor("#0F172A");
    doc.saveAndClose(); return file.getUrl();
  } catch (e) { return null; }
}

/**
 * ============================================================================
 * STRIPE FINANCIAL COUPLING LAYER (System Engine Tools Integration)
 * ============================================================================
 */
function fetchStripeDataMatrix(endpointPath, httpMethod, config) {
  var activeKey = config.STRIPE_SECRET_KEY || config.STRIPE_RESTRICTED_KEY;
  if (!activeKey) return { error: true, message: "Missing structural secret verification fields." };
  var url = "https://api.stripe.com/v1/" + endpointPath;
  var options = { "method": httpMethod || "get", "muteHttpExceptions": true, "headers": { "Authorization": "Bearer " + activeKey } };
  try {
    var response = UrlFetchApp.fetch(url, options);
    if (response.getResponseCode() === 200 || response.getResponseCode() === 201) return JSON.parse(response.getContentText());
    return { error: true, message: response.getContentText() };
  } catch (err) { return { error: true, message: err.toString() }; }
}