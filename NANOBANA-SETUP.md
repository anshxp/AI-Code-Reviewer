# NanoBanana API Setup Guide

## Overview
The Visual Beginner Code Reviewer uses **NanoBanana AI** to generate visual explanations of code errors. Each error gets a unique AI-generated image visualization.

## Getting a NanoBanana API Key

1. Visit [https://nanobanana.ai](https://nanobanana.ai)
2. Sign up for a free account
3. Navigate to your API keys section
4. Copy your API key

## Configuration Options

### Option 1: Environment Variable (Recommended)
Set the `NANOBANANA_API_KEY` environment variable before running the app:

**On Linux/Mac:**
```bash
export NANOBANANA_API_KEY="your-api-key-here"
/bin/python3 main.py
```

**On Windows (PowerShell):**
```powershell
$env:NANOBANANA_API_KEY="your-api-key-here"
python main.py
```

**On Windows (CMD):**
```cmd
set NANOBANANA_API_KEY=your-api-key-here
python main.py
```

### Option 2: Create a `.env` File
Create a `.env` file in the project root:
```
NANOBANANA_API_KEY=your-api-key-here
```

Then load it before running:
```bash
set -a
source .env
set +a
/bin/python3 main.py
```

### Option 3: Pass API Key in Code
Modify `app/ui.py` line where NanoBananaService is initialized:
```python
self.nanobanan = NanoBananaService(api_key="your-api-key-here")
```

## API Endpoints Supported

- **Stable Diffusion v1.5** (default)
- **Other models** available through NanoBanana (SDXL, etc.)

## Image Generation Parameters

The app uses these default settings:
- Resolution: 512x512 pixels
- Inference Steps: 20
- Guidance Scale: 7.5

## Caching

Generated images are cached in:
- Linux/Mac: `~/.cache/mini-ai-images/`
- Windows: `%APPDATA%/mini-ai-images/`

This prevents unnecessary API calls for the same error type.

## Troubleshooting

### "No image in API response"
- Check your API key is valid
- Verify you have API credits remaining
- Check internet connection

### "NanoBanana API error 401"
- API key is invalid or expired
- Set the correct API key and restart

### "Network error connecting to NanoBanana"
- Check internet connection
- Verify NanoBanana API is up: https://status.nanobanana.ai

## Free Tier Limits

NanoBanana free tier typically includes:
- Limited API calls per day
- Lower priority processing
- Standard image resolution

Upgrade to paid plan for unlimited usage.

## Using Without API Key

If no API key is provided, the app will still function but visualization tab will fail gracefully with an error message.

## API Documentation

For more details, visit: [https://docs.nanobanana.ai](https://docs.nanobanana.ai)
