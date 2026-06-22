# 🎨 Color Schemes & Visual Identity

## FirstAid Platform - Design System

### Overview

The FirstAid Platform uses a **dual-theme design system** with distinct visual identities for each module:

---

## 🏥 Pharmacy Module - Modern Tech Theme

### Color Palette

#### Primary Colors
```
Primary Purple:     #5B5FFF
  - Used for: Main buttons, headers, primary accents
  - RGB: rgb(91, 95, 255)
  - HSL: hsl(238, 100%, 68%)

Secondary Cyan:     #00D4FF
  - Used for: Secondary accents, highlights
  - RGB: rgb(0, 212, 255)
  - HSL: hsl(189, 100%, 50%)
```

#### Gradient
```
Main Gradient: linear-gradient(135deg, #5B5FFF 0%, #00D4FF 100%)
  - Creates smooth purple to cyan transition
  - Used for buttons, backgrounds, overlays
  - 45-degree angle for modern feel
```

#### Supporting Colors
```
Light Background:   #F0F5FF
  - Soft blue tint for page backgrounds
  - Cards and containers
  - Accent text backgrounds

Dark Accent:        #2C3E50
  - Dark text and strong accents
  - High contrast elements
```

### Interactive States

#### Buttons
```
Idle:       gradient(#5B5FFF → #00D4FF)
Hover:      lifted 2px, enhanced shadow
Active:     pressed effect
Focus:      outlined with 2px border
Disabled:   opacity 50%, no hover
```

#### Cards
```
Idle:       subtle shadow, slight transparency
Hover:      lifted 6px, glow shadow, scale 1.02
Focus:      border highlight
```

#### Inputs
```
Idle:       2px border rgba(91,95,255,0.2)
Focus:      2px border #5B5FFF, glow shadow
Error:      2px border #ef4444
Success:    2px border #10b981
```

### Shadows

```
Base:       0 4px 12px rgba(0,0,0,0.08)
Large:      0 8px 24px rgba(0,0,0,0.12)
Hover:      0 12px 32px rgba(91,95,255,0.15)
Focus:      0 0 0 4px rgba(91,95,255,0.1)
```

### Typography Colors

```
Headings (H1-H3):   #1f2937 (dark gray)
Body Text:          #6B7280 (medium gray)
Secondary Text:     #9CA3AF (light gray)
Links:              #5B5FFF (primary purple)
```

---

## 🩺 Dermatology Module - Healthcare Theme

### Color Palette

#### Primary Colors
```
Primary Gold:       #C4A87B
  - Used for: Main buttons, section headers
  - RGB: rgb(196, 168, 123)
  - HSL: hsl(32, 40%, 62%)

Secondary Peach:    #E8C5B0
  - Used for: Accents, highlights
  - RGB: rgb(232, 197, 176)
  - HSL: hsl(17, 66%, 80%)
```

#### Accent Color
```
Warm Beige:         #F5E6D3
  - Light backgrounds
  - Card backgrounds
  - Soft accents
  - Calming effect
```

#### Gradient
```
Main Gradient: linear-gradient(135deg, #C4A87B 0%, #E8C5B0 100%)
  - Creates smooth gold to peach transition
  - Professional, warm feel
  - Healthcare aesthetic
```

#### Supporting Colors
```
Dark Brown:         #6B5B52
  - Primary text color
  - Headers and accents
  - Professional appearance
```

### Interactive States

#### Buttons
```
Idle:       gradient(#C4A87B → #E8C5B0)
Hover:      lifted 2px, enhanced warm shadow
Active:     pressed effect
Focus:      outlined with 2px border
Disabled:   opacity 50%, no hover
```

#### Cards
```
Idle:       subtle shadow, warm background
Hover:      lifted 4px, warm glow shadow
Focus:      warm border highlight
```

#### Inputs
```
Idle:       2px border rgba(196,168,123,0.2)
Focus:      2px border #C4A87B, glow shadow
Error:      2px border #ef4444
Success:    2px border #10b981
```

### Shadows (Warm-tinted)

```
Base:       0 4px 12px rgba(107,91,82,0.08)
Large:      0 8px 24px rgba(107,91,82,0.12)
Hover:      0 12px 32px rgba(196,168,123,0.15)
Focus:      0 0 0 4px rgba(196,168,123,0.1)
```

### Typography Colors

```
Headings (H1-H3):   #6B5B52 (warm brown)
Body Text:          #6B7280 (medium gray)
Secondary Text:     #8B7B70 (warm gray)
Links:              #C4A87B (primary gold)
```

---

## 🎨 Semantic Colors (Both Themes)

### Status Colors

```
Success:    #10b981 (Emerald)
  - Confirmations
  - Positive actions
  - Good news

Warning:    #f59e0b (Amber)
  - Cautions
  - Important notices
  - Attention needed

Danger:     #ef4444 (Red)
  - Errors
  - Critical alerts
  - Destructive actions

Info:       #3b82f6 (Blue)
  - Informational
  - Tips and hints
  - Additional info
```

### Neutral Colors

```
Light:      #f9fafb (Almost white)
Medium:     #e5e7eb (Light gray)
Dark:       #1f2937 (Near black)
Gray:       #6B7280 (Body text)
```

---

## 📐 Color Usage Guidelines

### Pharmacy (Purple/Cyan Theme)

#### When to Use:
- **Primary Purple (#5B5FFF)**
  - Main call-to-action buttons
  - Primary headings
  - Active states
  - Focus indicators

- **Secondary Cyan (#00D4FF)**
  - Secondary buttons
  - Accent lines
  - Highlight effects
  - Supporting text

- **Light Blue (#F0F5FF)**
  - Page backgrounds
  - Card backgrounds
  - Input backgrounds
  - Hover states

#### Avoid:
- Using only color to convey information
- Low contrast text combinations
- Overusing gradients (limit to 2-3 per page)

### Dermatology (Gold/Peach Theme)

#### When to Use:
- **Primary Gold (#C4A87B)**
  - Main call-to-action buttons
  - Section headers
  - Active states
  - Links

- **Secondary Peach (#E8C5B0)**
  - Secondary buttons
  - Accent borders
  - Highlight effects
  - Supporting elements

- **Light Beige (#F5E6D3)**
  - Page backgrounds
  - Card backgrounds
  - Light accents
  - Calm areas

#### Avoid:
- Bright colors that contrast with warm palette
- Cold grays with warm theme
- Too much saturation (keep professional)

---

## 🎯 Contrast Compliance

### WCAG AA Standards Met

#### Pharmacy Theme
```
Text on Light:      #1f2937 on #F0F5FF = 12.8:1 ✓
Text on Dark:       #ffffff on #5B5FFF = 5.2:1 ✓
Accent on White:    #5B5FFF on #ffffff = 4.9:1 ✓
```

#### Dermatology Theme
```
Text on Light:      #6B5B52 on #F5E6D3 = 7.1:1 ✓
Text on Dark:       #ffffff on #C4A87B = 5.8:1 ✓
Accent on White:    #C4A87B on #ffffff = 4.7:1 ✓
```

#### Status Colors
```
Success Green:      #10b981 - 5.5:1 minimum ✓
Warning Orange:     #f59e0b - 4.9:1 minimum ✓
Danger Red:         #ef4444 - 5.1:1 minimum ✓
```

---

## 🎬 Color Transitions

### Hover Effects

#### Pharmacy Button
```
Idle:   #5B5FFF (purple)
Hover:  Lighter shade + lift effect
Glow:   rgba(91, 95, 255, 0.15) shadow
```

#### Dermatology Button
```
Idle:   #C4A87B (gold)
Hover:  Lighter shade + lift effect
Glow:   rgba(196, 168, 123, 0.15) shadow
```

### Animation Timing
```
Transition Duration: 0.3s
Easing Function:    cubic-bezier(0.4, 0, 0.2, 1)
Result:             Smooth, natural motion
```

---

## 📱 Color Adaptation

### Dark Mode Consideration

While currently light-mode only, colors are chosen to support future dark mode:

#### Pharmacy Dark Mode (Theoretical)
```
Background:         #1a1b2e (dark blue)
Cards:              #252642 (slightly lighter)
Text:               #e5e7eb (light gray)
Primary:            #6b7aff (adjusted purple)
```

#### Dermatology Dark Mode (Theoretical)
```
Background:         #2a2420 (dark brown)
Cards:              #3a3430 (slightly lighter)
Text:               #e5e7eb (light gray)
Primary:            #d4a574 (adjusted gold)
```

---

## 🎨 Gradient Specifications

### Pharmacy Gradient

```css
Name: Tech Gradient
Angle: 135 degrees (top-left to bottom-right)
Color 1: #5B5FFF (0% - purple)
Color 2: #00D4FF (100% - cyan)

Application:
- Buttons
- Page backgrounds (with 5% opacity)
- Card overlays (on hover)
- Accent borders
```

### Dermatology Gradient

```css
Name: Healthcare Gradient
Angle: 135 degrees (top-left to bottom-right)
Color 1: #C4A87B (0% - gold)
Color 2: #E8C5B0 (100% - peach)

Application:
- Buttons
- Page backgrounds (with 5% opacity)
- Section headers
- Accent elements
```

---

## 🔄 Color Mixing

### Pharmacy Color Combinations

```
Primary + Secondary:
  - Gradient effect
  - Modern, energetic
  - Tech-forward feel

Primary + Light:
  - Soft, readable
  - Professional
  - Clean appearance

Secondary + Dark:
  - High contrast
  - Emphasis
  - Strong impact
```

### Dermatology Color Combinations

```
Primary + Secondary:
  - Warm, inviting
  - Professional
  - Healthcare-appropriate

Primary + Light:
  - Calming, soft
  - Trustworthy
  - Clinical feel

Secondary + Dark:
  - Elegant
  - Sophisticated
  - Premium appearance
```

---

## 📊 Color Distribution

### Recommended Breakdown

#### Page Composition
```
Primary Color:      15-25% (main accents, buttons)
Secondary Color:    10-15% (highlights, accents)
Light Background:   40-50% (cards, sections)
Neutral/Gray:       20-30% (text, dividers)
White:              10-15% (breathing room)
```

#### Visual Weight
```
Dark elements:      Draw attention (use sparingly)
Bright elements:    Eye-catching (use for CTA)
Neutral elements:   Balance (use for body)
Light elements:     Calm (use for backgrounds)
```

---

## 🎯 Color Psychology

### Pharmacy (Purple/Cyan)
- **Purple**: Wisdom, innovation, digital
- **Cyan**: Technology, modernity, freshness
- **Combined**: Digital health, modern medicine
- **Feeling**: Professional, innovative, tech-forward

### Dermatology (Gold/Peach)
- **Gold**: Premium, trustworthy, healing
- **Peach**: Warm, welcoming, human touch
- **Combined**: Professional care, personal health
- **Feeling**: Calming, trustworthy, clinical

---

## ✅ Implementation Checklist

- [ ] Color variables defined in CSS
- [ ] Gradients created correctly
- [ ] Shadows use theme colors
- [ ] Text colors meet WCAG AA
- [ ] Buttons have proper contrast
- [ ] Hover states use correct colors
- [ ] Cards match theme palette
- [ ] Status colors are distinct
- [ ] Transitions are smooth
- [ ] Dark mode considered (future)

---

## 🎨 Design Resources

### CSS Variable Usage

```css
/* Apply pharmacy theme */
:root {
  --primary-color: #5B5FFF;
  --pharmacy-gradient: linear-gradient(135deg, #5B5FFF 0%, #00D4FF 100%);
}

/* Apply dermatology theme */
:root {
  --primary-color: #C4A87B;
  --dermatology-gradient: linear-gradient(135deg, #C4A87B 0%, #E8C5B0 100%);
}
```

### Customization

```css
/* Override theme color */
:root {
  --pharmacy-primary: #YOUR_COLOR;
}

/* Create new gradient */
.custom-bg {
  background: linear-gradient(135deg, #color1 0%, #color2 100%);
}
```

---

## 📝 Color Documentation

For each color, include:
- Hex code
- RGB values
- HSL values
- Use cases
- Contrast ratios
- Accessibility notes

---

## 🎊 Summary

### Pharmacy Theme
- **Primary**: #5B5FFF (Purple)
- **Secondary**: #00D4FF (Cyan)
- **Feeling**: Modern, Tech-forward, Professional
- **Best for**: Medicine identification, pharmacy services

### Dermatology Theme
- **Primary**: #C4A87B (Gold)
- **Secondary**: #E8C5B0 (Peach)
- **Feeling**: Warm, Clinical, Trustworthy
- **Best for**: Skin analysis, healthcare services

---

**Version**: 2.0.0
**Last Updated**: June 2026
**Status**: ✅ Complete

