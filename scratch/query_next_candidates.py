import sqlite3

def main():
    conn = sqlite3.connect('channel/content.db')
    cur = conn.cursor()
    
    # Select Priority 1 episodes with status 'idea'
    cur.execute("""
        SELECT code, category, title_kr, title_en, logline_kr 
        FROM episodes 
        WHERE status='idea' AND priority=1;
    """)
    rows = cur.fetchall()
    
    with open("scratch/candidates_utf8.txt", "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("  다음 제작 후보 에피소드 (우선순위 1순위 / 기획 단계)\n")
        f.write("=" * 80 + "\n")
        for row in rows:
            code, category, title_kr, title_en, logline_kr = row
            f.write(f"코드: {code}\n")
            f.write(f"카테고리: {category}\n")
            f.write(f"제목 (한글): {title_kr}\n")
            f.write(f"제목 (영어): {title_en}\n")
            f.write(f"로그라인 (설명): {logline_kr}\n")
            f.write("-" * 50 + "\n")
            
    conn.close()
    print("Exported next candidates to scratch/candidates_utf8.txt")

if __name__ == "__main__":
    main()
