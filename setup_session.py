import asyncio
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# Load environment variables
load_dotenv()

SESSION_DIR = os.path.join(os.getcwd(), 'naukri_session')
EMAIL = os.getenv('NAUKRI_EMAIL')
PASSWORD = os.getenv('NAUKRI_PASSWORD')

async def main():
    print(f"Creating/using session directory at: {SESSION_DIR}")
    print("A browser window will open. We will attempt to auto-fill your credentials.")
    print("Please solve any Captchas, complete the login, and then close the browser window to save the session.")
    
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=SESSION_DIR,
            headless=False,
            viewport={'width': 1280, 'height': 720},
            args=['--disable-blink-features=AutomationControlled']
        )
        
        page = context.pages[0]
        await page.goto('https://www.naukri.com/nlogin/login')
        
        try:
            # Auto-fill credentials if they exist
            if EMAIL and PASSWORD:
                print("Auto-filling credentials...")
                
                # Wait for username field and fill it
                username_selector = '#usernameField'
                await page.wait_for_selector(username_selector, timeout=5000)
                await page.fill(username_selector, EMAIL)
                await asyncio.sleep(1) # Small human-like delay
                
                # Wait for password field and fill it
                password_selector = '#passwordField'
                await page.wait_for_selector(password_selector, timeout=5000)
                await page.fill(password_selector, PASSWORD)
                print("Credentials filled. Please verify and click 'Login'.")
            else:
                print("No credentials found in .env. Please fill them manually.")
        except Exception as e:
            print(f"Could not auto-fill credentials: {e}")
            print("Please enter them manually.")
            
        try:
            # Keep browser open until closed by user
            await page.wait_for_event('close', timeout=0)
        except Exception:
            pass
            
        print("Session saved successfully. You can now run naukri_bot.py")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSession setup stopped.")
