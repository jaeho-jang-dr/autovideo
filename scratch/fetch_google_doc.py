import sys
import os
from playwright.sync_api import sync_playwright

def main():
    url = "https://docs.google.com/document/d/10BeRAjYtmOB0_Cbq5If25h1qwRoNRi0te8wdHIob-wo/edit?usp=sharing"
    dest_file = r"d:\Entertainments\DevEnvironment\autovideo\scratch\cleaned_google_doc.txt"
    
    print(f"Launching Playwright to fetch: {url}")
    with sync_playwright() as p:
        # Launch headless browser with a viewport size
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 1024})
        page = context.new_page()
        
        # Navigate to url
        page.goto(url, timeout=60000)
        
        print("Waiting for kix-paragraphrenderer elements...")
        # Google Docs renders its content asynchronously. Let's wait for paragraphs.
        try:
            page.wait_for_selector('.kix-paragraphrenderer', timeout=25000)
            print("Successfully found paragraph elements.")
        except Exception as e:
            print(f"Failed to find specific elements: {e}. Checking standard selectors...")
            
        # Give it a couple more seconds to render all pages
        page.wait_for_timeout(5000)
        
        # Scroll down to trigger lazy loading of pages in google docs
        for _ in range(5):
            page.mouse.wheel(0, 1500)
            page.wait_for_timeout(500)
            
        paragraphs = page.locator(".kix-paragraphrenderer")
        p_count = paragraphs.count()
        print(f"Number of paragraph elements found: {p_count}")
        
        if p_count > 0:
            text_list = []
            for i in range(p_count):
                txt = paragraphs.nth(i).inner_text()
                if txt.strip():
                    text_list.append(txt)
            text = "\n\n".join(text_list)
        else:
            print("Falling back to full body inner_text...")
            text = page.locator("body").inner_text()
            
        # Save to file
        with open(dest_file, "w", encoding="utf-8") as f:
            f.write(text)
            
        print(f"Content successfully saved to: {dest_file}")
        print(f"Total characters fetched: {len(text)}")
        browser.close()

if __name__ == "__main__":
    main()
