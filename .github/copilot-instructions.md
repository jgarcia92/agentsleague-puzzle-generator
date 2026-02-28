# GitHub Copilot Guidelines – Puzzle Generator

## 📋 Project Vision
Build an AI-powered puzzle and riddle generator for Agents League Creative Apps track, showcasing effective use of GitHub Copilot for creative development.

## 🤖 How to Use Copilot in This Project

### 1. **Feature Expansion**
Open VS Code, go to `puzzle_generator.py`, and use Copilot Chat:
- Query: *"Add 5 new hard-difficulty riddles to PUZZLE_TEMPLATES"*
- Query: *"Generate category suggestions for puzzle types"*
- Query: *"Suggest new puzzle categories and add them to CATEGORIES"*

### 2. **API Enhancement**
Extend the puzzle generator with a REST API:
- Query: *"Convert this CLI to a FastAPI server with endpoints for /puzzles and /generate"*
- Query: *"Add database support for persisting user-solved puzzles"*

### 3. **Code Optimization**
- Query: *"Refactor generate_puzzles() for performance with large counts"*
- Query: *"Add caching for frequently requested puzzle combinations"*

### 4. **Testing & Validation**
- Query: *"Generate pytest test cases for puzzle_generator.py"*
- Query: *"Create edge case tests for invalid inputs (count=-1, difficulty='xyz')"*

### 5. **UI/UX Improvements**
- Query: *"Create a simple web UI using Flask to display puzzles"*
- Query: *"Add color formatting and emojis to the CLI output"*

## 🎯 Development Workflow

1. **Open the project in VS Code**
   ```bash
   code C:\Users\jaime\agentsleague-puzzle-generator
   ```

2. **Use Copilot Chat** (`Ctrl+Shift+I`):
   - Highlight code and ask Copilot to explain, refactor, or extend it
   - Use natural language prompts for feature ideas

3. **Use Copilot Inline** (`Ctrl+I`):
   - Select a function or class
   - Ask for tests, documentation, or performance improvements

4. **Document Changes**
   - Update README.md with the new feature
   - Note which Copilot queries led to the enhancement

## 📝 Copilot Usage Logging

When expanding features with Copilot, add comments in the code:
```python
# AI-Assisted by Copilot: Added dynamic puzzle templates (Chat query: "Generate 10 riddles...")
# Copilot suggested: Using dict comprehensions for efficient filtering
```

This helps demonstrate Copilot's role during evaluation.

## 🚀 Suggested Next Features (with Copilot)

- **Puzzle Difficulty Algorithm**: Ask Copilot to create a scoring system
- **User Statistics**: Persist puzzle attempts and success rates
- **Multiplayer Mode**: Copilot suggestions for turn-based puzzle sharing
- **AI Hints**: Use Copilot to suggest puzzle-solving hints
- **Mobile App**: Ask Copilot for React Native or Flutter scaffolding

## ✨ Quick Copilot Prompts to Try

```
1. "Create a web API endpoint that generates and returns 10 puzzles in JSON format"
2. "Add leaderboard functionality to track which puzzles are solved most"
3. "Refactor the puzzle_generator module to support streaming puzzle generation"
4. "Generate comprehensive docstrings for all functions using Google style"
5. "Create a CLI command to export puzzles as a CSV file"
```

---

**Remember:** The goal is to showcase meaningful, intentional use of Copilot—not just code completion. Document your process!
