import os
import sys

# Hangeul Unicode Constants
CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
JUNGSEUNG_LIST = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']
JONGSUNG_LIST = ['', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

# Full decomposition mapping for ALL double/compound consonants and vowels
JAMO_FULL_DECOMPOSITION_MAP = {
    # 1. Double Consonants (Chosung & Jongsung)
    'ㄲ': ['ㄱ', 'ㄱ'],
    'ㄸ': ['ㄷ', 'ㄷ'],
    'ㅃ': ['ㅂ', 'ㅂ'],
    'ㅆ': ['ㅅ', 'ㅅ'],
    'ㅉ': ['ㅈ', 'ㅈ'],
    
    # 2. Compound Vowels (Jungseung)
    'ㅐ': ['ㅏ', 'ㅣ'],
    'ㅔ': ['ㅓ', 'ㅣ'],
    'ㅒ': ['ㅑ', 'ㅣ'],
    'ㅖ': ['ㅕ', 'ㅣ'],
    'ㅘ': ['ㅗ', 'ㅏ'],
    'ㅙ': ['ㅗ', 'ㅏ', 'ㅣ'],
    'ㅚ': ['ㅗ', 'ㅣ'],
    'ㅝ': ['ㅜ', 'ㅓ'],
    'ㅞ': ['ㅜ', 'ㅓ', 'ㅣ'],
    'ㅟ': ['ㅜ', 'ㅣ'],
    'ㅢ': ['ㅡ', 'ㅣ'],
    
    # 3. Compound Batchim Consonants (Jongsung)
    'ㄳ': ['ㄱ', 'ㅅ'],
    'ㄵ': ['ㄴ', 'ㅈ'],
    'ㄶ': ['ㄴ', 'ㅎ'],
    'ㄺ': ['ㄹ', 'ㄱ'],
    'ㄻ': ['ㄹ', 'ㅁ'],
    'ㄼ': ['ㄹ', 'ㅂ'],
    'ㄽ': ['ㄹ', 'ㅅ'],
    'ㄾ': ['ㄹ', 'ㅌ'],
    'ㄿ': ['ㄹ', 'ㅍ'],
    'ㅀ': ['ㄹ', 'ㅎ'],
    'ㅄ': ['ㅂ', 'ㅅ']
}

def decompose_char(char, fully_decompose=True):
    """Decomposes a single Hangeul syllable into constituent letters, optionally fully dismantling composite/double forms."""
    if not '\uac00' <= char <= '\ud7a3':
        return [char]
        
    char_code = ord(char) - 0xAC00
    jongsung_idx = char_code % 28
    jungseung_idx = ((char_code - jongsung_idx) // 28) % 21
    chosung_idx = ((char_code - jongsung_idx) // 28) // 21
    
    jamos = []
    # 1. Chosung
    cho = CHOSUNG_LIST[chosung_idx]
    if fully_decompose and cho in JAMO_FULL_DECOMPOSITION_MAP:
        jamos.extend(JAMO_FULL_DECOMPOSITION_MAP[cho])
    else:
        jamos.append(cho)
        
    # 2. Jungseung
    jung = JUNGSEUNG_LIST[jungseung_idx]
    if fully_decompose and jung in JAMO_FULL_DECOMPOSITION_MAP:
        jamos.extend(JAMO_FULL_DECOMPOSITION_MAP[jung])
    else:
        jamos.append(jung)
        
    # 3. Jongsung
    jong = JONGSUNG_LIST[jongsung_idx]
    if jong:
        if fully_decompose and jong in JAMO_FULL_DECOMPOSITION_MAP:
            jamos.extend(JAMO_FULL_DECOMPOSITION_MAP[jong])
        else:
            jamos.append(jong)
            
    return jamos

def decompose_text(text, fully_decompose=True):
    """Decomposes an entire text sentence into a flat list of constituent Jamo letters."""
    result = []
    for char in text:
        result.extend(decompose_char(char, fully_decompose))
    return result

def get_jamo_asset_paths(text):
    """Decomposes text and returns list of dict containing the Jamo char and its corresponding PNG asset path."""
    decomposed = decompose_text(text)
    assets_dir = "assets/graphics/letters"
    
    assets_list = []
    for jamo in decomposed:
        # Check if basic asset exists
        filename = f"letter_{jamo}.png"
        path = os.path.join(assets_dir, filename)
        
        # If the complex consonant asset doesn't exist, we can generate it on the fly
        if not os.path.exists(path) and jamo not in [' ', '\n', '\t', '.', ',', '!', '?']:
            # Call generation function
            from generate_letters_assets import generate_text_lineart
            generate_text_lineart(jamo, path, font_size=180, stroke_width=6)
            
        assets_list.append({
            "char": jamo,
            "path": path if os.path.exists(path) else None
        })
        
    return assets_list

if __name__ == "__main__":
    test_text = "깎는 왏"
    print(f"Decomposing test text: '{test_text}'")
    decomposed = decompose_text(test_text, fully_decompose=True)
    print(f"Constituent Jamos: {decomposed}")
    
    assets = get_jamo_asset_paths(test_text)
    print("\nAsset Mappings:")
    for asset in assets:
        print(f"  Character '{asset['char']}' -> {asset['path']}")
