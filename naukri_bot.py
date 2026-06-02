import asyncio
import os
import random
from dotenv import load_dotenv
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# Load environment variables
load_dotenv()

# ================= CONFIGURATION =================
SEARCH_KEYWORD = "Full Stack Developer"
EXPERIENCE_YEARS = 0 # 0 means Fresher
MAX_PAGES = 5 # Number of pages to scan and apply
SESSION_DIR = os.path.join(os.getcwd(), 'naukri_session')
EMAIL = os.getenv('NAUKRI_EMAIL')
PASSWORD = os.getenv('NAUKRI_PASSWORD')
# =================================================

async def random_delay(min_seconds=2, max_seconds=5):
    """Wait for a random amount of time to mimic human behavior and avoid bot detection."""
    await asyncio.sleep(random.uniform(min_seconds, max_seconds))

async def apply_to_job(context, card, job_index):
    """Opens a job card, checks the apply status, and attempts to apply."""
    try:
        title_element = card.locator('.title')
        if await title_element.count() == 0:
            return False
            
        title = await title_element.inner_text()
        
        # Check if company name is available
        company = "Unknown Company"
        comp_element = card.locator('.comp-name')
        if await comp_element.count() > 0:
            company = await comp_element.inner_text()

        print(f"\n[{job_index}] Checking: '{title}' at '{company}'")

        # Click the job title to open in a new tab/page
        async with context.expect_page() as new_page_info:
            await title_element.click()
            
        job_page = await new_page_info.value
        await job_page.wait_for_load_state('domcontentloaded')
        await random_delay(2, 4)

        # Check if already applied
        # Sometimes Naukri shows "Applied" or "Already Applied" on the button
        page_content = await job_page.content()
        
        # Detect typical apply buttons
        # 1. Primary Apply button
        apply_btn = job_page.locator('button.apply-button')
        
        # 2. Secondary apply button selectors (sometimes Naukri uses ID or text)
        if await apply_btn.count() == 0:
            apply_btn = job_page.get_by_role("button", name="Apply", exact=True)
            
        if await apply_btn.count() == 0:
            apply_btn = job_page.locator('#apply-button')

        # Check if button contains text like "applied"
        if await apply_btn.count() > 0:
            btn_text = (await apply_btn.first.inner_text()).lower()
            if "applied" in btn_text:
                print("  -> Already applied. Skipping.")
                await job_page.close()
                return False
                
            print("  -> Found Apply button. Clicking...")
            await apply_btn.first.click()
            await random_delay(3, 5)
            
            # Check if there is a chatbot or questionnaire pop-up
            # Chatbot elements usually contain classes like 'chatbot', 'chat', 'screener'
            # We will wait a moment to see if any popup overlay or iframe appears
            popup_indicators = [
                "div[class*='chatbot']", 
                "div[class*='screener']", 
                "iframe[src*='chatbot']",
                ".chatbot-container",
                ".screener-questions"
            ]
            
            has_popup = False
            for selector in popup_indicators:
                if await job_page.locator(selector).count() > 0:
                    has_popup = True
                    break
                    
            if has_popup:
                print("  -> WARNING: A questionnaire/chatbot popped up. Please complete it manually in the browser if needed.")
                # We leave the page open for a bit longer so the user can look, or we just close it and let the user handle it
                # For safety, we keep it open for 15 seconds to let the user see it, or close and skip
                await asyncio.sleep(5)
            else:
                print("  -> Successfully applied (no popup detected)!")
                
            await job_page.close()
            return True
        else:
            # Check if it has "Apply on company site"
            company_site_btn = job_page.get_by_role("button", name="Apply on company site", exact=False)
            if await company_site_btn.count() > 0:
                print("  -> Redirects to external company site. Skipping (Easy Apply only).")
            else:
                print("  -> No standard Apply button found (might be already applied or external site). Skipping.")
                
            await job_page.close()
            return False

    except Exception as e:
        print(f"  -> Error applying to job: {e}")
        # Make sure we close the tab if it got stuck open
        if len(context.pages) > 1:
            await context.pages[-1].close()
        return False

async def close_modals_if_any(page):
    """Detects and closes any popup modals or notification overlays."""
    print("Checking for popups or modals...")
    # Common selectors for close buttons/actions on Naukri
    modal_selectors = [
        '.crossIcon',           # Standard Naukri drawer/popup close button
        'span.cross',           # Cross icon span
        '.close-icon',          # Close icon
        'span.close',           # Close text/span
        '.close',               # Generic close class
        'text=Skip',            # Skip links/buttons
        'text=Later',           # "Later" or "Maybe Later" buttons
        'text=Remind me later'  # Onboarding/profile update remind buttons
    ]
    
    for selector in modal_selectors:
        try:
            element = page.locator(selector)
            if await element.count() > 0 and await element.first.is_visible():
                print(f"  -> Found modal element matching: '{selector}'. Clicking to close...")
                await element.first.click()
                await random_delay(1, 2)
        except Exception:
            pass

async def main():
    if not os.path.exists(SESSION_DIR):
        print("Session directory not found! Creating a new one...")
        os.makedirs(SESSION_DIR, exist_ok=True)

    async with async_playwright() as p:
        print("Launching browser with session...")
        context = await p.chromium.launch_persistent_context(
            user_data_dir=SESSION_DIR,
            headless=False, # Keep False so you can see what it's doing
            viewport={'width': 1280, 'height': 720},
            args=['--disable-blink-features=AutomationControlled']
        )
        
        page = context.pages[0]
        
        # Navigate to home page to check login state
        print("Checking login state...")
        await page.goto('https://www.naukri.com/')
        await page.wait_for_load_state('domcontentloaded')
        await random_delay(2, 4)
        
        # Check if we need to log in (if we see a login button)
        login_btn_selector = '#login_Layer' # Common Naukri login link/button ID
        is_logged_in = True
        
        # If login button is visible, we are not logged in
        try:
            login_btn = page.locator(login_btn_selector)
            if await login_btn.count() > 0 and await login_btn.is_visible():
                is_logged_in = False
        except Exception:
            is_logged_in = False

        if not is_logged_in:
            print("Not logged in. Directing to login page...")
            await page.goto('https://www.naukri.com/nlogin/login')
            await page.wait_for_load_state('domcontentloaded')
            await random_delay(2, 3)
            
            if EMAIL and PASSWORD:
                print("Logging in with saved credentials...")
                try:
                    await page.fill('#usernameField', EMAIL)
                    await random_delay(1, 2)
                    await page.fill('#passwordField', PASSWORD)
                    await random_delay(1, 2)
                    
                    # Click the Login button
                    # Naukri uses a button with type="submit" inside login-form or class "login-btn"
                    login_submit = page.locator('button[type="submit"]')
                    if await login_submit.count() > 0:
                        await login_submit.first.click()
                    else:
                        await page.get_by_role("button", name="Login").click()
                        
                    print("Clicked login. Waiting for navigation/dashboard...")
                    await page.wait_for_load_state('domcontentloaded')
                    await random_delay(3, 5)
                except Exception as e:
                    print(f"Error during automated login: {e}")
                    print("Please log in manually now in the browser window.")
            else:
                print("No credentials found in .env! Please log in manually now in the browser window.")
            
            # Pause a little to let any redirect or 2FA/Captcha be completed if needed
            print("Waiting for page load after login...")
            await page.wait_for_load_state('domcontentloaded')
            await random_delay(3, 5)

        # Close any welcome modals, onboarding popups, or updates drawer
        await close_modals_if_any(page)
        
        # Navigate to homepage to ensure we see the dashboard search box
        print("Navigating to home/dashboard...")
        await page.goto('https://www.naukri.com/')
        await page.wait_for_load_state('domcontentloaded')
        await random_delay(2, 4)
        await close_modals_if_any(page)

        # Search using the search box shown in the image
        print("Searching via the search box...")
        try:
            # Look for the input with placeholder "Search jobs here"
            search_input = page.locator('input[placeholder="Search jobs here"]')
            if await search_input.count() == 0:
                # Alternate selector: class suggestor-input
                search_input = page.locator('.suggestor-input').first

            # Use focus() and force-click to bypass pointer interception by wrapper elements
            await search_input.focus()
            await search_input.click(force=True)
            await random_delay(1, 2)
            
            # Type the keyword + fresher
            search_query = f"{SEARCH_KEYWORD} fresher"
            await search_input.fill(search_query)
            await random_delay(1, 2)
            
            # Press Enter to perform search
            await search_input.press('Enter')
            print("Pressed Enter to search.")
        except Exception as e:
            print(f"Error searching via search box: {e}")
            # Fallback to direct search URL if something goes wrong
            print("Falling back to direct search URL...")
            keyword_url_part = SEARCH_KEYWORD.lower().replace(" ", "-")
            await page.goto(f"https://www.naukri.com/{keyword_url_part}-jobs?experience={EXPERIENCE_YEARS}")
            
        await page.wait_for_load_state('domcontentloaded')
        await random_delay(4, 6)
        
        for page_num in range(1, MAX_PAGES + 1):
            if page.is_closed():
                print("Browser window closed. Stopping bot.")
                break
                
            print(f"\n=================== SCANNING PAGE {page_num} ===================")
            
            # Again, close modals if they block search page
            await close_modals_if_any(page)
            
            # Find all job cards on the page
            job_cards = page.locator('.srp-jobtuple-wrapper')
            count = await job_cards.count()
            print(f"Found {count} jobs on page {page_num}.")
            
            if count == 0:
                print("No jobs found on this page. Stopping.")
                break
                
            for i in range(count):
                if page.is_closed():
                    print("Browser window closed during loop. Stopping.")
                    break
                    
                card = job_cards.nth(i)
                # Apply to job
                applied = await apply_to_job(context, card, i + 1)
                if applied:
                    # Delay between applications
                    await random_delay(4, 8)
                else:
                    await random_delay(1, 3)
            
            if page.is_closed():
                print("Browser window closed. Stopping.")
                break
                
            # If we want to go to the next page
            if page_num < MAX_PAGES:
                print("Attempting to navigate to the next page...")
                next_btn = page.locator("a:has-text('Next')")
                if await next_btn.count() == 0:
                    next_btn = page.get_by_role("link", name="Next")
                
                if await next_btn.count() > 0 and await next_btn.first.is_visible():
                    print("Clicking 'Next' button...")
                    await next_btn.first.click()
                    await page.wait_for_load_state('domcontentloaded')
                    await random_delay(4, 7)
                else:
                    print("No 'Next' button found. Stopping.")
                    break
                    
        print("\nAll pages processed successfully.")
        if not page.is_closed():
            await context.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user.")
