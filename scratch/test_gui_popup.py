import tkinter as tk
import time

def on_allow():
    print("[SIMULATOR] 'Yes, allow this time' 버튼이 클릭되었습니다!")

def on_submit():
    print("[SIMULATOR] 'Submit' 버튼이 클릭되었습니다! 시뮬레이션을 종료합니다.")
    root.destroy()

root = tk.Tk()
root.title("Antigravity Approval Simulation Dialog")
root.geometry("400x200")

label = tk.Label(root, text="자동 승인 매크로(UIA) 동작 검증을 위한 가상 팝업창입니다.\n매크로가 정상 실행 중이라면 마우스 이동 없이\n버튼들이 자동 클릭되면서 이 창이 닫힙니다.", pady=20)
label.pack()

# UIA가 감지할 수 있도록 정확한 Name 텍스트를 버튼에 부여
btn_allow = tk.Button(root, text="Yes, allow this time", command=on_allow, width=20, height=2)
btn_allow.pack(pady=5)

btn_submit = tk.Button(root, text="Submit", command=on_submit, width=20, height=2)
btn_submit.pack(pady=5)

print("[SIMULATOR] 대기 중... 가상 팝업을 화면에 노출합니다.")
root.mainloop()
