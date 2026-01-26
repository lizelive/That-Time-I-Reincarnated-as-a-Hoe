#!/usr/bin/env python3
"""
Image Generation Tool for "The Time I Reincarnated as a Hoe" Manga

Uses FLUX.2-klein-9B via Hugging Face API to generate consistent manga-style images.
Each chapter contains 24 images that tell the story from Howen's POV.

Usage:
    python generate_images.py --chapter arc1/chapter01 --token YOUR_HF_TOKEN
    python generate_images.py --chapter arc1/chapter01 --token YOUR_HF_TOKEN --image 5
    python generate_images.py --list-chapters
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
import requests
from typing import Optional, List, Dict, Any

# Hugging Face API endpoint for FLUX.2-klein-9B
HF_API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.2-klein-9B"

# Character reference descriptions for consistency
CHARACTER_REFS = {
    "howen": {
        "description": "A persona hoe (farming tool) with a curved dark metal blade showing subtle archotech circuitry patterns, hardwood handle reinforced with plasteel, small glowing blue AI core where handle meets head. The tool glows faintly when communicating. Sometimes has small roots or fungal growths along the handle when emotional.",
        "human_memory": "A woman with dark hair in a practical ponytail, calloused farmer's hands, deep brown eyes, wearing simple work-stained farmer's clothing.",
    },
    "cora": {
        "description": "A 19-year-old tribal woman with honey-brown hair tied back with cloth, bright green eyes that look old for her face, calloused hands, sun-weathered skin with freckles across her nose. Lean and strong build from hard work.",
        "arc1_attire": "Simple homespun shirt, sturdy trousers, leather boots worn thin.",
        "arc3_attire": "Imperial auxiliary uniform, practical and well-fitted.",
        "arc5_attire": "Deserter combat attire - leather and plasteel hybrid armor, Howen always at her hip.",
    },
    "chitin": {
        "larva": "A dog-sized megascarab larva with pale white carapace, large mandibles, six stumpy legs. Has a distinctive crack in carapace forming a 'lightning bolt' pattern.",
        "adult": "A horse-sized megascarab with iridescent black-green carapace, massive mandibles capable of crushing plasteel. The lightning bolt crack pattern is still visible.",
    },
    "vex": {
        "description": "A tall, muscular woman in her 40s with close-cropped gray hair, battle scars, missing left ear. Wears an old Imperial coat with the insignia burned off.",
    },
    "wheatstone": {
        "description": "An AI entity that manifests as glowing text/interface on screens, or as a holographic projection of a formal, older gentleman with kind but sad eyes.",
    },
}

# Location reference descriptions
LOCATION_REFS = {
    "vault": "Ancient danger vault - dark metal walls with dormant archotech circuits, dim emergency lighting, ancient dust, cryptosleep caskets, dormant mechanoids in shadows.",
    "mushroom_garden": "Underground cave with bioluminescent mushrooms in various colors, soft glowing light, Howen's cultivation area in the vault.",
    "megascarab_nest": "Dark cavern with chitinous remains, insect tunnels, the smell of earth and decay, skittering sounds in the darkness.",
    "rim_surface": "Harsh rimworld terrain - scrubby vegetation, distant mountains, alien sky with two small moons, scattered ruins.",
    "imperial_fort": "Clean, ordered Imperial military installation - plasteel walls, energy barriers, Imperial banners, uniformed soldiers.",
    "barleybloom_valley": "Hidden valley with golden barley fields, traditional wooden buildings with thatched roofs, peaceful farming community.",
    "anima_grove": "Sacred clearing with seven massive anima trees that glow with inner light, luminescent moss, charged air with psychic energy.",
    "deserter_camp": "Hidden guerrilla base in a box canyon - canvas tents, training grounds, maps on tables, hard-looking fighters.",
}

# Style guidelines for manga images
STYLE_GUIDE = """
Manga style, black and white with screentones, dynamic composition, 
expressive linework, dramatic lighting. POV from Howen (the hoe) - 
often showing Cora's face from below/side, or environmental shots 
as if looking from ground level or being held. Include subtle 
visual indicators of Howen's emotional state through the glow of 
her core or plant growth along her handle.
"""


def load_chapter_data(chapter_path: str) -> Dict[str, Any]:
    """Load chapter JSON data from the manga directory."""
    base_path = Path(__file__).parent.parent / "manga" / f"{chapter_path}.json"
    if not base_path.exists():
        raise FileNotFoundError(f"Chapter file not found: {base_path}")
    
    with open(base_path, "r") as f:
        return json.load(f)


def list_available_chapters() -> List[str]:
    """List all available chapter JSON files."""
    manga_path = Path(__file__).parent.parent / "manga"
    chapters = []
    for json_file in manga_path.rglob("*.json"):
        rel_path = json_file.relative_to(manga_path)
        chapters.append(str(rel_path.with_suffix("")))
    return sorted(chapters)


def build_prompt(image_data: Dict[str, Any], chapter_data: Dict[str, Any]) -> str:
    """Build the full prompt for image generation including references."""
    # Start with base style
    prompt_parts = [STYLE_GUIDE.strip()]
    
    # Add scene description
    prompt_parts.append(f"Scene: {image_data['description']}")
    
    # Add character references
    for char in image_data.get("characters", []):
        if char in CHARACTER_REFS:
            char_ref = CHARACTER_REFS[char]
            if isinstance(char_ref, dict):
                # Get appropriate description based on context
                if "description" in char_ref:
                    prompt_parts.append(f"{char.title()}: {char_ref['description']}")
            else:
                prompt_parts.append(f"{char.title()}: {char_ref}")
    
    # Add location reference
    location = image_data.get("location")
    if location and location in LOCATION_REFS:
        prompt_parts.append(f"Setting: {LOCATION_REFS[location]}")
    
    # Add POV indicator
    prompt_parts.append("POV: From Howen (the hoe) - ground level or being held perspective")
    
    # Add mood/emotion
    if "mood" in image_data:
        prompt_parts.append(f"Mood: {image_data['mood']}")
    
    # Add any specific visual elements
    if "visual_elements" in image_data:
        prompt_parts.append(f"Include: {', '.join(image_data['visual_elements'])}")
    
    return "\n".join(prompt_parts)


def generate_image(
    prompt: str, 
    token: str, 
    output_path: Path,
    width: int = 768,
    height: int = 1024,
    guidance_scale: float = 7.5,
    num_inference_steps: int = 50
) -> bool:
    """Generate a single image using the Hugging Face API.
    
    Note: Some parameters may not be supported by all models. The API will
    ignore unsupported parameters gracefully.
    """
    headers = {"Authorization": f"Bearer {token}"}
    
    # Build parameters dict - some models may not support all of these
    # The HF Inference API typically ignores unsupported parameters
    payload = {
        "inputs": prompt,
        "parameters": {
            "width": width,
            "height": height,  # Manga page proportions
        }
    }
    
    # Add optional parameters that may not be supported by all models
    if guidance_scale is not None:
        payload["parameters"]["guidance_scale"] = guidance_scale
    if num_inference_steps is not None:
        payload["parameters"]["num_inference_steps"] = num_inference_steps
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=120)
            
            if response.status_code == 200:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return True
            elif response.status_code == 503:
                # Model loading, wait and retry
                wait_time = response.json().get("estimated_time", 30)
                print(f"  Model loading, waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"  Error: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            print(f"  Timeout on attempt {attempt + 1}")
            time.sleep(10)
        except Exception as e:
            print(f"  Error: {e}")
            return False
    
    return False


def generate_chapter_images(
    chapter_path: str,
    token: str,
    specific_image: Optional[int] = None,
    dry_run: bool = False
) -> None:
    """Generate all images for a chapter."""
    chapter_data = load_chapter_data(chapter_path)
    
    print(f"\n{'='*60}")
    print(f"Chapter: {chapter_data['title']}")
    print(f"Arc: {chapter_data['arc']}")
    print(f"POV: {chapter_data['pov']}")
    print(f"{'='*60}\n")
    
    images = chapter_data["images"]
    
    if specific_image is not None:
        if 1 <= specific_image <= len(images):
            images = [(specific_image, images[specific_image - 1])]
        else:
            print(f"Error: Image {specific_image} not found (chapter has {len(images)} images)")
            return
    else:
        images = list(enumerate(images, 1))
    
    output_dir = Path(__file__).parent.parent / "manga" / "output" / chapter_path
    
    for img_num, img_data in images:
        print(f"Image {img_num}/{len(chapter_data['images'])}: {img_data.get('caption', 'No caption')}")
        
        prompt = build_prompt(img_data, chapter_data)
        
        if dry_run:
            print(f"  [DRY RUN] Would generate with prompt:")
            print(f"  {prompt[:200]}...")
            print()
            continue
        
        output_path = output_dir / f"page_{img_num:02d}.png"
        
        if output_path.exists():
            print(f"  Skipping (already exists)")
            continue
        
        print(f"  Generating...")
        success = generate_image(prompt, token, output_path)
        
        if success:
            print(f"  Saved to {output_path}")
        else:
            print(f"  FAILED")
        
        # Rate limiting
        time.sleep(2)
    
    print(f"\nGeneration complete!")


def create_chapter_template(chapter_path: str) -> None:
    """Create a template JSON file for a new chapter."""
    template = {
        "title": "Chapter Title",
        "arc": "arc1",
        "chapter_number": 1,
        "pov": "howen",
        "summary": "Brief chapter summary from Howen's perspective.",
        "images": [
            {
                "page": i,
                "description": f"Scene description for page {i}",
                "caption": "Dialogue or narration text",
                "characters": ["howen"],
                "location": "vault",
                "mood": "mysterious",
                "visual_elements": [],
                "reference_images": []
            }
            for i in range(1, 25)
        ]
    }
    
    output_path = Path(__file__).parent.parent / "manga" / f"{chapter_path}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w") as f:
        json.dump(template, f, indent=2)
    
    print(f"Created template: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate manga images for The Time I Reincarnated as a Hoe"
    )
    parser.add_argument(
        "--chapter",
        help="Chapter path (e.g., arc1/chapter01)"
    )
    parser.add_argument(
        "--token",
        help="Hugging Face API token",
        default=os.environ.get("HF_TOKEN")
    )
    parser.add_argument(
        "--image",
        type=int,
        help="Generate only a specific image number"
    )
    parser.add_argument(
        "--list-chapters",
        action="store_true",
        help="List available chapters"
    )
    parser.add_argument(
        "--create-template",
        metavar="PATH",
        help="Create a new chapter template"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show prompts without generating images"
    )
    
    args = parser.parse_args()
    
    if args.list_chapters:
        chapters = list_available_chapters()
        if chapters:
            print("Available chapters:")
            for ch in chapters:
                print(f"  {ch}")
        else:
            print("No chapters found. Create one with --create-template")
        return
    
    if args.create_template:
        create_chapter_template(args.create_template)
        return
    
    if not args.chapter:
        parser.print_help()
        return
    
    if not args.token and not args.dry_run:
        print("Error: HF_TOKEN required. Set via --token or HF_TOKEN environment variable.")
        sys.exit(1)
    
    generate_chapter_images(
        args.chapter,
        args.token or "",
        args.image,
        args.dry_run
    )


if __name__ == "__main__":
    main()
