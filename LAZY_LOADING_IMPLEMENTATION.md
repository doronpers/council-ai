# Lazy Loading and Code Splitting Implementation

## Summary

Successfully implemented comprehensive lazy loading and code splitting for the Council AI web application using Vite as the build system.

## Implementation Complete

### ✅ Phase 1: Build System Setup

- **Vite Configuration**: Created `vite.config.js` with code splitting configuration
- **Project Structure**: Organized assets into `assets/css/` and `assets/js/` directories
- **Dependencies**: Added `vite>=5.0.0` to `pyproject.toml` and created `package.json`
- **Build Output**: Configured to output to `src/council_ai/webapp/static/`

### ✅ Phase 2: Code Splitting

**CSS Splitting:**

- `critical.css`: Above-the-fold styles (inline in HTML)
- `main.css`: Core application styles (loaded immediately)
- `mobile.css`: Mobile-specific styles (lazy loaded on mobile devices)

**JavaScript Splitting:**

- `core/utils.js`: Utility functions (escapeHtml)
- `core/api.js`: API client (loadInfo, submitConsultation)
- `ui/render.js`: Result rendering (lazy loaded when first consultation completes)
- `lazy/mobile.js`: Mobile features (lazy loaded on mobile devices)
- `main.js`: Entry point with dynamic imports

### ✅ Phase 3: Lazy Loading Implementation

**CSS Lazy Loading:**

- Critical CSS inlined in HTML for instant rendering
- Main CSS imported in main.js (Vite processes it)
- Mobile CSS lazy loaded via dynamic import in mobile.js module

**JavaScript Lazy Loading:**

- Render module (`ui/render.js`) lazy loaded when first consultation completes
- Mobile module (`lazy/mobile.js`) lazy loaded based on viewport size
- API info loading deferred using `requestIdleCallback` when available

**Content Lazy Loading:**

- Results section auto-scrolls on mobile after rendering
- Mobile CSS only loads on mobile devices

### ✅ Phase 4: FastAPI Integration

- Updated `app.py` to detect production build
- Serves built HTML from `static/index.html` in production
- Falls back to inline HTML in development mode
- Static file serving for built assets (`/assets/*`)
- API endpoints unchanged (`/api/info`, `/api/consult`)

### ✅ Phase 5: Performance Optimizations

**Critical Rendering Path:**

- Critical CSS inlined (< 3KB)
- Main CSS loaded as module import (Vite optimizes)
- JavaScript loaded as ES modules with defer

**Bundle Optimization:**

- Vite configured for tree shaking
- CSS code splitting enabled
- Minification with terser
- Manual chunk splitting (core, ui, lazy)

**Caching Strategy:**

- API responses cached in memory
- Static assets can be cached by browser/CDN

## File Structure

```text
src/council_ai/webapp/
├── index.html              # Entry HTML template
├── app.py                  # FastAPI app (updated)
├── assets/
│   ├── css/
│   │   ├── critical.css    # Critical styles (inline)
│   │   ├── main.css        # Main stylesheet
│   │   └── mobile.css      # Mobile styles (lazy)
│   └── js/
│       ├── main.js         # Entry point
│       ├── core/
│       │   ├── utils.js    # Utilities
│       │   └── api.js      # API client
│       ├── ui/
│       │   └── render.js   # Rendering (lazy)
│       └── lazy/
│           └── mobile.js    # Mobile features (lazy)
└── static/                 # Build output (gitignored)
    ├── index.html
    └── assets/
        ├── css/
        └── js/
```

## Build Commands

```bash
# Install dependencies
npm install

# Development (with hot reload)
npm run dev

# Production build
npm run build

# Preview production build
npm run preview
```

## Performance Targets

- **Initial Load**: < 50KB (HTML + critical CSS + core JS)
- **Time to Interactive**: < 2s on 3G
- **First Contentful Paint**: < 1s
- **Largest Contentful Paint**: < 2.5s
- **Total Bundle Size**: < 200KB (all chunks combined)

## Key Features

1. **Code Splitting**: Automatic chunk splitting (core, ui, lazy)
2. **Lazy Loading**: Mobile CSS and features only load on mobile
3. **Critical CSS**: Inline critical styles for instant rendering
4. **ES Modules**: Modern JavaScript with dynamic imports
5. **Vite Integration**: Fast builds and optimized production output
6. **Development/Production Modes**: Automatic detection and fallback

## Next Steps

1. Run `npm install` to install Vite
2. Run `npm run build` to create production build
3. Test with `council web` command
4. Run Lighthouse audit to verify performance improvements
5. Monitor bundle sizes and optimize further if needed

## Notes

- The old inline HTML (`_INDEX_HTML`) is kept as a fallback for development
- Static files are served from `/assets/*` in production
- Mobile CSS is conditionally loaded based on viewport size
- All lazy loading is handled via dynamic `import()` statements
