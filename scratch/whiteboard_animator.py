import os
import numpy as np
from moviepy import (
    ColorClip, ImageClip, CompositeVideoClip, VideoClip
)
from moviepy.video.fx import FadeIn, FadeOut

def create_whiteboard_background(duration, size=(1280, 720), color=(245, 245, 240)):
    """Creates a basic warm beige background clip."""
    # Convert rgb in 0-255 range to float 0.0-1.0 if moviepy expects it, 
    # but color expects 3-element tuple or list.
    return ColorClip(size=size, color=color).with_duration(duration)

def create_door_clip(duration, action_time, closed_path, open_path, pos=(900, 250)):
    """Switches from closed door to open door at action_time."""
    # closed_clip shown from 0 to action_time
    closed_clip = ImageClip(closed_path).with_duration(action_time).with_position(pos)
    
    # open_clip shown from action_time to duration
    open_clip = (ImageClip(open_path)
                 .with_duration(duration - action_time)
                 .with_start(action_time)
                 .with_position(pos))
                 
    return CompositeVideoClip([closed_clip, open_clip], size=(1280, 720))

def create_moving_stickman_clip(duration, stickman_path, start_x, end_x, y, fade_in_dur=1.0, fade_out_dur=1.0):
    """Stickman moves from start_x to end_x while fading in and out."""
    img_clip = ImageClip(stickman_path).with_duration(duration)
    
    # Position animation function
    def make_pos(t):
        if t <= 0:
            return (start_x, y)
        elif t >= duration:
            return (end_x, y)
        else:
            # Linear interpolation
            x = start_x + (end_x - start_x) * (t / duration)
            return (int(x), y)
            
    # Apply position and fade effects (v2.x effect syntax)
    stickman = img_clip.with_position(make_pos)
    
    # Apply fade in/out using moviepy v2.x effects
    if fade_in_dur > 0:
        stickman = stickman.with_effects([FadeIn(fade_in_dur, [245, 245, 240])])
    if fade_out_dur > 0:
        stickman = stickman.with_effects([FadeOut(fade_out_dur, [245, 245, 240])])
        
    return stickman

def create_writing_chalkboard_clip(text_path, duration, pencil_path, start_pos=(100, 200), size=(1280, 720)):
    """Renders a text Hangeul image with a sweep mask reveal effect and a pencil drawing it."""
    text_clip = ImageClip(text_path).with_duration(duration).with_position(start_pos)
    text_w, text_h = text_clip.size
    
    # Create a custom mask that reveals the text from left to right
    # MoviePy v2.x uses numpy frames.
    def make_mask_frame(t):
        # Create a mask frame of size (text_h, text_w)
        # 1.0 means visible, 0.0 means hidden
        mask = np.zeros((text_h, text_w), dtype=np.float32)
        progress = t / duration
        reveal_width = int(text_w * progress)
        if reveal_width > 0:
            mask[:, :reveal_width] = 1.0
        return mask
        
    # Create mask clip and set it to the text clip
    mask_clip = VideoClip(make_mask_frame, is_mask=True).with_duration(duration)
    text_clip = text_clip.with_mask(mask_clip)
    
    # Pencil animation clip to follow the reveal boundary
    pencil_clip = ImageClip(pencil_path).with_duration(duration)
    pencil_w, pencil_h = pencil_clip.size
    
    def make_pencil_pos(t):
        progress = t / duration
        # Pencil tip follows the reveal boundary (right edge of revealed text)
        pencil_tip_x = start_pos[0] + text_w * progress
        # Add a tiny wobble to simulate drawing oscillation
        pencil_tip_y = start_pos[1] + text_h / 2 + 10 * np.sin(2 * np.pi * 5 * t)
        
        # Position is relative to top-left of the pencil image
        # Assume pencil drawing end is bottom-left (pencil_w/2, pencil_h)
        return (int(pencil_tip_x - pencil_w/2), int(pencil_tip_y - pencil_h))
        
    pencil = pencil_clip.with_position(make_pencil_pos)
    
    return CompositeVideoClip([text_clip, pencil], size=size)

def create_checkmark_clip(pos, duration, start_time, checkmark_path="assets/graphics/effect_checkmark.png"):
    """Creates a checkmark clip that draws/reveals itself at start_time."""
    check = ImageClip(checkmark_path).with_duration(duration - start_time).with_start(start_time)
    check = check.resized(width=120) # Compact check badge size to fit canvas
    check = check.with_position(pos)
    check_w, check_h = check.size
    
    # Reveal checkmark from left-to-right (Wipe mask)
    def make_mask(t):
        mask = np.zeros((check_h, check_w), dtype=np.float32)
        progress = min(1.0, max(0.0, t / 0.4)) # Complete wipe in 0.4s
        reveal = min(check_w, max(0, int(check_w * progress)))
        if reveal > 0:
            mask[:, :reveal] = 1.0
        return mask
        
    mask_clip = VideoClip(make_mask, is_mask=True).with_duration(duration - start_time)
    return check.with_mask(mask_clip)

def create_underline_clip(target_pos, target_width, duration, start_time, underline_path="assets/graphics/effect_underline.png"):
    """Creates a gold underline clip that draws itself under text."""
    line = ImageClip(underline_path).with_duration(duration - start_time).with_start(start_time)
    
    # Resize underline width to match target_width, keeping thickness
    line = line.resized(width=target_width)
    line = line.with_position(target_pos)
    line_w, line_h = line.size
    
    # Wipe reveal under text
    def make_mask(t):
        mask = np.zeros((line_h, line_w), dtype=np.float32)
        progress = min(1.0, max(0.0, t / 0.4)) # Wipe in 0.4s
        reveal = min(line_w, max(0, int(line_w * progress)))
        if reveal > 0:
            mask[:, :reveal] = 1.0
        return mask
        
    mask_clip = VideoClip(make_mask, is_mask=True).with_duration(duration - start_time)
    return line.with_mask(mask_clip)

def create_number_badge_clip(number_str, pos, duration, start_time):
    """Creates a number badge (1, 2, or 3) clip that pops in with elastic bounce scaling."""
    badge_path = f"assets/graphics/badge_{number_str}.png"
    badge = ImageClip(badge_path).with_duration(duration - start_time).with_start(start_time)
    badge_w, badge_h = badge.size
    
    # Custom VideoClip to handle Pillow-based elastic resize frame by frame
    from PIL import Image
    base_img = Image.open(badge_path).convert("RGBA")
    
    def make_badge_frame(t):
        # Elastic bounce formula
        p = t / 0.5 # pop-in finishes in 0.5s
        if p >= 1.0:
            scale = 1.0
        else:
            # Dampened cosine wave for spring effect: 0 -> 1.2 -> 1.0
            scale = 1.0 - np.exp(-6.0 * p) * np.cos(2.0 * np.pi * 1.5 * p)
            
        scale = max(0.01, min(1.5, scale))
        new_w = max(1, min(badge_w, int(badge_w * scale)))
        new_h = max(1, min(badge_h, int(badge_h * scale)))
        
        # Resize Pillow image
        resized_img = base_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Center resized image in a canvas of original size to maintain position anchor
        canvas = Image.new("RGBA", (badge_w, badge_h), (0, 0, 0, 0))
        offset_x = (badge_w - new_w) // 2
        offset_y = (badge_h - new_h) // 2
        canvas.paste(resized_img, (offset_x, offset_y))
        
        return np.array(canvas)[:, :, :3] # Return RGB
        
    def make_badge_mask(t):
        p = t / 0.5
        scale = 1.0 if p >= 1.0 else 1.0 - np.exp(-6.0 * p) * np.cos(2.0 * np.pi * 1.5 * p)
        scale = max(0.01, min(1.5, scale))
        new_w = max(1, min(badge_w, int(badge_w * scale)))
        new_h = max(1, min(badge_h, int(badge_h * scale)))
        
        resized_mask = Image.open(badge_path).convert("RGBA").split()[3].resize((new_w, new_h), Image.Resampling.LANCZOS)
        canvas = Image.new("L", (badge_w, badge_h), 0)
        offset_x = (badge_w - new_w) // 2
        offset_y = (badge_h - new_h) // 2
        canvas.paste(resized_mask, (offset_x, offset_y))
        
        return np.array(canvas).astype(np.float32) / 255.0
        
    # Build badge video clip from custom frame generators
    badge_pop = VideoClip(make_badge_frame).with_duration(duration - start_time)
    badge_mask = VideoClip(make_badge_mask, is_mask=True).with_duration(duration - start_time)
    
    return badge_pop.with_mask(badge_mask).with_position(pos).with_start(start_time)

def create_extreme_close_up_writing_clip(text_path, duration, target_pos=(200, 150), tool_type="pencil", size=(1280, 720)):
    """Creates a close-up writing scene with micro camera jitter and falling powder/chalk particles."""
    # 1. Background blackboard or notebook zoomed in
    if tool_type == "pencil":
        base_bg = create_whiteboard_background(duration, size=size, color=(245, 245, 240))
        notebook_img = ImageClip("assets/graphics/obj_notebook.png").with_duration(duration).resized(new_size=size)
        bg = CompositeVideoClip([base_bg, notebook_img.with_position(("center", "center"))], size=size)
    else:
        bg = ImageClip("assets/graphics/obj_blackboard.png").with_duration(duration).resized(new_size=size)
    
    # 2. Text image scaled up (3x) for close-up view
    text_clip = ImageClip(text_path).with_duration(duration)
    orig_w, orig_h = text_clip.size
    text_clip = text_clip.resized(width=orig_w * 3)
    text_w, text_h = text_clip.size
    
    # Position text at target_pos
    text_clip = text_clip.with_position(target_pos)
    
    # Text mask reveal (3-stage stroke-by-stroke writing path: Chosung -> Jungseung -> Jongsung)
    def make_mask(t):
        mask = np.zeros((text_h, text_w), dtype=np.float32)
        progress = min(1.0, max(0.0, t / duration))
        
        # Stage 1: Chosung 'ㄱ' (y in [0, 0.35 * text_h]) reveals in first 33% of time
        if progress < 0.33:
            p1 = progress / 0.33
            reveal1 = int(text_w * p1)
            if reveal1 > 0:
                mask[:int(0.35 * text_h), :reveal1] = 1.0
        # Stage 2: Jungseung 'ㅡ' (y in [0.35 * text_h, 0.55 * text_h]) reveals in middle 33% of time
        elif progress < 0.66:
            mask[:int(0.35 * text_h), :] = 1.0 # Chosung fully revealed
            p2 = (progress - 0.33) / 0.33
            reveal2 = int(text_w * p2)
            if reveal2 > 0:
                mask[int(0.35 * text_h):int(0.55 * text_h), :reveal2] = 1.0
        # Stage 3: Jongsung 'ㄹ' (y in [0.55 * text_h, text_h]) reveals in final 34% of time
        else:
            mask[:int(0.55 * text_h), :] = 1.0 # Chosung & Jungseung fully revealed
            p3 = (progress - 0.66) / 0.34
            reveal3 = int(text_w * p3)
            if reveal3 > 0:
                mask[int(0.55 * text_h):, :reveal3] = 1.0
        return mask
        
    mask_clip = VideoClip(make_mask, is_mask=True).with_duration(duration)
    text_clip = text_clip.with_mask(mask_clip)
    
    # 3. Tool clip (pencil or chalk)
    tool_path = "assets/graphics/obj_pencil.png" if tool_type == "pencil" else "assets/graphics/obj_chalk.png"
    tool_clip = ImageClip(tool_path).with_duration(duration)
    tool_w, tool_h = tool_clip.size
    
    # 4. Particles (chalk dust or graphite powder) falling down
    particle_path = "assets/graphics/obj_particle.png"
    
    # Custom position tracking for tool and micro-jitter camera offset
    clips_list = [bg, text_clip]
    
    # Render multiple particles periodically (every 0.2s)
    num_particles = int(duration / 0.2)
    for i in range(num_particles):
        p_start = i * 0.2
        if p_start >= duration - 0.3:
            continue
            
        p_dur = min(0.4, duration - p_start)
        
        # Calculate birth coordinate matching tool position at p_start
        progress = p_start / duration
        if progress < 0.33:
            p1 = progress / 0.33
            birth_x = target_pos[0] + text_w * p1
            birth_y = target_pos[1] + int(0.18 * text_h)
        elif progress < 0.66:
            p2 = (progress - 0.33) / 0.33
            birth_x = target_pos[0] + text_w * p2
            birth_y = target_pos[1] + int(0.45 * text_h)
        else:
            p3 = (progress - 0.66) / 0.34
            birth_x = target_pos[0] + text_w * p3
            birth_y = target_pos[1] + int(0.78 * text_h)
        
        # Gravity falling physics function for particle
        def make_particle_pos(t):
            # t goes from 0 to p_dur
            x_offset = 15 * np.sin(2 * np.pi * 3 * t) # sway left-right
            y_fall = 250 * (t ** 2) # gravity acceleration
            cur_x = max(-100, min(1280, birth_x + x_offset))
            cur_y = max(-100, min(720, birth_y + y_fall))
            return (int(cur_x), int(cur_y))
            
        part = (ImageClip(particle_path)
                .with_duration(p_dur)
                .with_start(p_start)
                .with_position(make_particle_pos))
                
        # Chalk particles are white, graphite is black. 
        # For chalk, invert particle colors or keep it (process_lineart made it transparent outline, which works)
        if tool_type == "chalk":
            # Just tint the particle or keep it, the gray/black fits okay, but we can keep it as is
            pass
            
        clips_list.append(part)
        
    # Tool position function matching active stroke
    def make_tool_pos(t):
        progress = min(1.0, max(0.0, t / duration))
        wobble = 15 * np.sin(2 * np.pi * 6 * t)
        
        if progress < 0.33:
            p1 = progress / 0.33
            tip_x = target_pos[0] + text_w * p1
            tip_y = target_pos[1] + int(0.18 * text_h) + wobble
        elif progress < 0.66:
            p2 = (progress - 0.33) / 0.33
            tip_x = target_pos[0] + text_w * p2
            tip_y = target_pos[1] + int(0.45 * text_h) + wobble
        else:
            p3 = (progress - 0.66) / 0.34
            tip_x = target_pos[0] + text_w * p3
            tip_y = target_pos[1] + int(0.78 * text_h) + wobble
            
        cur_x = max(-tool_w, min(1280, tip_x - tool_w/2))
        cur_y = max(-tool_h, min(720, tip_y - tool_h))
        return (int(cur_x), int(cur_y))
        
    tool = tool_clip.with_position(make_tool_pos)
    clips_list.append(tool)
    
    # 5. Composite all elements with high-frequency micro camera shake (Jitter)
    composite_base = CompositeVideoClip(clips_list, size=size)
    
    # Micro Jitter wrapper (wobble entire frame by 2px)
    def make_jitter_offset(t):
        jx = int(2.5 * np.sin(2 * np.pi * 15 * t))
        jy = int(2.5 * np.cos(2 * np.pi * 15 * t))
        return (jx, jy)
        
    # Wrap in a larger canvas and crop to center with jitter offsets
    # For MoviePy 2.x, we can simply apply the jitter offset directly as a position function of the composite clip inside a background
    final_jitter = CompositeVideoClip([composite_base.with_position(make_jitter_offset)], size=size)
    
    return final_jitter

if __name__ == "__main__":
    print("Whiteboard animator helper library compiled successfully.")
