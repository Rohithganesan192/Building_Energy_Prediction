import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1280, 'height': 900})
        
        print("Navigating to app...")
        await page.goto('http://localhost:5173/')
        
        print("Logging in...")
        await page.wait_for_selector('input[type="text"]')
        await page.fill('input[type="text"]', 'admin')
        await page.fill('input[type="password"]', 'demo123')
        await page.click('button[type="submit"]')
        
        print("Waiting for dashboard to load...")
        await page.wait_for_selector('text=Overview')
        
        print("Navigating to Buildings to find Building 565...")
        await page.goto('http://localhost:5173/buildings')
        await page.wait_for_selector('input[type="text"]')
        
        # We know building 565 is education
        await page.fill('input[type="text"]', '565')
        await page.wait_for_timeout(1000)
        
        # Click the building row
        await page.click('text=ID 565')
        
        # Click "Use for Prediction"
        await page.click('button:has-text("Use for Prediction")')
        
        print("In Predict page, clicking Generate Prediction...")
        await page.wait_for_selector('text=Generate Prediction')
        await page.click('button:has-text("Generate Prediction")')
        
        # Wait for result to appear
        await page.wait_for_selector('text=Predicted Energy')
        await page.wait_for_timeout(1000)
        
        # Take screenshot of Predict
        await page.screenshot(path=r'c:\Users\ROHITHGANESAN G\Building_Energy_Prediction\reports\figures\predict_auth.png', full_page=True)
        print("Predict snapshot saved.")
        
        # Go to Explain
        await page.click('button:has-text("Explain Prediction")')
        await page.wait_for_selector('text=Explainable Model Intelligence')
        await page.wait_for_timeout(2000)
        
        # Take screenshot of Explain
        await page.screenshot(path=r'c:\Users\ROHITHGANESAN G\Building_Energy_Prediction\reports\figures\explain_auth.png', full_page=True)
        print("Explain snapshot saved.")
        
        await browser.close()
        print("E2E Test Passed!")

if __name__ == '__main__':
    asyncio.run(main())
