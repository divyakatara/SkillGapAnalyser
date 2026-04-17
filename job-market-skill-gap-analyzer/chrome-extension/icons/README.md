# Icon Generation Guide

The extension requires icons in the following sizes:
- 16x16 (toolbar small)
- 32x32 (toolbar retina)
- 48x48 (extension management)
- 128x128 (Chrome Web Store)

## Quick Generation Using icon.svg

### Option 1: Using Online Tool (Easiest)
1. Go to https://www.iloveimg.com/svg-to-png or https://convertio.co/svg-png/
2. Upload `icon.svg`
3. Convert to PNG
4. Resize to 128x128, 48x48, 32x32, 16x16
5. Save as icon128.png, icon48.png, icon32.png, icon16.png

### Option 2: Using Inkscape (Free Software)
```bash
# Install Inkscape (https://inkscape.org/)

# Generate all sizes
inkscape icon.svg --export-filename=icon128.png --export-width=128
inkscape icon.svg --export-filename=icon48.png --export-width=48
inkscape icon.svg --export-filename=icon32.png --export-width=32
inkscape icon.svg --export-filename=icon16.png --export-width=16
```

### Option 3: Using ImageMagick
```bash
# Install ImageMagick (https://imagemagick.org/)

# Convert SVG to PNG at different sizes
convert -background none icon.svg -resize 128x128 icon128.png
convert -background none icon.svg -resize 48x48 icon48.png
convert -background none icon.svg -resize 32x32 icon32.png
convert -background none icon.svg -resize 16x16 icon16.png
```

### Option 4: Using rsvg-convert
```bash
# Install librsvg (includes rsvg-convert)
# Ubuntu/Debian: sudo apt-get install librsvg2-bin
# macOS: brew install librsvg

rsvg-convert -w 128 -h 128 icon.svg > icon128.png
rsvg-convert -w 48 -h 48 icon.svg > icon48.png
rsvg-convert -w 32 -h 32 icon.svg > icon32.png
rsvg-convert -w 16 -h 16 icon.svg > icon16.png
```

## Custom Icon Design

For a professional look, consider:

1. **Hiring a Designer** on Fiverr or Upwork ($20-100)
2. **Using Figma** (free design tool)
3. **Icon Generators**:
   - https://icon.kitchen/ - Free icon generator
   - https://favicon.io/ - Favicon and icon generator
   - https://realfavicongenerator.net/ - Complete icon pack

## Design Guidelines

### Chrome Extension Best Practices
- Use simple, recognizable symbols
- High contrast for visibility
- Works well at small sizes
- Looks good on light and dark backgrounds
- Represents the app's purpose

### Color Scheme
Current gradient: #667eea → #764ba2 (purple gradient)
- Consider using your brand colors
- Ensure good contrast with backgrounds

### Symbol Ideas
- ✅ Activity/pulse line (current) - represents analysis
- 📊 Bar chart - represents data/analytics
- 🎯 Target - represents job matching
- 💼 Briefcase - represents jobs
- 🔍 Magnifying glass - represents search/analysis

## Testing Icons

After generating:
1. Reload extension in chrome://extensions/
2. Check toolbar icon (should use 16px/32px)
3. Check extension management page (should use 48px)
4. Check Chrome Web Store preview (should use 128px)

## Current Status

The `icon.svg` file is provided as a template. 

**Before publishing to Chrome Web Store:**
- Replace icon.svg with your custom design
- Generate all PNG sizes
- Test at all sizes
- Ensure clarity and recognition
