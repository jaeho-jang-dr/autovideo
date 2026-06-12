import os
import shutil
import glob

def main():
    print("Backing up old hypnosis assets...")
    
    # Target directories
    vid_backup = "assets/videos_hypnosis"
    img_backup = "assets/images_hypnosis"
    
    os.makedirs(vid_backup, exist_ok=True)
    os.makedirs(img_backup, exist_ok=True)
    
    # Move videos
    videos = glob.glob("assets/videos/scene_*.mp4")
    for v in videos:
        basename = os.path.basename(v)
        dest = os.path.join(vid_backup, basename)
        print(f"Moving {v} -> {dest}")
        shutil.move(v, dest)
        
    # Move images
    images = glob.glob("assets/images/scene_*.png")
    for i in images:
        basename = os.path.basename(i)
        dest = os.path.join(img_backup, basename)
        print(f"Moving {i} -> {dest}")
        shutil.move(i, dest)
        
    print("Backup completed successfully!")

if __name__ == "__main__":
    main()
