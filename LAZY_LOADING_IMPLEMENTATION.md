# Lazy Loading and Code Splitting - Implementation Guide

## Overview

This document outlines the plan for implementing lazy loading and code splitting for the Council AI web application using Vite as the build system.

## Current Status

- ✅ Vite configuration file created (`vite.config.js`)
- ✅ Package.json with build scripts
- ✅ Basic project structure
- ⏳ Build implementation pending
- ⏳ Asset organization pending
- ⏳ Production deployment pending

## Planned Implementation

### Phase 1: Build System Setup

**Tasks:**
- Configure Vite for code splitting
- Set up output directory structure
- Add build scripts to package.json
- Configure FastAPI to serve static files

**Files:**
- `vite.config.js` - ✅ Created
- `package.json` - ✅ Created
- `src/council_ai/webapp/app.py` - Needs updates

### Phase 2: Code Splitting

**Planned Structure:**

```
src/council_ai/webapp/
├── index.html              # Entry HTML template
├── app.py                  # FastAPI app
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
```

### Phase 3: Lazy Loading Strategy

**CSS Lazy Loading:**
- Critical CSS inlined in HTML for instant rendering
- Main CSS imported as ES module
- Mobile CSS lazy loaded based on viewport size

**JavaScript Lazy Loading:**
- Render module lazy loaded when consultation completes
- Mobile module lazy loaded based on device detection
- Use dynamic `import()` for deferred loading

### Phase 4: FastAPI Integration

**Required Changes:**
1. Detect production build existence
2. Serve built HTML from `static/index.html`
3. Fall back to inline HTML in development
4. Add static file serving for `/assets/*`

### Phase 5: Performance Optimization

**Targets:**
- Initial Load: < 50KB (HTML + critical CSS + core JS)
- Time to Interactive: < 2s on 3G
- First Contentful Paint: < 1s
- Largest Contentful Paint: < 2.5s
- Total Bundle Size: < 200KB (all chunks)

**Optimizations:**
- Tree shaking via Vite
- CSS code splitting
- Minification with terser
- Manual chunk splitting
- Browser caching strategy

## Build Commands (Planned)

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

## Next Steps

1. **Organize Assets**: Move CSS/JS into structured directories
2. **Implement Modules**: Create separate JS modules
3. **Update FastAPI**: Add static file serving logic
4. **Build & Test**: Run production build and test
5. **Performance Audit**: Run Lighthouse and optimize

## Notes

- Configuration files are in place but implementation is pending
- The current webapp uses inline HTML which works for development
- Building for production will improve load times and performance
- This is a planned enhancement, not yet implemented

## Dependencies

Required packages (already in `package.json`):
- `vite` >= 5.4.20 - Build tool and dev server

---

*Status: Planning Phase - Implementation Pending*
