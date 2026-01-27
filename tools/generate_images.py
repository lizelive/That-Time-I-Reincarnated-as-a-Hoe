#!/usr/bin/env python3
"""
Image Generation Tool for "The Time I Reincarnated as a Hoe" Manga

Uses FLUX.2-klein-9B via Hugging Face API to generate consistent manga-style images.
Each chapter contains 24 images that tell the story from Howen's POV.

Follows the FLUX.2 prompting guide:
- Write like a novelist: Subject → Setting → Details → Lighting → Atmosphere
- Front-load important elements
- Include explicit lighting description
- Add style and mood annotations

Usage:
    python generate_images.py --chapter arc1/chapter01 --token YOUR_HF_TOKEN
    python generate_images.py --chapter arc1/chapter01 --token YOUR_HF_TOKEN --page 5
    python generate_images.py --list-chapters
    python generate_images.py --generate-reference howen --token YOUR_HF_TOKEN
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
import requests
from typing import Optional, List, Dict, Any

# Base paths
MANGA_PATH = Path(__file__).parent.parent / "manga"
REFERENCES_PATH = MANGA_PATH / "references"

# Hugging Face API endpoint for FLUX.2-klein-9B
HF_API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"


def load_character_reference(char_id: str) -> Optional[Dict[str, Any]]:
    """Load a character reference JSON file."""
    char_path = REFERENCES_PATH / "characters" / f"{char_id}.json"
    if char_path.exists():
        with open(char_path) as f:
            return json.load(f)
    return None


def load_location_reference(loc_id: str) -> Optional[Dict[str, Any]]:
    """Load a location reference JSON file."""
    loc_path = REFERENCES_PATH / "locations" / f"{loc_id}.json"
    if loc_path.exists():
        with open(loc_path) as f:
            return json.load(f)
    return None


def load_page_data(chapter_path: str, page_num: int) -> Dict[str, Any]:
    """Load a single page JSON file."""
    page_path = MANGA_PATH / chapter_path / f"page_{page_num:03d}.json"
    if not page_path.exists():
        raise FileNotFoundError(f"Page file not found: {page_path}")
    
    with open(page_path) as f:
        return json.load(f)


def load_chapter_meta(chapter_path: str) -> Dict[str, Any]:
    """Load chapter metadata."""
    meta_path = MANGA_PATH / chapter_path / "chapter_meta.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"Chapter metadata not found: {meta_path}")
    
    with open(meta_path) as f:
        return json.load(f)


def list_available_chapters() -> List[str]:
    """List all available chapters (directories with chapter_meta.json)."""
    chapters = []
    for meta_file in MANGA_PATH.rglob("chapter_meta.json"):
        chapter_path = meta_file.parent.relative_to(MANGA_PATH)
        chapters.append(str(chapter_path))
    return sorted(chapters)


def list_chapter_pages(chapter_path: str) -> List[int]:
    """List all available page numbers for a chapter."""
    chapter_dir = MANGA_PATH / chapter_path
    pages = []
    for page_file in chapter_dir.glob("page_*.json"):
        try:
            page_num = int(page_file.stem.split("_")[1])
            pages.append(page_num)
        except (IndexError, ValueError):
            continue
    return sorted(pages)


def build_prompt(page_data: Dict[str, Any]) -> str:
    """
    Build the full prompt for image generation following FLUX.2 guide.
    
    Structure: Subject → Setting → Details → Lighting → Atmosphere
    """
    # The prompt field should already be well-formed following the guide
    # Just return it directly - it's written as flowing prose
    prompt = page_data.get("prompt", "")
    
    # If no prompt, build from components (legacy support)
    if not prompt:
        parts = []
        
        # Subject/Scene description
        if "description" in page_data:
            parts.append(page_data["description"])
        
        # Add lighting if specified separately
        if "lighting" in page_data:
            parts.append(page_data["lighting"])
        
        # Add mood as style annotation
        if "mood" in page_data:
            parts.append(f"Mood: {page_data['mood']}")
        
        prompt = " ".join(parts)
    
    return prompt


def build_reference_prompt(ref_type: str, ref_id: str) -> Optional[str]:
    """Build prompt from a reference file."""
    if ref_type == "character":
        ref = load_character_reference(ref_id)
        if ref:
            return ref.get("reference_prompt") or ref.get("reference_prompt_adult")
    elif ref_type == "location":
        ref = load_location_reference(ref_id)
        if ref:
            return ref.get("reference_prompt")
    return None


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
    specific_page: Optional[int] = None,
    dry_run: bool = False
) -> None:
    """Generate all images for a chapter."""
    try:
        chapter_meta = load_chapter_meta(chapter_path)
    except FileNotFoundError:
        print(f"Error: Chapter metadata not found at {chapter_path}")
        return
    
    print(f"\n{'='*60}")
    print(f"Chapter: {chapter_meta['chapter_title']}")
    print(f"Arc: {chapter_meta['arc_title']}")
    print(f"POV: {chapter_meta['pov']}")
    print(f"{'='*60}\n")
    
    pages = list_chapter_pages(chapter_path)
    
    if specific_page is not None:
        if specific_page in pages:
            pages = [specific_page]
        else:
            print(f"Error: Page {specific_page} not found (available: {pages})")
            return
    
    output_dir = MANGA_PATH / "output" / chapter_path
    
    for page_num in pages:
        page_data = load_page_data(chapter_path, page_num)
        caption = page_data.get('caption', 'No caption')
        
        print(f"Page {page_num}/{max(pages)}: {caption[:50]}...")
        
        prompt = build_prompt(page_data)
        
        if dry_run:
            print(f"  [DRY RUN] Prompt:")
            print(f"  {prompt[:300]}...")
            print()
            continue
        
        output_path = output_dir / f"page_{page_num:03d}.png"
        
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


def generate_reference_image(
    ref_type: str,
    ref_id: str,
    token: str,
    dry_run: bool = False
) -> None:
    """Generate a reference image for a character or location."""
    prompt = build_reference_prompt(ref_type, ref_id)
    
    if not prompt:
        print(f"Error: No reference prompt found for {ref_type}/{ref_id}")
        return
    
    print(f"\n{'='*60}")
    print(f"Generating reference: {ref_type}/{ref_id}")
    print(f"{'='*60}\n")
    
    if dry_run:
        print(f"[DRY RUN] Prompt:")
        print(f"{prompt}")
        return
    
    output_dir = MANGA_PATH / "output" / "references" / f"{ref_type}s"
    output_path = output_dir / f"{ref_id}.png"
    
    if output_path.exists():
        print(f"Skipping (already exists)")
        return
    
    print(f"Generating...")
    success = generate_image(prompt, token, output_path)
    
    if success:
        print(f"Saved to {output_path}")
    else:
        print(f"FAILED")


def create_chapter_template(chapter_path: str, num_pages: int = 24) -> None:
    """Create a template directory structure for a new chapter."""
    chapter_dir = MANGA_PATH / chapter_path
    chapter_dir.mkdir(parents=True, exist_ok=True)
    
    # Create chapter metadata
    meta = {
        "chapter_id": chapter_path.replace("/", "_"),
        "arc": int(chapter_path.split("/")[0].replace("arc", "")),
        "arc_title": "Arc Title",
        "chapter": int(chapter_path.split("/")[1].replace("chapter", "")),
        "chapter_title": "Chapter Title",
        "pov": "howen",
        "total_pages": num_pages,
        "summary": "Chapter summary from Howen's POV.",
        "themes": [],
        "character_development": {},
        "key_moments": [],
        "page_files": [f"page_{i:03d}.json" for i in range(1, num_pages + 1)],
        "next_chapter": None,
        "previous_chapter": None
    }
    
    with open(chapter_dir / "chapter_meta.json", "w") as f:
        json.dump(meta, f, indent=2)
    
    # Create page templates
    for i in range(1, num_pages + 1):
        page = {
            "image_id": f"{chapter_path.replace('/', '_')}_{i:03d}",
            "arc": meta["arc"],
            "chapter": meta["chapter"],
            "chapter_title": meta["chapter_title"],
            "page": i,
            "pov": "howen",
            "prompt": "Write flowing prose describing: Subject → Setting → Details → Lighting → Atmosphere. Style: [style]. Mood: [mood].",
            "caption": "Dialogue or narration text",
            "narration": "Internal monologue from Howen's POV",
            "characters": ["howen"],
            "character_refs": ["references/characters/howen.json"],
            "location": "vault",
            "location_refs": ["references/locations/vault.json"],
            "visual_elements": [],
            "lighting": "Describe lighting",
            "mood": "mysterious",
            "technical_notes": ""
        }
        
        with open(chapter_dir / f"page_{i:03d}.json", "w") as f:
            json.dump(page, f, indent=2)
    
    print(f"Created chapter template at {chapter_dir}")
    print(f"  - chapter_meta.json")
    print(f"  - {num_pages} page files")


def list_references() -> None:
    """List all available reference files."""
    print("\nCharacter References:")
    for ref in (REFERENCES_PATH / "characters").glob("*.json"):
        print(f"  {ref.stem}")
    
    print("\nLocation References:")
    for ref in (REFERENCES_PATH / "locations").glob("*.json"):
        print(f"  {ref.stem}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate manga images for The Time I Reincarnated as a Hoe",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available chapters
  python generate_images.py --list-chapters
  
  # Generate all pages for a chapter
  python generate_images.py --chapter arc1/chapter01 --token YOUR_TOKEN
  
  # Generate a specific page
  python generate_images.py --chapter arc1/chapter01 --page 5 --token YOUR_TOKEN
  
  # Preview prompts without generating
  python generate_images.py --chapter arc1/chapter01 --dry-run
  
  # Generate character reference image
  python generate_images.py --generate-reference character:howen --token YOUR_TOKEN
  
  # List all references
  python generate_images.py --list-references
"""
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
        "--page",
        type=int,
        help="Generate only a specific page number"
    )
    parser.add_argument(
        "--list-chapters",
        action="store_true",
        help="List available chapters"
    )
    parser.add_argument(
        "--list-references",
        action="store_true",
        help="List available reference files"
    )
    parser.add_argument(
        "--create-template",
        metavar="PATH",
        help="Create a new chapter template (e.g., arc1/chapter03)"
    )
    parser.add_argument(
        "--generate-reference",
        metavar="TYPE:ID",
        help="Generate a reference image (e.g., character:howen, location:vault)"
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
                try:
                    meta = load_chapter_meta(ch)
                    print(f"  {ch}: {meta.get('chapter_title', 'Untitled')}")
                except Exception:
                    print(f"  {ch}")
        else:
            print("No chapters found. Create one with --create-template")
        return
    
    if args.list_references:
        list_references()
        return
    
    if args.create_template:
        create_chapter_template(args.create_template)
        return
    
    if args.generate_reference:
        if ":" not in args.generate_reference:
            print("Error: Format should be TYPE:ID (e.g., character:howen)")
            sys.exit(1)
        ref_type, ref_id = args.generate_reference.split(":", 1)
        if not args.token and not args.dry_run:
            print("Error: HF_TOKEN required. Set via --token or HF_TOKEN environment variable.")
            sys.exit(1)
        generate_reference_image(ref_type, ref_id, args.token or "", args.dry_run)
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
        args.page,
        args.dry_run
    )


if __name__ == "__main__":
    main()
