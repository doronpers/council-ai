# Building the Web Application

The Council AI web application uses Vite for building and code splitting.

## Prerequisites

1. Install Node.js (v18 or higher)
2. Install npm dependencies:
   ```bash
   npm install
   ```

## Development

Run the Vite dev server (with hot reload):
```bash
npm run dev
```

The dev server will run on `http://localhost:5173` and proxy API requests to the FastAPI server (expected on `http://localhost:8000`).

## Building for Production

Build the web assets:
```bash
npm run build
```

This will:
- Bundle and minify JavaScript
- Extract and optimize CSS
- Split code into chunks (core, UI, lazy modules)
- Output to `src/council_ai/webapp/static/`

## Running the Production Build

After building, start the FastAPI server:
```bash
council web
```

The FastAPI app will automatically detect the built assets and serve them. If no build exists, it falls back to the inline HTML (development mode).

## Performance Targets

- **Initial Load**: < 50KB (HTML + critical CSS + core JS)
- **Time to Interactive**: < 2s on 3G
- **First Contentful Paint**: < 1s
- **Largest Contentful Paint**: < 2.5s
- **Total Bundle Size**: < 200KB (all chunks combined)

## Code Splitting

The build creates the following chunks:
- **core**: Utility functions and API client
- **ui**: Result rendering (lazy loaded)
- **lazy**: Mobile-specific features (lazy loaded on mobile devices)

## Lazy Loading

- Mobile CSS is lazy loaded only on mobile devices
- Render module is lazy loaded when first consultation completes
- Mobile features are lazy loaded based on viewport size
