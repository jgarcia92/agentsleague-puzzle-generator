#!/usr/bin/env python3
"""
Puzzle Generator – AI-powered riddle and puzzle creator for Agents League Creative Apps track.

Built with GitHub Copilot assistance for creative problem-solving and code structure.
"""

import argparse
import json
import random
from typing import List, Dict, Literal

# Puzzle templates (can be expanded with Copilot's help)
PUZZLE_TEMPLATES = {
    "riddle": [
        {
            "question": "I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I?",
            "answer": "An echo",
            "difficulty": "easy",
            "category": "general"
        },
        {
            "question": "I have cities but no houses, forests but no trees, and water but no fish. What am I?",
            "answer": "A map",
            "difficulty": "easy",
            "category": "general"
        },
    ],
    "logic": [
        {
            "question": "Three switches control three light bulbs in another room. You can toggle the switches, but can only enter the room once. How do you determine which switch controls which bulb?",
            "answer": "Toggle switch 1 for 10 minutes (heating the bulb), then turn it off. Toggle switch 2 on, leave switch 3 off. Enter the room: warm bulb = switch 1, on bulb = switch 2, off bulb = switch 3.",
            "difficulty": "hard",
            "category": "logic"
        },
        {
            "question": "A man walks into a room and shoots himself. Another man walks in the same room but does not shoot himself and survives. How?",
            "answer": "The first man shot himself in a mirror (suicide simulation); the second man shoots a real gun at a target or prop in the room.",
            "difficulty": "medium",
            "category": "logic"
        },
    ],
    "math": [
        {
            "question": "If you have a bowl with 6 apples and you take away 4, how many do you have?",
            "answer": "4 (the ones you took away)",
            "difficulty": "easy",
            "category": "math"
        },
        {
            "question": "Two trains are running towards each other on the same track. Train A is moving at 60 mph and Train B at 40 mph. When they are 100 miles apart, a bird flies between them at 80 mph. The bird keeps flying until the trains collide. How far does the bird travel?",
            "answer": "80 miles (the trains meet in 1 hour, and the bird flies at 80 mph for 1 hour)",
            "difficulty": "hard",
            "category": "math"
        },
    ],
    "wordplay": [
        {
            "question": "What word becomes shorter the more letters you add to it?",
            "answer": "Short (s-hort, sh-ort, sho-rt, short)",
            "difficulty": "easy",
            "category": "wordplay"
        },
    ],
}

DIFFICULTIES = ["easy", "medium", "hard"]
CATEGORIES = ["general", "logic", "math", "wordplay"]


def generate_puzzle(
    difficulty: Literal["easy", "medium", "hard"] = "medium",
    category: str = "general"
) -> Dict:
    """
    Generate a random puzzle based on difficulty and category.
    
    Args:
        difficulty: Puzzle difficulty level (easy, medium, hard)
        category: Puzzle category (general, logic, math, wordplay)
        
    Returns:
        Dictionary with question, answer, difficulty, and category
    """
    # Validate inputs
    if difficulty not in DIFFICULTIES:
        raise ValueError(f"Difficulty must be one of: {DIFFICULTIES}")
    if category not in CATEGORIES:
        raise ValueError(f"Category must be one of: {CATEGORIES}")
    
    # Find matching puzzles
    matching_puzzles = []
    for puzzle_type, puzzles in PUZZLE_TEMPLATES.items():
        for puzzle in puzzles:
            if puzzle["difficulty"] == difficulty and puzzle["category"] == category:
                matching_puzzles.append(puzzle)
    
    # Fallback: if no exact match, get any puzzle of the requested difficulty
    if not matching_puzzles:
        for puzzle_type, puzzles in PUZZLE_TEMPLATES.items():
            for puzzle in puzzles:
                if puzzle["difficulty"] == difficulty:
                    matching_puzzles.append(puzzle)
    
    # Return random puzzle or a default
    if matching_puzzles:
        return random.choice(matching_puzzles)
    else:
        return {
            "question": "What has a head and a tail but no body?",
            "answer": "A coin",
            "difficulty": difficulty,
            "category": category
        }


def generate_puzzles(
    count: int = 3,
    difficulty: Literal["easy", "medium", "hard"] = "medium",
    category: str = "general"
) -> List[Dict]:
    """
    Generate multiple puzzles.
    
    Args:
        count: Number of puzzles to generate
        difficulty: Puzzle difficulty level
        category: Puzzle category
        
    Returns:
        List of puzzles
    """
    if count < 1 or count > 100:
        raise ValueError("Count must be between 1 and 100")
    
    # Build pools to sample without replacement, preferring exact matches first
    exact_pool: List[Dict] = []
    same_diff_pool: List[Dict] = []
    any_pool: List[Dict] = []

    for puzzles in PUZZLE_TEMPLATES.values():
        for p in puzzles:
            any_pool.append(p)
            if p["difficulty"] == difficulty:
                same_diff_pool.append(p)
                if p["category"] == category:
                    exact_pool.append(p)

    # Helper to sample unique items from a pool excluding already chosen
    def take_from(pool: List[Dict], chosen: List[Dict], k: int) -> None:
        remaining = [p for p in pool if p not in chosen]
        if not remaining or k <= 0:
            return
        if len(remaining) <= k:
            chosen.extend(remaining)
        else:
            chosen.extend(random.sample(remaining, k))

    selected: List[Dict] = []
    # 1) exact category + difficulty
    take_from(exact_pool, selected, count)
    # 2) broaden to same difficulty across categories
    if len(selected) < count:
        take_from(same_diff_pool, selected, count - len(selected))
    # 3) broaden to any remaining templates
    if len(selected) < count:
        take_from(any_pool, selected, count - len(selected))

    # If still short (very small template set), allow replacement as last resort
    while len(selected) < count:
        selected.append(random.choice(any_pool))

    # Trim and shuffle to avoid a fixed first puzzle
    selected = selected[:count]
    random.shuffle(selected)
    return selected


def format_output(puzzles: List[Dict], output_format: str = "text") -> str:
    """
    Format puzzles for display.
    
    Args:
        puzzles: List of puzzle dictionaries
        output_format: Output format (text or json)
        
    Returns:
        Formatted string
    """
    if output_format == "json":
        return json.dumps(puzzles, indent=2)
    
    # Text format
    output = []
    for i, puzzle in enumerate(puzzles, 1):
        output.append(f"✨ Puzzle {i}: {puzzle.get('category', 'general').title()} ({puzzle.get('difficulty', 'medium').upper()})")
        output.append(f"   Q: {puzzle['question']}")
        output.append(f"   A: {puzzle['answer']}")
        output.append("")
    
    return "\n".join(output)


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="🧩 Puzzle Generator – AI-powered riddle and puzzle creator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python puzzle_generator.py --count 5 --difficulty medium
  python puzzle_generator.py --count 3 --difficulty hard --category logic
  python puzzle_generator.py --count 1 --format json
        """
    )
    
    parser.add_argument(
        "--count",
        type=int,
        default=3,
        help="Number of puzzles to generate (1-100, default: 3)"
    )
    parser.add_argument(
        "--difficulty",
        choices=DIFFICULTIES,
        default="medium",
        help="Puzzle difficulty level (default: medium)"
    )
    parser.add_argument(
        "--category",
        choices=CATEGORIES,
        default="general",
        help="Puzzle category (default: general)"
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    
    args = parser.parse_args()
    
    try:
        # Generate puzzles
        puzzles = generate_puzzles(
            count=args.count,
            difficulty=args.difficulty,
            category=args.category
        )
        
        # Format and display
        output = format_output(puzzles, args.format)
        print(f"\n🧩 Puzzle Generator – Demo Run")
        print("─" * 48)
        print(output)
        
    except ValueError as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
