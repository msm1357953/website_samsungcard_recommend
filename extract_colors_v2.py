import json
import os
import requests
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
from io import BytesIO
import colorsys

def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip('#')
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

def adjust_color_brightness(hex_color, factor=0.85):
    """
    Adjusts the brightness of a HEX color.
    factor < 1.0 makes it darker, factor > 1.0 makes it lighter.
    """
    rgb = hex_to_rgb(hex_color)
    # Simple darkening
    new_rgb = [max(0, min(255, c * factor)) for c in rgb]
    return rgb_to_hex(new_rgb)

def score_color(rgb):
    """
    Scoring function to prioritize vibrant colors.
    Converts to HSV.
    Higher saturation and reasonable brightness = higher score.
    Penalizes very white, very black, or very gray colors.
    """
    r, g, b = [x/255.0 for x in rgb]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    
    # Penalties
    penalty = 0
    if s < 0.2: penalty += 200 # Too gray
    if v < 0.2: penalty += 200 # Too black
    if v > 0.9 and s < 0.1: penalty += 300 # Too white
    
    # Heuristic score: High Saturation * Value is good.
    score = (s * 100) + (v * 50) - penalty
    return score

def extract_dominant_color(image_url):
    try:
        response = requests.get(image_url, timeout=10)
        img = Image.open(BytesIO(response.content))
        img = img.convert("RGB")
        img = img.resize((100, 100)) # Resize for speed
        
        data = np.array(img).reshape(-1, 3)
        
        # Use KMeans to find 5 dominant clusters
        kmeans = KMeans(n_clusters=5, n_init=3, random_state=42)
        kmeans.fit(data)
        colors = kmeans.cluster_centers_
        
        # Score colors and pick the best one
        best_color = None
        best_score = -9999
        
        for color in colors:
            score = score_color(color)
            if score > best_score:
                best_score = score
                best_color = color
                
        # If all colors are terrible (e.g., black and white card), just pick the most saturated one found
        if best_color is None:
             best_color = colors[0]

        return rgb_to_hex(best_color)
        
    except Exception as e:
        print(f"Error processing {image_url}: {e}")
        return None

def main():
    json_path = 'data/samsung_cards.json'
    output_path = 'data/samsung_cards_updated.json'
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    cards = data['cards']
    total = len(cards)
    
    print(f"Starting color extraction for {total} cards...")
    
    for i, card in enumerate(cards):
        img_url = card.get('image_url')
        if not img_url:
            continue
            
        print(f"[{i+1}/{total}] Processing: {card['name']}...", end='', flush=True)
        
        new_primary = extract_dominant_color(img_url)
        
        if new_primary:
            new_secondary = adjust_color_brightness(new_primary, 0.8) # Generate slightly darker secondary
            
            # Log changes if significantly different (optional, simple log here)
            old_primary = card.get('primary_color', 'N/A')
            
            card['primary_color'] = new_primary
            card['secondary_color'] = new_secondary
            print(f" Done. {old_primary} -> {new_primary}")
        else:
            print(" Failed. Keeping original.")
            
    # Save updated file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"\nCompleted! Updated data saved to {output_path}")

if __name__ == '__main__':
    main()
