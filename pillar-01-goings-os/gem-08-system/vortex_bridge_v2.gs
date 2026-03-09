/** * THE GOINGS OS: VORTEX BRIDGE V2.0 
 * COMMANDER: [KING GOINGS] | GRID: 757
 * CORE MODEL: GEMINI 1.5 PRO
 */

const CONFIG = {
  GEMINI_KEY: "PASTE_YOUR_GEMINI_KEY",
  STRIPE_KEY: "PASTE_YOUR_STRIPE_KEY",
  GHL_WEBHOOK: "PASTE_YOUR_GHL_WEBHOOK", // Connected to 757-500-0711
  YIELD_TARGET: 714.28
};

/**
 * THE SWARM COMMAND: This talks to all 12 Gems
 */
function callTheSwarm(agentNumber, task) {
  const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key=${CONFIG.GEMINI_KEY}`;
  const payload = {
    "contents": [{ "parts": [{ "text": `System Order for Agent ${agentNumber}: ${task}` }] }]
  };
  
  const response = UrlFetchApp.fetch(url, {
    method: "post",
    contentType: "application/json",
    payload: JSON.stringify(payload)
  });
  
  return JSON.parse(response.getContentText()).candidates[0].content.parts[0].text;
}

/**
 * THE 711 DISPATCHER: SMS Alert System
 */
function sendCommanderAlert(msg) {
  const options = {
    method: "post",
    contentType: "application/json",
    payload: JSON.stringify({ "to": "7575000711", "message": `[GOINGS OS]: ${msg}` })
  };
  UrlFetchApp.fetch(CONFIG.GHL_WEBHOOK, options);
}

/**
 * THE HARBINGER: Daily Yield Calculation
 */
function checkDailyYield() {
  const stripeUrl = "https://api.stripe.com/v1/balance_transactions?limit=20";
  const options = { method: "get", headers: { "Authorization": "Bearer " + CONFIG.STRIPE_KEY } };
  const response = JSON.parse(UrlFetchApp.fetch(stripeUrl, options));
  
  let currentYield = 0;
  response.data.forEach(tx => { if(tx.type === 'charge') currentYield += (tx.amount / 100); });
  
  const percentage = (currentYield / CONFIG.YIELD_TARGET) * 100;
  sendCommanderAlert(`Yield Update: $${currentYield.toFixed(2)} (${percentage.toFixed(1)}% of Daily Goal)`);
  
  return currentYield;
}
