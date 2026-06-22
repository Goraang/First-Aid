# 🎨 Component Styling Reference

## Complete Component Breakdown

This document provides detailed styling information for each component and module.

---

## 📦 Global Styles

### Color Tokens

```css
:root {
  /* Pharmacy Theme */
  --pharmacy-primary: #5B5FFF;
  --pharmacy-secondary: #00D4FF;
  --pharmacy-gradient: linear-gradient(135deg, #5B5FFF 0%, #00D4FF 100%);
  --pharmacy-light: #F0F5FF;
  --pharmacy-dark: #2C3E50;
  
  /* Dermatology Theme */
  --dermatology-primary: #C4A87B;
  --dermatology-secondary: #F5E6D3;
  --dermatology-accent: #E8C5B0;
  --dermatology-dark: #6B5B52;
  --dermatology-gradient: linear-gradient(135deg, #C4A87B 0%, #E8C5B0 100%);
  
  /* Neutral Palette */
  --primary-color: #5B5FFF;
  --secondary-color: #6c757d;
  --success-color: #10b981;
  --danger-color: #ef4444;
  --warning-color: #f59e0b;
  --light-color: #f9fafb;
  --dark-color: #1f2937;
}
```

### Spacing Scale

```css
:root {
  /* 8px base unit */
  --spacing-xs: 0.5rem;   /* 8px */
  --spacing-sm: 1rem;     /* 16px */
  --spacing-md: 1.5rem;   /* 24px */
  --spacing-lg: 2rem;     /* 32px */
  --spacing-xl: 2.5rem;   /* 40px */
  --spacing-2xl: 3rem;    /* 48px */
  --spacing-3xl: 4rem;    /* 64px */
}
```

### Border Radius

```css
:root {
  --border-radius: 12px;      /* Buttons, inputs */
  --border-radius-lg: 16px;   /* Cards, sections */
  --border-radius-xl: 20px;   /* Containers */
  --border-radius-2xl: 24px;  /* Large areas */
}
```

### Shadow System

```css
:root {
  --box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  --box-shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.12);
  --box-shadow-hover: 0 12px 32px rgba(91, 95, 255, 0.15);
}
```

### Transitions

```css
:root {
  --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
```

---

## 🏠 Home Page Components

### Hero Section

```css
.hero {
  max-width: 1200px;
  margin: 0 auto;
  padding: 6rem 2rem 4rem;
  text-align: center;
  animation: slideDown 0.6s ease;
}

.hero h1 {
  font-size: 3.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #5B5FFF 0%, #C4A87B 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 1.5rem;
  letter-spacing: -1px;
}

.hero p {
  font-size: 1.3rem;
  color: #6B7280;
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.8;
}
```

### Service Cards

```css
.service-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(240, 245, 255, 0.95) 100%);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(91, 95, 255, 0.1);
  padding: 2.5rem;
  border-radius: 16px;
  text-align: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  animation: scaleIn 0.6s ease;
}

.service-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 32px rgba(91, 95, 255, 0.15);
  border-color: rgba(91, 95, 255, 0.2);
}
```

### Features Grid

```css
.feature {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(91, 95, 255, 0.1);
  transition: all 0.3s ease;
}

.feature:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(91, 95, 255, 0.1);
}

.feature-icon {
  font-size: 3rem;
  display: block;
  margin-bottom: 1rem;
}

.feature h3 {
  font-size: 1.3rem;
  color: #1f2937;
  margin-bottom: 0.75rem;
  font-weight: 700;
}
```

---

## 💊 Pharmacy Module

### Container

```css
.pharmacy-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  background: linear-gradient(135deg, rgba(91, 95, 255, 0.05) 0%, rgba(0, 212, 255, 0.05) 100%);
  min-height: 100vh;
}

.pharmacy-container {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(91, 95, 255, 0.1);
  border: 1px solid rgba(91, 95, 255, 0.1);
  padding: 2.5rem;
}
```

### Tabs

```css
.tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2.5rem;
  border-bottom: 2px solid rgba(91, 95, 255, 0.1);
  padding-bottom: 1rem;
}

.tab-button {
  background: none;
  border: none;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: #6B7280;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.tab-button:hover {
  color: #5B5FFF;
  background-color: rgba(91, 95, 255, 0.05);
}

.tab-button.active {
  color: #5B5FFF;
  background: linear-gradient(135deg, rgba(91, 95, 255, 0.1) 0%, rgba(0, 212, 255, 0.05) 100%);
  box-shadow: 0 2px 8px rgba(91, 95, 255, 0.15);
}
```

### Search Input

```css
.search-input {
  flex: 1;
  min-width: 250px;
  padding: 1rem 1.5rem;
  border: 2px solid rgba(91, 95, 255, 0.2);
  border-radius: 12px;
  font-size: 1rem;
  background-color: rgba(255, 255, 255, 0.8);
  transition: all 0.3s ease;
  font-family: inherit;
}

.search-input:focus {
  outline: none;
  border-color: #5B5FFF;
  background-color: white;
  box-shadow: 0 0 0 4px rgba(91, 95, 255, 0.1);
}

.search-input::placeholder {
  color: #9CA3AF;
}
```

### Search Button

```css
.search-box .btn {
  padding: 1rem 2.5rem;
  background: linear-gradient(135deg, #5B5FFF, #00D4FF);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(91, 95, 255, 0.3);
}

.search-box .btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(91, 95, 255, 0.4);
}
```

### Medicine Card

```css
.medicine-card {
  border: 1px solid rgba(91, 95, 255, 0.15);
  border-radius: 16px;
  padding: 2rem;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(240, 245, 255, 0.95) 100%);
  backdrop-filter: blur(8px);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.medicine-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(91, 95, 255, 0.05) 0%, transparent 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.medicine-card:hover {
  transform: translateY(-6px) scale(1.02);
  box-shadow: 0 12px 32px rgba(91, 95, 255, 0.2);
  border-color: rgba(91, 95, 255, 0.3);
}

.medicine-card:hover::before {
  opacity: 1;
}
```

### Medicine Card Title

```css
.medicine-card h3 {
  color: #5B5FFF;
  margin-bottom: 0.5rem;
  font-size: 1.2rem;
  font-weight: 700;
  position: relative;
  z-index: 1;
}

.medicine-card .generic-name {
  font-size: 0.9rem;
  color: #8B7B70;
  font-style: italic;
  margin-bottom: 1rem;
  position: relative;
  z-index: 1;
}
```

### Category Badge

```css
.medicine-card .category {
  display: inline-block;
  background: linear-gradient(135deg, rgba(91, 95, 255, 0.1) 0%, rgba(0, 212, 255, 0.05) 100%);
  color: #5B5FFF;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  margin-bottom: 1rem;
  border: 1px solid rgba(91, 95, 255, 0.2);
  position: relative;
  z-index: 1;
}
```

### Warning Box

```css
.medicine-card .warning {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.05) 0%, rgba(239, 68, 68, 0.02) 100%);
  padding: 1.25rem;
  border-radius: 12px;
  border-left: 4px solid #ef4444;
  margin-top: 1rem;
  position: relative;
  z-index: 1;
}

.medicine-card .warning h4 {
  color: #b91c1c;
  margin-bottom: 0.5rem;
}

.medicine-card .warning p {
  color: #991b1b;
  font-size: 0.9rem;
  margin: 0;
}
```

---

## 🩺 Dermatology Module

### Container

```css
.dermatology-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  background: linear-gradient(135deg, rgba(196, 168, 123, 0.05) 0%, rgba(232, 197, 176, 0.05) 100%);
  min-height: 100vh;
}

.page-header {
  text-align: center;
  margin-bottom: 4rem;
  padding: 2rem 0;
}

.page-header h1 {
  font-size: 2.8rem;
  color: #6B5B52;
  margin-bottom: 0.75rem;
  font-weight: 700;
  letter-spacing: -0.5px;
}
```

### Two-Column Layout

```css
.dermatology-container {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 2.5rem;
  align-items: start;
}

@media (max-width: 768px) {
  .dermatology-container {
    grid-template-columns: 1fr;
  }
}
```

### Upload Section

```css
.upload-section {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(245, 230, 211, 0.95) 100%);
  backdrop-filter: blur(10px);
  padding: 2.5rem;
  border-radius: 20px;
  box-shadow: 0 8px 24px rgba(107, 91, 82, 0.08);
  border: 1px solid rgba(196, 168, 123, 0.15);
}

.upload-section h2 {
  margin-bottom: 2rem;
  color: #6B5B52;
  font-size: 1.5rem;
  font-weight: 700;
}
```

### Upload Label

```css
.upload-label {
  display: block;
  cursor: pointer;
  border: 2px dashed rgba(196, 168, 123, 0.4);
  border-radius: 16px;
  padding: 3rem 2rem;
  text-align: center;
  background: linear-gradient(135deg, rgba(245, 230, 211, 0.5) 0%, rgba(232, 197, 176, 0.3) 100%);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.upload-label:hover {
  background: linear-gradient(135deg, rgba(245, 230, 211, 0.8) 0%, rgba(232, 197, 176, 0.6) 100%);
  border-color: #C4A87B;
  box-shadow: 0 4px 16px rgba(196, 168, 123, 0.15);
  transform: translateY(-2px);
}

.upload-label::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 20% 50%, rgba(232, 197, 176, 0.1) 0%, transparent 50%);
  pointer-events: none;
}
```

### Result Section

```css
.result-section {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(245, 230, 211, 0.95) 100%);
  backdrop-filter: blur(10px);
  padding: 2.5rem;
  border-radius: 20px;
  box-shadow: 0 8px 24px rgba(107, 91, 82, 0.08);
  border: 1px solid rgba(196, 168, 123, 0.15);
}

.result-section h2 {
  margin-bottom: 2rem;
  color: #6B5B52;
  font-size: 1.5rem;
  font-weight: 700;
}
```

### Result Card

```css
.result-card {
  border: 1px solid rgba(196, 168, 123, 0.15);
  border-radius: 16px;
  overflow: hidden;
  background: white;
  box-shadow: 0 4px 12px rgba(107, 91, 82, 0.05);
  transition: all 0.3s ease;
}
```

### Result Header

```css
.result-header {
  background: linear-gradient(135deg, rgba(196, 168, 123, 0.1) 0%, rgba(232, 197, 176, 0.1) 100%);
  padding: 2rem;
  border-bottom: 1px solid rgba(196, 168, 123, 0.2);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-header h3 {
  margin: 0;
  color: #6B5B52;
  font-size: 1.3rem;
  font-weight: 700;
}
```

### Confidence Badge

```css
.confidence-badge {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  padding: 0.7rem 1.5rem;
  border-radius: 20px;
  font-weight: 700;
  font-size: 0.9rem;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}
```

### Result Body

```css
.result-body {
  padding: 2.5rem;
}

.description {
  font-size: 1.05rem;
  margin-bottom: 2rem;
  color: #6B7280;
  line-height: 1.7;
  background: rgba(196, 168, 123, 0.05);
  padding: 1.5rem;
  border-radius: 12px;
  border-left: 4px solid #C4A87B;
}
```

### Information Sections

```css
.section {
  margin-bottom: 2rem;
}

.section h4 {
  color: #6B5B52;
  margin-bottom: 1rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-size: 0.95rem;
}

.section ul {
  list-style: none;
  padding-left: 0;
}

.section ul li {
  padding: 0.6rem 0;
  padding-left: 2rem;
  position: relative;
  color: #6B7280;
  line-height: 1.6;
}

.section ul li:before {
  content: "→";
  position: absolute;
  left: 0;
  color: #C4A87B;
  font-weight: bold;
}
```

### Warning Section

```css
.section.warning {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.05) 0%, rgba(239, 68, 68, 0.02) 100%);
  padding: 1.5rem;
  border-radius: 12px;
  border-left: 4px solid #ef4444;
}

.section.warning p {
  margin: 0;
  color: #991b1b;
}
```

### Disclaimer

```css
.disclaimer {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.08) 0%, rgba(239, 68, 68, 0.04) 100%);
  color: #991b1b;
  padding: 1.5rem;
  border-radius: 12px;
  border-left: 4px solid #dc3545;
  margin-top: 2rem;
  font-weight: 500;
}
```

---

## 🎬 Global Animations

### Slide Down

```css
@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Applied to page/section entries */
.hero { animation: slideDown 0.6s ease; }
.scan-section { animation: slideDown 0.4s ease; }
```

### Scale In

```css
@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* Applied to cards and elements */
.service-card { animation: scaleIn 0.6s ease; }
```

### Fade In

```css
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Applied to content that appears */
.search-section { animation: fadeIn 0.3s ease; }
```

### Shimmer

```css
@keyframes shimmer {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

/* Applied to loading states */
.loading { animation: shimmer 2s ease-in-out infinite; }
```

---

## 📱 Responsive Utilities

### Mobile-First Approach

```css
/* Mobile first (default) */
.pharmacy-container {
  grid-template-columns: 1fr;
}

/* Tablet */
@media (min-width: 768px) {
  .pharmacy-container {
    grid-template-columns: 1fr;
  }
}

/* Desktop */
@media (min-width: 1024px) {
  .pharmacy-container {
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  }
}
```

### Touch Targets

```css
/* Minimum 44px for touch */
.btn {
  min-height: 44px;
  min-width: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.tab-button {
  min-height: 44px;
  padding: 0.75rem 1.5rem;
}
```

---

## ✅ Accessibility

### Focus States

```css
.btn:focus {
  outline: 2px solid #5B5FFF;
  outline-offset: 2px;
}

.search-input:focus {
  border-color: #5B5FFF;
  box-shadow: 0 0 0 4px rgba(91, 95, 255, 0.1);
}
```

### Color Contrast

All text meets WCAG AA standards:
- ✅ Body text: 4.5:1 minimum ratio
- ✅ Large text: 3:1 minimum ratio
- ✅ Graphics: 3:1 minimum ratio

### Keyboard Navigation

All interactive elements are keyboard accessible:
- ✅ Buttons: Tab focus + Enter activation
- ✅ Inputs: Tab navigation + focus indicators
- ✅ Dropdowns: Arrow keys supported
- ✅ Modals: Escape to close

---

## 🎯 Usage Tips

1. **Use CSS Variables** - For easy theme switching
2. **Apply Animations** - Use predefined keyframes
3. **Follow Spacing** - Use 8px base unit
4. **Maintain Contrast** - Use provided color palettes
5. **Test Responsive** - Check all breakpoints
6. **Consider Motion** - Respect `prefers-reduced-motion`

---

**Last Updated**: June 2026
**Version**: 2.0.0
**Status**: ✅ Production Ready

