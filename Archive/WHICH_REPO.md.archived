# Which Repository Should I Use?

## Quick Answer

**For most users: Work in `council-ai`**

- `council-ai` = Main repository with all the core functionality
- `council-ai-personal` = Your personal customizations (personas, configs, settings)

## Detailed Explanation

### `council-ai` (Main Repository)

- **Contains**: All the core Council AI code, web interface, CLI, personas, domains
- **Use this for**:
  - Running the web server
  - Using the CLI commands
  - Development and bug fixes
  - Installing and using Council AI

### `council-ai-personal` (Personal Overlay)

- **Contains**: Your personal customizations:
  - Custom personas you've created
  - Personal configuration files
  - Custom domain presets
  - Personal scripts
- **Use this for**:
  - Storing your personal customizations
  - Version controlling your personal configs
  - Sharing your custom personas with others

## How They Work Together

1. **Install/use Council AI from `council-ai`**:

   ```bash
   cd council-ai
   python bin/launch-council.py
   ```

2. **Integrate your personal configs** (one-time setup):

   ```bash
   cd council-ai
   council personal integrate
   ```

   This copies your custom configs from `council-ai-personal` into `~/.config/council-ai/`

3. **After integration**: Council AI automatically uses both:
   - Built-in personas/domains from `council-ai`
   - Your personal personas/configs from `council-ai-personal`

## Launch Options

### Standard Launch (uses built-in + integrated personal configs)

```bash
cd council-ai
python bin/launch-council.py
```

### Launch with Personal Integration (auto-detects council-ai-personal)

```bash
cd council-ai
bin/launch-council-personal.bat  # Windows
# or
python bin/launch-council.py --personal  # If supported
```

## Workflow Summary

1. **Development/Bug fixes**: Work in `council-ai`
2. **Personal customizations**: Edit files in `council-ai-personal/personal/`
3. **Running the app**: Always run from `council-ai`
4. **After changing personal configs**: Re-run `council personal integrate` to sync changes

## Still Confused?

**Default workflow**: Just use `council-ai` for everything. Your personal configs will be automatically detected and integrated if `council-ai-personal` exists as a sibling directory.
