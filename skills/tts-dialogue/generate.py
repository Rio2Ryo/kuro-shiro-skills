import os
import yaml
from openai import OpenAI

# OpenAIクライアント初期化
client = OpenAI()

# 設定
YAML_PATH = "x-strategy/06-tts-script-v2.yaml"
OUTPUT_DIR = "x-strategy/audio-v2"
VOICE_MAPPING = {
    "kuro": "onyx",
    "shiro": "nova"
}

def generate_audio():
    # YAML読み込み
    with open(YAML_PATH, "r") as f:
        # 複数ドキュメントに対応するため safe_load_all を使用
        documents = list(yaml.safe_load_all(f))

    print(f"Loaded YAML from {YAML_PATH}")
    
    # 全ドキュメントをフラットなリストに結合
    all_slides = []
    for doc in documents:
        if isinstance(doc, list):
            all_slides.extend(doc)
    
    # 各スライド処理
    for slide in all_slides:
        if not slide: continue # skip empty lines or headers parsed as None
        
        slide_num = slide.get('slide')
        lines = slide.get('lines', [])
        
        if not slide_num: continue

        print(f"Processing Slide {slide_num}...")
        
        for i, line in enumerate(lines):
            speaker = line.get('speaker')
            text = line.get('text')
            voice = VOICE_MAPPING.get(speaker, "alloy")
            
            # ファイル名: slide-01-01.mp3 (スライド番号-行番号)
            filename = f"slide-{slide_num:02d}-{i+1:02d}.mp3"
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            if os.path.exists(filepath):
                print(f"  Skipping {filename} (already exists)")
                continue
                
            print(f"  Generating {filename} ({speaker}): {text[:20]}...")
            
            try:
                response = client.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=text
                )
                response.stream_to_file(filepath)
            except Exception as e:
                print(f"  Error generating {filename}: {e}")

if __name__ == "__main__":
    generate_audio()
