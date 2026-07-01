import sqlite3
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HERE, '..', 'channel', 'content.db')
OUT_PATH = os.path.join(HERE, '..', 'peter_pan_prompts.txt')

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        for seq, img_p, veo_p in cur.execute('SELECT seq, image_prompt, veo_prompt FROM scenes WHERE episode="CA-001" ORDER BY seq'):
            f.write(f'[Scene {seq}] {img_p} {veo_p}\n')
    conn.close()
    print(f'[OK] Generated {OUT_PATH} from DB.')

if __name__ == '__main__':
    main()
