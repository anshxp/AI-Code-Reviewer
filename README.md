# Quick Start with NanoBanana Visualizations

## Before Running

1. Get your NanoBanana API key from [nanobanana.ai](https://nanobanana.ai)
2. Set the environment variable:

```bash
export NANOBANANA_API_KEY="sk-xxx-your-key-here"
```

## Run the App

```bash
cd "/home/anshxhhh/Desktop/projects/Mini AI"
python3 main.py
```

## Using the App

1. **Write Code** - Type or paste Python code in the editor
2. **Analyze** - Click "Analyze Code" to detect errors
3. **View Issues** - Click on any issue in the list
4. **Generate Visualization** - Click the "Visualization" tab, then "Generate Visualization"
5. **See AI Image** - NanoBanana will create a visual explanation of the error

## Example Workflow

```python
# Paste this broken code:
x = 5
if x = 5:      # ERROR: = instead of ==
    print("Equal")

# Click "Analyze Code"
# Click "Assignment in condition" from the issues list
# Click "Visualization" tab
# Click "Generate Visualization"
# Watch as NanoBanana creates a visual explanation!
```

## Error Types with Visualizations

- ✨ **Syntax errors** - Shows code editor with red highlights
- ✨ **Assignment vs Comparison** - Visual comparison of = vs ==
- ✨ **Undefined names** - Shows variable lifecycle
- ✨ **Infinite loops** - Visualizes loop flow and break conditions
- ✨ **No issues** - Celebratory success visualization

## Keyboard Shortcuts

- `Ctrl+A` - Select all code
- `Ctrl+V` - Paste code
- `Tab` - Next issue

## Need Help?

See [NANOBANA-SETUP.md](NANOBANA-SETUP.md) for detailed configuration options.
# AI-Code-Reviewer
