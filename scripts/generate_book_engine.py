import os
import requests
import json
import time

# Goings OS Direct REST API Setup
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ENDPOINT_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={GEMINI_API_KEY}"

# Book Metadata
BOOK_TITLE = "KEEP IT GOINGS: THE EVERYDAY FOUNDER'S BLUEPRINT TO AI AUTOMATION"
AUTHOR = "Terrence Goings"
PUBLISHERS = "Keep It Goings LLC & Goings OS LLC"

# The 6-Chapter Best-Seller Blueprint
SECTIONS = [
    {
        "type": "Front Matter",
        "title": "Prelude: The Norfolk Origin & The Math of the Streets",
        "focus": "Born November 14, 1981 in Norfolk, Virginia. Mischievous adolescence turned street smarts. Helping his mother (Barbara Goings), a math teacher, grade algebra, calculus, and statistics papers as a child. Learning early that everything and everyone has a specific place and value, bridging street logic directly into software code."
    },
    {
        "type": "Front Matter",
        "title": "Table of Contents & Best-Seller Reader Roadmap",
        "focus": "Complete structural roadmap of the book, explaining callout boxes, primary source notes, and how to read for rapid implementation."
    },
    {
        "type": "Core Chapter",
        "title": "Chapter 1: Proof Before Promises: Street Logic Meets AI",
        "focus": "Demanding real proof over marketing hype. Giving away the Who, What, and When for free to empower the community, while Keep It Goings LLC monetizes the proprietary HOW execution."
    },
    {
        "type": "Core Chapter",
        "title": "Chapter 2: Demystifying AI & The C-P-O Framework",
        "focus": "Stripping away academic confusion. Explaining generative companions in plain English. Full breakdown of Context, Persona, and Output rules with practical templates."
    },
    {
        "type": "Core Chapter",
        "title": "Chapter 3: The 15-Hour Time Audit: Building Your Life Operating System",
        "focus": "Building a business operating system that lets you work ON your business instead of IN your business. Reclaiming 15 hours a week to protect family sovereignty, health, and legacy."
    },
    {
        "type": "Core Chapter",
        "title": "Chapter 4: Building Kernels & The Shepardizing Principle",
        "focus": "Writing 24/7 system kernels. The Shepardizing Principle: double-checking AI responses against primary document verification, open-source schematics, and custom code wrappers."
    },
    {
        "type": "Core Chapter",
        "title": "Chapter 5: Practical Workflows & The Executive Second Brain",
        "focus": "Everyday AI workflows for local service businesses and creators. Capturing founder knowledge and story in structured Markdown memory vaults so no idea is ever lost."
    },
    {
        "type": "Core Chapter",
        "title": "Chapter 6: The Bridge to Enterprise Scale & Community Healing",
        "focus": "Transitioning from basic prompts to autonomous GoHighLevel CRM webhooks powered by Goings OS LLC. Upskilling Hampton Roads founders to build generational wealth."
    },
    {
        "type": "Back Matter",
        "title": "Epilogue: The Crown Principle",
        "focus": "Executive sovereignty, self-determination, taking ownership of your vision, and leaving a lasting family legacy."
    },
    {
        "type": "Back Matter",
        "title": "Glossary & Founder AI Dictionary",
        "focus": "A plain English dictionary of key terms: AI, Prompt, Context, Persona, Workflow, Agent, Kernel, Shepardizing, REST API, Webhook, and Second Brain."
    },
    {
        "type": "Back Matter",
        "title": "Notes, Citations & Primary Sources",
        "focus": "Formal best-seller reference index citing research papers on generative reasoning, system prompt architectures, labor statistics on time recovery, and foundational computer science principles."
    }
]

OUTPUT_FILE = "brain/manuscript/keep_it_goings_6chapter_blueprint.md"

def generate_section(section):
    prompt = f"""
    Act as an elite technology author writing in the authentic, street-smart, inspiring voice of Terrence Goings.
    Write full, high-impact narrative prose for the following section of the book '{BOOK_TITLE}'.
    
    SECTION TITLE: {section['title']}
    SECTION TYPE: {section['type']}
    CORE FOCUS: {section['focus']}
    
    STRICT VOICE & PUBLISHING GUIDELINES:
    1. STRICTLY ZERO EM-DASHES across the entire text. Use colons, commas, periods, or standard parentheses.
    2. AUTHOR VOICE: Terrence Goings was born November 14, 1981 in Norfolk, VA. Raised with street smarts and educated at his mother Barbara Goings' table grading algebra, calculus, and statistics papers. Everything and everyone has value and place.
    3. BEST-SELLER STRUCTURE: Include professional subheadings, indented callout blocks, actionable steps, and formal citations/source references where appropriate.
    4. CORE PHILOSOPHY: Life Operating System philosophy (working ON your business, not IN your business to protect family time).
    5. Author Credit: Terrence Goings.
    6. Protect backend code secrets and proprietary algorithms while explaining the Who, What, and When clearly.
    7. Write at least 1,500 words for this section.
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    headers = {"Content-Type": "application/json"}
    
    print(f"Generating {section['title']}...")
    response = requests.post(ENDPOINT_URL, headers=headers, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    else:
        print(f"Error generating {section['title']}: {response.text}")
        return f"\n\n## {section['title']}\n\n[Generation Failed. Retry manually.]\n\n"

def build_full_book():
    os.makedirs("brain/manuscript", exist_ok=True)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(f"# {BOOK_TITLE}\n")
        f.write(f"### By {AUTHOR}\n")
        f.write(f"**Publishers:** {PUBLISHERS}\n\n")
        f.write("---\n\n")
    
    for sec in SECTIONS:
        section_content = generate_section(sec)
        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n\n{section_content}\n\n---\n")
        print(f"Successfully appended {sec['title']} to {OUTPUT_FILE}")
        time.sleep(2)
        
    print(f"\n🎉 6-CHAPTER BEST-SELLER MANUSCRIPT COMPLETE! Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    build_full_book()