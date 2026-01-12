# Building the Web Application (Future)

The Council AI web application is currently served as inline HTML by FastAPI. This document outlines plans for implementing Vite-based builds with code splitting.

## Current State

The web application currently:
- Runs directly from FastAPI with inline HTML
- Works out of the box without build steps
- Is suitable for development and small-scale usage

## Planned Enhancements

### Build System (Vite)

Configuration files exist for future implementation:
- `vite.config.js` - Build configuration
- `package.json` - Node dependencies and scripts

### Planned Features

1. **Code Splitting**
   - Separate chunks for core, UI, and lazy modules
   - Mobile-specific code loaded only on mobile devices

2. **Lazy Loading**
   - Deferred loading of non-critical resources
   - Dynamic imports for on-demand modules

3. **Performance Optimization**
   - Minification and tree shaking
   - Asset optimization
   - Caching strategies

## Running the Web App (Current)

```bash
# Install the package
pip install -e ".[web]"

# Run the web server
council web --reload
```

The application will be available at `http://127.0.0.1:8000`.

## Future Build Process (Planned)

Once implemented, the build process will be:

```bash
# Install Node dependencies
npm install

# Development mode with hot reload
npm run dev

# Production build
npm run build

# Run FastAPI with production build
council web
```

## Performance Targets (Goals)

- Initial Load: < 50KB
- Time to Interactive: < 2s on 3G
- First Contentful Paint: < 1s
- Largest Contentful Paint: < 2.5s
- Total Bundle Size: < 200KB

## Notes

- The current inline HTML approach works well for development
- Build system implementation is planned for future optimization
- See `LAZY_LOADING_IMPLEMENTATION.md` for detailed plans

---

*Status: Planning Phase - Current implementation uses inline HTML*
