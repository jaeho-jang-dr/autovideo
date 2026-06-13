import uiautomation as auto

def test_find_windows():
    root = auto.GetRootControl()
    print("Listing all top-level windows:")
    for w in root.GetChildren():
        try:
            print(f"Name: '{w.Name}', ClassName: '{w.ClassName}', ProcessId: {w.ProcessId}")
        except Exception as e:
            pass

if __name__ == "__main__":
    test_find_windows()
