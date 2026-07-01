import sqlite3

def main():
    conn = sqlite3.connect('channel/content.db')
    cur = conn.cursor()
    
    cur.execute("SELECT code, category, title_kr, title_en, status, priority FROM episodes;")
    rows = cur.fetchall()
    
    with open("scratch/episodes_utf8.txt", "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("  drjay-ed 에피소드 목록 및 상태 (UTF-8)\n")
        f.write("=" * 80 + "\n")
        for row in rows:
            code, category, title_kr, title_en, status, priority = row
            f.write(f"Code: {code:<8} | Category: {category:<5} | Title(KR): {title_kr:<35} | Status: {status:<10} | Priority: {priority}\n")
            
        f.write("\n" + "=" * 80 + "\n")
        f.write("  모든 에피소드의 데이터베이스 씬(Scene) 개수 현황\n")
        f.write("=" * 80 + "\n")
        
        # Check all unique episodes in scenes table
        cur.execute("SELECT episode, COUNT(*) FROM scenes GROUP BY episode;")
        scene_counts = cur.fetchall()
        for ep_code, count in scene_counts:
            f.write(f"에피소드 코드: {ep_code:<10} | 등록된 씬 개수: {count}개\n")
            
    conn.close()
    print("Exported info to scratch/episodes_utf8.txt")

if __name__ == "__main__":
    main()
