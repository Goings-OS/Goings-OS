# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: UNIFIED COMPUTER USE COGNITIVE ENGINE
# BIND: BRANCH KING GOINGS 81 // GEMINI 3.5 FLASH NATIVE
# COMPLIANCE: ZERO EM-DASHES ENFORCED // ALWAYS POSITIVE
# ==============================================================================

import os
import time
from datetime import datetime, timezone
from dotenv import load_dotenv
from google import genai
from google.genai import types
from playwright.sync_api import sync_playwright
from agent_state_wrapper import AgentStateWrapper

load_dotenv()

class GoingsComputerUseEngine:
    """Controls native screen interaction using the 5 core design patterns."""

    def __init__(self, task_prompt: str, width: int = 1280, height: int = 800):
        self.task_prompt = task_prompt
        self.width = width
        self.height = height
        self.client = genai.Client()
        self.state_wrapper = AgentStateWrapper()
        self.history = []
        self.max_saved_screenshots = 2

    def denormalize_coordinates(self, norm_x: int, norm_y: int) -> tuple[int, int]:
        """Pattern 1: Translates universal 0-999 coordinates to local layout pixels."""
        pixel_x = int(norm_x / 1000 * self.width)
        pixel_y = int(norm_y / 1000 * self.height)
        return pixel_x, pixel_y

    def prune_context_history(self):
        """Pattern 5: Clears historical image data blobs to protect token margins."""
        screenshots_counted = 0
        for content in reversed(self.history):
            if content.role != "user" or not content.parts:
                continue
            
            has_image = any(p.function_response and p.function_response.parts for p in content.parts)
            if has_image:
                screenshots_counted += 1
                if screenshots_counted > self.max_saved_screenshots:
                    for part in content.parts:
                        if part.function_response and part.function_response.parts:
                            part.function_response.parts = None
                            print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] [PRUNE] Historical image byte array cleared.")

    def execute_autonomous_loop(self):
        """Pattern 2: Runs the persistent multi-step observe-think-act sequence."""
        print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] [START] Initializing visual assembly line loop.")
        
        with sync_playwright() as spatial_hand:
            browser = spatial_hand.chromium.launch(headless=False)
            context = browser.new_context(viewport={"width": self.width, "height": self.height})
            page = context.new_page()
            
            page.goto("https://news.ycombinator.com")
            page.wait_for_load_state("load")
            
            computer_use_tool = types.Tool(
                computer_use=types.ComputerUse(
                    environment=types.Environment.ENVIRONMENT_BROWSER
                )
            )

            screenshot_bytes = page.screenshot(type="png")
            
            self.history.append(types.Content(
                role="user",
                parts=[
                    types.Part(text=self.task_prompt),
                    types.Part(inline_data=types.Blob(mime_type="image/png", data=screenshot_bytes))
                ]
            ))

            turn_limit = 6
            for active_turn in range(turn_limit):
                print(f"\n--- Digital Assembly Line: Processing Turn {active_turn + 1} ---")
                
                response = self.client.models.generate_content(
                    model="gemini-3.5-flash",
                    contents=self.history,
                    config=types.GenerateContentConfig(
                        tools=[computer_use_tool],
                        thinking_config=types.ThinkingConfig(include_thoughts=True)
                    )
                )

                if response.candidates and response.candidates[0].content:
                    self.history.append(response.candidates[0].content)
                    
                has_function_calls = any(part.function_call for part in response.candidates[0].content.parts if part.function_call)
                
                if not has_function_calls:
                    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] [COMPLETE] Task concluded successfully.")
                    print(f"Final Agent Report: {response.text}")
                    break

                for part in response.candidates[0].content.parts:
                    if part.function_call:
                        call_object = part.function_call
                        action_name = call_object.name
                        arguments = call_object.args
                        intent = arguments.get("intent", "No intention declared.")
                        
                        print(f" -> Agent Decision: {action_name}")
                        print(f" -> Stated Intent: {intent}")

                        if action_name in ["click", "click_at"]:
                            norm_x = int(arguments.get("x", 0))
                            norm_y = int(arguments.get("y", 0))
                            target_x, target_y = self.denormalize_coordinates(norm_x, norm_y)
                            
                            page.mouse.click(target_x, target_y)
                            page.wait_for_load_state("load")
                            time.sleep(1)

                        post_action_screenshot = page.screenshot(type="png")
                        
                        self.history.append(types.Content(
                            role="user",
                            parts=[
                                types.Part(
                                    function_response=types.FunctionResponse(
                                        name=action_name,
                                        response={"status": "ok", "current_url": page.url},
                                        parts=[
                                            types.Part(inline_data=types.Blob(mime_type="image/png", data=post_action_screenshot))
                                        ]
                                    )
                                )
                            ]
                        ))

                self.prune_context_history()

            browser.close()

if __name__ == "__main__":
    task = "Locate the top article link on the page, click it, and wait for load."
    engine = GoingsComputerUseEngine(task_prompt=task)
    engine.execute_autonomous_loop()
