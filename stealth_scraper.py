import asyncio
import random
import json
from typing import Dict, Any, List
import aiohttp
from bs4 import BeautifulSoup

class EnterpriseIngestionNode:
    def __init__(self, tenant_id: str = "Choice Inc"):
        self.tenant_id = tenant_id
        # Rotating industrial user-agent matrix to mask browser signatures
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        ]

    def _generate_stealth_headers(self) -> Dict[str, str]:
        """Synthesizes realistic, un-insulated browser metadata on every transaction."""
        return {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Upgrade-Insecure-Requests": "1"
        }

    async def ingest_target_stream(self, session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
        """Executes high-velocity async extraction with integrated fallback protection."""
        headers = self._generate_stealth_headers()
        try:
            # Introduce a variable micro-delay to simulate organic human interaction
            await asyncio.sleep(random.uniform(0.5, 2.0))
            
            async with session.get(url, headers=headers, timeout=12) as response:
                if response.status != 200:
                    return {"url": url, "status": "NETWORK_ERR", "code": response.status}
                
                raw_html = await response.text()
                return self._parse_semantic_payload(raw_html, url)
                
        except Exception as e:
            return {"url": url, "status": "EXCEPTION_FATAL", "details": str(e)}

    def _parse_semantic_payload(self, html_content: str, source_url: str) -> Dict[str, Any]:
        """Transforms noisy web code into structural knowledge blocks."""
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Immediate removal of structural code noise and interface elements
        for noise in soup(["script", "style", "iframe", "footer", "nav", "header", "aside"]):
            noise.decompose()
            
        # Target structured markup if explicitly provided by the web node
        json_ld = soup.find("script", type="application/ld+json")
        structured_data = json.loads(json_ld.string) if json_ld else None
        
        # Extract clean, scannable text segments
        text_lines = [line.strip() for line in soup.get_text(separator="\n").splitlines() if line.strip()]
        dense_content = "\n".join(text_lines)
        
        return {
            "source_url": source_url,
            "status": "PROCESSED",
            "tenant_allocation": self.tenant_id,
            "structured_metadata": structured_data,
            "cleaned_payload_density": len(dense_content),
            "extraction_matrix": dense_content[:2000] # Safe preview truncation for systemic ingestion
        }

    async def execute_bulk_pool(self, url_targets: List[str]) -> List[Dict[str, Any]]:
        """Coordinates multi-threaded batch operations concurrently across the network."""
        async with aiohttp.ClientSession() as session:
            tasks = [self.ingest_target_stream(session, url) for url in url_targets]
            return await asyncio.gather(*tasks)