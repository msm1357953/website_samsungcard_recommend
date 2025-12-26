"""
삼성카드 히어로 이미지 생성기
Gemini 3 Pro Image API를 사용하여 프리미엄 카드 쇼케이스 이미지 생성
"""
import os
import io
from PIL import Image
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

PROJECT_ID = os.getenv("project_id")
LOCATION = os.getenv("location")

if not PROJECT_ID or not LOCATION:
    raise ValueError("Please set project_id and location in .env file")


def generate_hero_image(card_images: list, output_path: str, prompt: str):
    """
    삼성카드 이미지들을 사용하여 프리미엄 히어로 이미지 생성
    
    Args:
        card_images: 카드 이미지 경로 리스트 (최대 3개)
        output_path: 출력 이미지 경로
        prompt: 생성 프롬프트
    """
    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    model_id = "gemini-3-pro-image-preview"
    
    # 카드 이미지들 로드
    contents = []
    for img_path in card_images:
        if os.path.exists(img_path):
            with open(img_path, "rb") as f:
                img_bytes = f.read()
            contents.append(types.Part.from_bytes(data=img_bytes, mime_type="image/png"))
            print(f"  [로드] {os.path.basename(img_path)}")
    
    # 프롬프트 추가
    contents.append(prompt)
    
    print("  [생성중] Gemini API 호출...")
    
    try:
        response = client.models.generate_content(
            model=model_id,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=['IMAGE'],
                image_config=types.ImageConfig(
                    aspect_ratio="4:3",  # 가로형
                    image_size="2K",
                ),
            ),
        )
        
        if not response.candidates[0].content.parts[0].inline_data:
            print("  [실패] 이미지 생성 실패")
            return None
        
        generated_data = response.candidates[0].content.parts[0].inline_data.data
        generated_img = Image.open(io.BytesIO(generated_data))
        
        # 저장
        generated_img.save(output_path, "PNG", optimize=True)
        print(f"  [완료] {output_path} ({generated_img.width}x{generated_img.height})")
        
        return generated_img
        
    except Exception as e:
        print(f"  [오류] {e}")
        return None


if __name__ == "__main__":
    # 삼성카드 이미지 경로 (상대 경로)
    card_images = [
        "assets/card1.png",
        "assets/card2.png",
        "assets/card3_monimo.png",
    ]
    
    output_path = "assets/hero_premium.png"
    
    # 세로 카드 프롬프트 (강화된 세로형 지시)
    prompt = """
    Create a premium 3D product photography scene featuring THESE THREE EXACT CREDIT CARDS.
    
    ABSOLUTELY CRITICAL - CARD ORIENTATION:
    - ALL THREE CARDS MUST BE DISPLAYED IN PORTRAIT/VERTICAL ORIENTATION
    - Each card must stand TALL (taller than wide) - NOT landscape/horizontal
    - Do NOT rotate any card to horizontal/landscape orientation under any circumstances
    - The card's short edge should be at the bottom, long edge should be vertical
    
    CARD ARRANGEMENT:
    - All three cards standing upright in elegant metallic chrome pedestals
    - Cards placed in sleek metallic slot holders gripping the bottom edge
    - Staggered pyramid composition:
      * Left card: lower position (VERTICAL)
      * Center card: highest position, prominent (VERTICAL)
      * Right card: medium position (VERTICAL)
    
    STYLING:
    - Deep black background
    - Beautiful cinematic lighting with blue and purple rim lights
    - Glowing highlights on the metal surfaces
    - Reflective polished floor surface
    - Ultra high quality, photorealistic
    
    CRITICAL:
    - Keep ALL original card designs EXACTLY as provided
    - Do NOT modify, rotate horizontally, or alter the card images in any way
    - ALL cards must remain in VERTICAL/PORTRAIT orientation (standing tall)
    - Cards should be clearly visible and recognizable
    """
    
    print("\n=== 삼성카드 히어로 이미지 생성기 ===\n")
    generate_hero_image(card_images, output_path, prompt)
