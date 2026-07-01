import os
import re

def main():
    scenario_path = 'child_growth_science/scenario.txt'
    prompts_path = 'child_growth_science/child_growth_prompts.txt'

    if not os.path.exists(scenario_path):
        print(f"Error: {scenario_path} not found")
        return

    # Visual enhancement mapping dictionary
    visual_map = {
        0: (
            'TED-Ed style flat crayon illustration of a title slide with very large, bold, clean lettering reading "How Tall Will I Grow?", centered on a simple solid cream-colored textured paper background, soft colored pencil border. Minimalist design, high contrast, clean typography. No watermark, no signatures.',
            ':: slow motion yellow and orange highlights trace the title text on the card, camera zooming in slowly'
        ),
        2: (
            'TED-Ed style flat crayon illustration of a child\'s skeletal hand wrist X-ray highlighting open growth plates (soft blue cartilage zones), soft pastel green background. No watermark, no signatures.',
            ':: slow motion the soft blue cartilage zones glow gently, camera tilting down'
        ),
        3: (
            'TED-Ed style flat crayon illustration of a clean medical diagram of a DNA double-helix showing genetic base pairs, soft lavender background, crayon texture. No watermark, no signatures.',
            ':: slow motion the DNA double-helix rotates slowly along its vertical axis, camera panning up'
        ),
        5: (
            'TED-Ed style flat crayon illustration of a clean blackboard showing mathematical formulas: "Mid-Parental Height (MPH) Formula" with "Boys = (Father + Mother + 13)/2" and "Girls = (Father + Mother - 13)/2" written in white chalk, soft pastel cream background.',
            ':: slow motion chalk formulas shine with a soft glow, camera rotating slowly'
        ),
        6: (
            'TED-Ed style flat crayon illustration of a boy sprout standing next to a large vertical ruler marked with height centimeter metrics, soft pastel blue background. No watermark, no signatures.',
            ':: slow motion the height metrics on the ruler highlight in blue, camera panning up slowly'
        ),
        7: (
            'TED-Ed style flat crayon illustration of a girl sprout standing next to a vertical growth chart ruler with centimeter markings, soft pastel coral background. No watermark, no signatures.',
            ':: slow motion the centimeter markings glow softly, camera panning up slowly'
        ),
        9: (
            'TED-Ed style flat crayon illustration of a clean bar chart showing "Genetics: 70-80%" and "Environment: 20-30%" in distinct colorful bars, soft lavender background, crayon texture.',
            ':: slow motion the bar heights adjust slightly with warm light pulses, camera tilting down'
        ),
        10: (
            'TED-Ed style flat crayon illustration of icons representing Sleep (crescent moon), Nutrition (vitamin block), and Exercise (running shoe) watering a growing seed, soft yellow background. No watermark, no signatures.',
            ':: slow motion warm droplets fall onto the seed from the icons, camera zooming in'
        ),
        11: (
            'TED-Ed style flat crayon illustration of a detailed cutaway of a leg bone joint showing the epiphyseal plate (growth plate) as a soft blue cartilage zone, soft mint background.',
            ':: slow motion the epiphyseal cartilage zone pulses with a soft orange light, camera rotating slowly'
        ),
        12: (
            'TED-Ed style flat crayon illustration of a microscope view of chondrocytes (cartilage cells) stacked in organized columns within the bone plate, soft pastel teal background.',
            ':: slow motion the stacked chondrocyte layers expand slightly, camera zooming out slowly'
        ),
        13: (
            'TED-Ed style flat crayon illustration of a micro-scale view of cartilage cells actively dividing and multiplying under a soft warm spotlight, soft yellow background.',
            ':: slow motion the cells divide and multiply in warm golden light, camera panning right'
        ),
        14: (
            'TED-Ed style flat crayon illustration of soft cartilage cell columns calcifying and transforming into hard white bone tissue from bottom to top, soft cream background.',
            ':: slow motion the cells calcify into solid bone texture, camera zooming in'
        ),
        15: (
            'TED-Ed style flat crayon illustration of sex hormones like estrogen and testosterone molecules entering a bone joint, soft pastel coral background.',
            ':: slow motion the hormone molecules drift into the cartilage plate, camera tilting slowly up'
        ),
        16: (
            'TED-Ed style flat crayon illustration of the growth plate completely fused and ossified into a thin solid white line, soft lavender background.',
            ':: slow motion the solid fused line glows with a warm light, camera rotating slowly'
        ),
        17: (
            'TED-Ed style flat crayon illustration of a side-by-side comparison of a wrist X-ray showing growth plates vs a ticking clock, soft warm cream background.',
            ':: slow motion the wrist bones in the X-ray glow softly, camera zooming in slowly'
        ),
        18: (
            'TED-Ed style flat crayon illustration of a pediatric hand-wrist X-ray diagram showing carpal bones and distal radius growth plates, soft blue background.',
            ':: slow motion the wrist bones pulse with gentle golden highlights, camera panning down slowly'
        ),
        19: (
            'TED-Ed style flat crayon illustration of a medical book showing hand bone maturation charts side-by-side with a slide comparison, soft green background.',
            ':: slow motion pages of the book turn slowly, revealing different hand charts, camera rotating slowly'
        ),
        20: (
            'TED-Ed style flat crayon illustration of two charts labeled "Greulich-Pyle Atlas" and "Tanner-Whitehouse Score" under a soft examination light, soft yellow background.',
            ':: slow motion the light moves across the charts, camera zooming out slowly'
        ),
        21: (
            'TED-Ed style flat crayon illustration of two clocks side by side, one labeled "Chronological Age" and the other "Bone Age", soft pastel coral background.',
            ':: slow motion the hands of the Bone Age clock spin at a different rate, camera panning left'
        ),
        26: (
            'TED-Ed style flat crayon illustration of a timeline chart with flat lines suddenly spiking into high waves, representing growth hormone release pulses, soft pastel teal background.',
            ':: slow motion golden hormone waves spike upwards along the timeline, camera zooming out slowly'
        ),
        27: (
            'TED-Ed style flat crayon illustration of a brain cross-section highlighting the pituitary gland at the base releasing golden hormone packets, soft purple background.',
            ':: slow motion warm energy rings expand from the pituitary gland, camera rotating slowly'
        ),
        28: (
            'TED-Ed style flat crayon illustration of a sleep stage chart showing Stage N3 deep sleep highlighted with large hormone wave spikes, soft blue-gray background.',
            ':: slow motion glowing golden bubbles rise slowly from the deep sleep stage, camera tilting up slowly'
        ),
        30: (
            'TED-Ed style flat crayon illustration of a child sprout sleeping cozy in bed next to a sleep wave graph (slow delta waves), soft dark blue background.',
            ':: slow motion the sleep waves ripple slowly with a warm glow, camera zooming in slowly'
        ),
        31: (
            'TED-Ed style flat crayon illustration of a diagram of pituitary hormone pulses spiking high during deep slow-wave sleep cycles, soft indigo background.',
            ':: slow motion the hormone pulses expand as waves, camera rotating slowly'
        ),
        32: (
            'TED-Ed style flat crayon illustration of a timeline showing "1 to 2 Hours" passing after falling asleep, marking the first deep wave spike, soft pastel indigo background.',
            ':: slow motion the timeline indicator slides from 0 to 2 hours, camera zooming out slowly'
        ),
        35: (
            'TED-Ed style flat crayon illustration of blue light rays from a smartphone screen blocking and pushing away purple melatonin hormone bubbles, soft charcoal background.',
            ':: slow motion the blue rays actively push away the purple melatonin bubbles, camera panning down slowly'
        ),
        36: (
            'TED-Ed style flat crayon illustration of a clock showing "Day" and "Night" indicators confused by blue light interference, soft purple background.',
            ':: slow motion the clock dial flickers with confused orange light, camera rotating slowly'
        ),
        37: (
            'TED-Ed style flat crayon illustration of a golden growth hormone tap dripping very slowly, soft pastel coral background.',
            ':: slow motion a single golden droplet falls from the tap slowly, camera zooming in slowly'
        ),
        41: (
            'TED-Ed style flat crayon illustration of Calcium, Zinc, Vitamin D, and Arginine icons depicted as strong structural bricks, soft mint background.',
            ':: slow motion the nutrient bricks pulse with warm light, camera zooming in slowly'
        ),
        42: (
            'TED-Ed style flat crayon illustration of a toy delivery truck labeled "Vitamin D" carrying white Calcium blocks into a bone canal under a warm sun, soft yellow background.',
            ':: slow motion the Vitamin D truck rolls forward smoothly, camera panning left'
        ),
        43: (
            'TED-Ed style flat crayon illustration of Calcium blocks bouncing off a locked intestinal wall gate due to lack of Vitamin D, soft pastel coral background.',
            ':: slow motion the blocks bounce off and drop into a stream below, camera zooming out slowly'
        ),
        45: (
            'TED-Ed style flat crayon illustration of a cartoon Zinc atom character holding a blueprint, organizing dividing cells inside a bone plate, soft blue background.',
            ':: slow motion the blueprint unrolls to reveal cell structures, camera zooming in'
        ),
        46: (
            'TED-Ed style flat crayon illustration of cells dividing rapidly under a glowing blue light representing Zinc activation, soft pastel green background.',
            ':: slow motion the cells divide under the blue light, camera panning up slowly'
        ),
        47: (
            'TED-Ed style flat crayon illustration of a chemical chain of L-Arginine amino acid pearls folding into a strong protein shape, soft peach background.',
            ':: slow motion the pearl chain folds into a protein structure, camera rotating slowly'
        ),
        48: (
            'TED-Ed style flat crayon illustration of L-Arginine molecules stimulating a golden pituitary valve to release growth hormone, soft lavender background.',
            ':: slow motion the golden valve opens, releasing a stream of glowing light, camera zooming out'
        ),
        52: (
            'TED-Ed style flat crayon illustration of mechanical stress arrows pressing down vertically on a growth plate joint during exercise, soft pastel orange background.',
            ':: slow motion the vertical arrows compress and expand the joint model, camera zooming out slowly'
        ),
        54: (
            'TED-Ed style flat crayon illustration of mechanical stress vectors acting on a springy growth plate model, soft pastel yellow background.',
            ':: slow motion the mechanical vectors pulse rhythmically on the growth plate, camera panning up'
        ),
        56: (
            'TED-Ed style flat crayon illustration of a diagram showing compression and relaxation cycles acting on epiphyseal cartilage, soft lavender background.',
            ':: slow motion the cartilage layer expands and contracts under soft pulses, camera tilting down'
        ),
        57: (
            'TED-Ed style flat crayon illustration of blood vessels forming near the growth plate, delivering oxygen and nutrients, soft yellow background.',
            ':: slow motion nutrients flow rapidly through the red blood vessels, camera rotating slowly'
        ),
        59: (
            'TED-Ed style flat crayon illustration of a bone density chart showing bone density increasing under moderate resistance training, soft pastel orange background.',
            ':: slow motion the density chart bars rise steadily, camera zooming out'
        ),
        64: (
            'TED-Ed style flat crayon illustration of an endocrine pathway diagram showing Obesity leading to Leptin, GnRH, and early Estrogen release, soft pastel teal background.',
            ':: slow motion energy dots flow through the hormone pathway diagram, camera rotating slowly'
        ),
        65: (
            'TED-Ed style flat crayon illustration of round yellow fat cells releasing red leptin molecule dots into a blood vessel tube, soft peach background.',
            ':: slow motion the red leptin dots multiply and float through the vessel, camera zooming in slowly'
        ),
        66: (
            'TED-Ed style flat crayon illustration of leptin dots stimulating the brain\'s hypothalamus to activate the kisspeptin gene spark, soft purple background.',
            ':: slow motion the kisspeptin spark ignites and pulses with orange light, camera rotating slowly'
        ),
        67: (
            'TED-Ed style flat crayon illustration of kisspeptin spark releasing GnRH keys down a neural pathway to the pituitary gland, soft lavender background.',
            ':: slow motion the GnRH keys travel down the pathway, camera panning down slowly'
        ),
        68: (
            'TED-Ed style flat crayon illustration of domino blocks labeled "Obesity -> Leptin -> GnRH -> Precocious Puberty" falling towards a fast-spinning clock, soft cream background.',
            ':: slow motion the dominoes fall and strike the fast clock, camera zooming out'
        ),
        70: (
            'TED-Ed style flat crayon illustration of estrogen molecules accelerating bone fusion, closing the growth plate into a solid white line prematurely, soft lavender background.',
            ':: slow motion the growth plate ossifies rapidly into a solid white line, camera zooming in slowly'
        ),
        71: (
            'TED-Ed style flat crayon illustration of a growth plate closure timeline accelerating abnormally under a strong wind, soft pastel gray background.',
            ':: slow motion the timeline dial spins rapidly, camera panning right slowly'
        ),
        74: (
            'TED-Ed style flat crayon illustration of growth hormone molecules being wasted and diverted to dissolve fat cells instead of targeting bone plates, soft peach background.',
            ':: slow motion the hormone stream is diverted onto fat tissue, camera rotating slowly'
        ),
        75: (
            'TED-Ed style flat crayon illustration of a bone joint looking pale and deprived of hormone pulses while fat cells glow, soft pastel gray background.',
            ':: slow motion the joint dims while surrounding fat cells pulse bright, camera zooming in slowly'
        ),
        80: (
            'TED-Ed style flat crayon illustration of melatonin bubbles filling the room warmly in a completely dark bedroom, soft indigo background.',
            ':: slow motion the purple melatonin bubbles float peacefully, camera tilting down slowly'
        ),
        82: (
            'TED-Ed style flat crayon illustration of blood circulation pathways lighting up in the leg joint during exercise, soft teal background.',
            ':: slow motion nutrients and oxygen flow rapidly through the glowing pathways, camera rotating slowly'
        ),
        85: (
            'TED-Ed style flat crayon illustration of a parent sprout measuring a child\'s body mass index (BMI) on a wooden chart scale, soft cream background.',
            ':: slow motion the chart scale adjusts into correct healthy range, camera zooming out'
        )
    }

    with open(scenario_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by [Scene X]
    blocks = re.split(r'(\[Scene\s+\d+\])', content, flags=re.IGNORECASE)
    
    new_blocks = []
    # blocks[0] is everything before [Scene 0] (usually empty or header)
    new_blocks.append(blocks[0])

    for i in range(1, len(blocks), 2):
        scene_header = blocks[i]
        block_body = blocks[i+1]
        
        # Parse scene ID
        scene_id_match = re.search(r'\d+', scene_header)
        if not scene_id_match:
            new_blocks.append(scene_header + block_body)
            continue
            
        scene_id = int(scene_id_match.group())
        
        # If we have a replacement for this scene, apply it
        if scene_id in visual_map:
            new_image, new_motion = visual_map[scene_id]
            
            # Replace image field
            block_body = re.sub(r'image:\s*(.*)', f'image: {new_image}', block_body, flags=re.IGNORECASE)
            # Replace motion field
            block_body = re.sub(r'motion:\s*(.*)', f'motion: {new_motion}', block_body, flags=re.IGNORECASE)
            
        new_blocks.append(scene_header + block_body)

    updated_content = "".join(new_blocks)

    with open(scenario_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    print(f"Successfully updated {scenario_path} with enhanced medical visuals.")

    # Now recreate child_growth_prompts.txt from the updated scenario.txt
    # Format of prompts: [Scene X] image_prompt :: motion_prompt
    raw_blocks = re.split(r'\[Scene\s+(\d+)\]', updated_content, flags=re.IGNORECASE)
    
    prompts_lines = []
    for i in range(1, len(raw_blocks), 2):
        scene_id = int(raw_blocks[i])
        block_text = raw_blocks[i+1]
        
        image_match = re.search(r'image:\s*(.*)', block_text, re.IGNORECASE)
        motion_match = re.search(r'motion:\s*(.*)', block_text, re.IGNORECASE)
        
        image_val = image_match.group(1).strip() if image_match else ""
        motion_val = motion_match.group(1).strip() if motion_match else ""
        
        prompts_lines.append(f"[Scene {scene_id}] {image_val} :: {motion_val}")

    with open(prompts_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(prompts_lines) + "\n")
    print(f"Successfully generated {prompts_path} with {len(prompts_lines)} lines.")

if __name__ == '__main__':
    main()
