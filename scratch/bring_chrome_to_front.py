import uiautomation as auto
import sys

print("Searching for Chrome window via UI Automation...")

# Find the main Chrome window (ClassName for Chrome is 'Chrome_WidgetWin_1')
chrome_window = auto.WindowControl(searchDepth=1, ClassName='Chrome_WidgetWin_1')

if chrome_window.Exists(maxSearchSeconds=5):
    title = chrome_window.Name
    print(f"Found Chrome window: Title='{title}'")
    
    # 9 is SW_RESTORE (restores window size and position), 5 is SW_SHOW, 3 is SW_MAXIMIZE
    chrome_window.ShowWindow(9) 
    chrome_window.SetActive()
    chrome_window.SetFocus()
    print("Successfully brought the Chrome window to the foreground.")
else:
    print("Chrome window (ClassName='Chrome_WidgetWin_1') was not found in UI Automation.")
