# Visual Effects Technical Guide

Deep technical reference for the favicon effects engine.

## The Perception of Quality

Why do some icons look "professional" and others look "amateur"? The answer lies in subtle visual cues that mimic real-world lighting and depth.

### Real-World Analogies

| Effect | Real-World Equivalent | Why It Works |
|--------|----------------------|--------------|
| Drop shadow | Object lifted from surface | Creates depth hierarchy |
| Highlight | Light source from above | Matches natural lighting |
| Inner glow | Ambient light reflection | Adds dimensionality |
| Noise/grain | Material texture | Prevents "digital" flatness |

## Effect Implementation Details

### Drop Shadow

The shadow creates the illusion that the icon floats above the background.

**Parameters**:
- **Color**: Black with 20-40% opacity
- **Offset**: 3-8% of icon size, typically downward
- **Blur**: 10-20% of icon size

**Canvas Implementation**:
```javascript
ctx.shadowColor = 'rgba(0, 0, 0, 0.25)';
ctx.shadowBlur = size * 0.12;
ctx.shadowOffsetY = size * 0.04;
// Draw shape - shadow appears automatically
```

**Pillow Implementation**:
```python
# Create shadow layer from alpha channel
shadow = Image.new('RGBA', size, (0,0,0,0))
shadow_alpha = original.split()[3]
shadow_color = Image.new('RGBA', size, (0,0,0,int(255*0.3)))
shadow.paste(shadow_color, (0, offset), shadow_alpha)
shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
# Composite behind original
result = Image.alpha_composite(shadow, original)
```

### Highlight Gradient

Simulates top-down lighting, making the icon appear three-dimensional.

**Parameters**:
- **Top**: White with 20-50% opacity
- **Middle**: Transparent
- **Bottom**: Black with 10-20% opacity

**Canvas Implementation**:
```javascript
const gradient = ctx.createLinearGradient(0, 0, 0, size);
gradient.addColorStop(0, 'rgba(255,255,255,0.4)');
gradient.addColorStop(0.5, 'rgba(255,255,255,0)');
gradient.addColorStop(1, 'rgba(0,0,0,0.15)');
ctx.globalCompositeOperation = 'overlay';
ctx.fillStyle = gradient;
ctx.fill();
```

### Inner Glow

Creates depth within the shape, as if light is reflecting inside.

**Parameters**:
- **Center**: Bright (white with low opacity)
- **Edges**: Dark (black with low opacity)
- **Center offset**: Slightly above geometric center (top lighting)

**Canvas Implementation**:
```javascript
const glowGradient = ctx.createRadialGradient(
  size/2, size*0.4, 0,           // Center slightly above middle
  size/2, size/2, size*0.6       // Extends to edges
);
glowGradient.addColorStop(0, 'rgba(255,255,255,0.3)');
glowGradient.addColorStop(0.6, 'rgba(255,255,255,0)');
glowGradient.addColorStop(1, 'rgba(0,0,0,0.15)');
```

### Noise/Grain

Adds subtle texture that prevents color banding and digital flatness.

**Parameters**:
- **Intensity**: 3-10% of full range
- **Alpha**: Very low (10-30 out of 255)
- **Blend mode**: Overlay or soft-light

**Canvas Implementation**:
```javascript
const noiseData = ctx.createImageData(size, size);
for (let i = 0; i < noiseData.data.length; i += 4) {
  const noise = (Math.random() - 0.5) * 255 * intensity;
  noiseData.data[i] = 128 + noise;     // R
  noiseData.data[i+1] = 128 + noise;   // G
  noiseData.data[i+2] = 128 + noise;   // B
  noiseData.data[i+3] = 25;            // Very low alpha
}
ctx.globalCompositeOperation = 'overlay';
ctx.putImageData(noiseData, 0, 0);
```

## Multi-Stop Gradients

Professional gradients use 3+ color stops for smoother transitions.

**Basic (2-stop)**:
```javascript
gradient.addColorStop(0, color1);
gradient.addColorStop(1, color2);
```

**Professional (4-stop)**:
```javascript
gradient.addColorStop(0, color1);
gradient.addColorStop(0.3, blendColors(color1, color2, 0.3));
gradient.addColorStop(0.7, blendColors(color1, color2, 0.7));
gradient.addColorStop(1, color2);
```

The extra stops create smoother perceptual transitions.

## Optical Centering

Letters aren't mathematically centered—they're optically adjusted.

**Problem**: Mathematical center places "T" too low visually.

**Solution**: Shift text up by 1-3% of icon size.

```javascript
// Get text metrics
const metrics = ctx.measureText(letter);
const textHeight = metrics.actualBoundingBoxAscent + metrics.actualBoundingBoxDescent;

// Mathematical center
const mathY = size / 2;

// Optical center (shift up slightly)
const opticalY = mathY - (size * 0.02);

ctx.fillText(letter, size/2, opticalY);
```

## Size-Specific Adjustments

Effects should scale appropriately—or be disabled at small sizes.

| Size | Shadow | Highlight | Inner Glow | Noise |
|------|--------|-----------|------------|-------|
| 16px | Off | Off | Off | Off |
| 32px | Light | Light | Off | Off |
| 64px | Full | Full | Light | Off |
| 128px+ | Full | Full | Full | Full |

**Implementation**:
```javascript
function getEffectsForSize(size) {
  if (size < 32) {
    return { shadow: 0, highlight: 0, innerGlow: 0, noise: 0 };
  }
  if (size < 64) {
    return { shadow: 0.5, highlight: 0.5, innerGlow: 0, noise: 0 };
  }
  return { shadow: 1, highlight: 1, innerGlow: 1, noise: 1 };
}
```

## Color Space Considerations

### Perceptual Uniformity

HSL is better than RGB for color manipulation because it matches human perception.

```javascript
// Lighten a color perceptually
function lighten(hex, amount) {
  const hsl = hexToHsl(hex);
  hsl.l = Math.min(1, hsl.l + amount);
  return hslToHex(hsl);
}
```

### Gradient Color Transitions

RGB gradients can produce muddy intermediate colors. For better results:

1. Convert to HSL
2. Interpolate hue, saturation, lightness separately
3. Convert back to RGB

```javascript
function blendColorsHsl(color1, color2, ratio) {
  const hsl1 = hexToHsl(color1);
  const hsl2 = hexToHsl(color2);
  
  return hslToHex({
    h: hsl1.h + (hsl2.h - hsl1.h) * ratio,
    s: hsl1.s + (hsl2.s - hsl1.s) * ratio,
    l: hsl1.l + (hsl2.l - hsl1.l) * ratio
  });
}
```

## Composite Operations

Understanding blend modes is key to layered effects.

| Mode | Effect | Use For |
|------|--------|---------|
| `source-over` | Normal stacking | Default |
| `overlay` | Preserves shadows/highlights | Noise, texture |
| `multiply` | Darkens | Shadows |
| `screen` | Lightens | Highlights |
| `soft-light` | Subtle overlay | Gentle effects |

```javascript
ctx.globalCompositeOperation = 'overlay';
// Draw highlight/noise layer
ctx.globalCompositeOperation = 'source-over'; // Reset
```

## Anti-Aliasing Techniques

### High-Resolution Rendering

Render at 2-4x target size, then downscale:

```javascript
const scale = 4;
const largeCanvas = createCanvas(size * scale, size * scale);
// Draw at large size
const result = downscale(largeCanvas, size);
```

### Lanczos Resampling

For best downscaling quality:

```python
# Pillow
result = large_image.resize((size, size), Image.Resampling.LANCZOS)
```

## Performance Optimization

### Canvas Performance

- **Batch operations**: Group draws before any state changes
- **Avoid recreating gradients**: Cache gradient objects
- **Use offscreen canvas**: For complex compositions

```javascript
// Cache the gradient
const cachedGradient = createGradient(size, colors);

// Use for multiple icons
sizes.forEach(s => {
  draw(cachedGradient.resize(s));
});
```

### Pillow Performance

- **Use numpy for noise**: Much faster than pixel loops
- **Composite fewer layers**: Merge where possible

```python
import numpy as np

def fast_noise(size, intensity):
    noise = np.random.random((size, size)) * 255 * intensity
    noise = noise.astype(np.uint8)
    return Image.fromarray(noise, mode='L')
```

## Debugging Visual Issues

### Banding in Gradients

**Symptom**: Visible steps in gradient instead of smooth transition.
**Cause**: 8-bit color depth, large uniform areas.
**Fix**: Add subtle noise (3-5%) to break up bands.

### Muddy Colors

**Symptom**: Gradient intermediate colors look gray/brown.
**Cause**: RGB interpolation through gray zone.
**Fix**: Use HSL interpolation, or choose colors on similar hue.

### Fuzzy Edges

**Symptom**: Icon edges look blurry/soft.
**Cause**: Anti-aliasing without proper scaling.
**Fix**: Render at 4x, use Lanczos downscaling.

### Shadow Cutoff

**Symptom**: Shadow appears clipped at edges.
**Cause**: Shadow extends beyond canvas bounds.
**Fix**: Add padding, or offset shadow inward.

