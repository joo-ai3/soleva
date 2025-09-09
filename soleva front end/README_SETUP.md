# Soleva Frontend Setup Guide

## Quick Setup

### Option 1: Automated Setup (Recommended)

**Windows PowerShell:**
```powershell
.\setup.ps1
```

**Windows Command Prompt:**
```cmd
setup.bat
```

### Option 2: Manual Setup

1. **Prerequisites**
   - Node.js 18+ (Download from [nodejs.org](https://nodejs.org/))
   - npm 9+ (comes with Node.js)

2. **Clean Installation**
   ```bash
   # Remove existing dependencies
   rm -rf node_modules package-lock.json dist

   # Clear npm cache
   npm cache clean --force

   # Install dependencies
   npm install
   ```

3. **If installation fails:**
   ```bash
   # Try with legacy peer deps
   npm install --legacy-peer-deps

   # Or force installation
   npm install --force
   ```

## Available Commands

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server (localhost:3000) |
| `npm start` | Start development server (alias for dev) |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build (localhost:4173) |
| `npm run lint` | Run ESLint |
| `npm run lint:fix` | Fix ESLint errors automatically |
| `npm run type-check` | Check TypeScript types |
| `npm run clean` | Clean build artifacts |
| `npm run reinstall` | Clean reinstall all dependencies |

## Troubleshooting

### Common Issues

1. **npm commands hang or fail**
   - Run `npm cache clean --force`
   - Delete `node_modules` and `package-lock.json`
   - Run `npm install --legacy-peer-deps`

2. **Permission errors on Windows**
   - Run PowerShell as Administrator
   - Or use Command Prompt instead

3. **Port already in use**
   - Development server uses port 3000
   - Preview server uses port 4173
   - Change ports in `vite.config.ts` if needed

4. **Build errors**
   - Run `npm run type-check` to find TypeScript errors
   - Run `npm run lint:fix` to fix linting issues

### Environment Requirements

- **Node.js**: 18.0.0 or higher
- **npm**: 9.0.0 or higher
- **Operating System**: Windows, macOS, or Linux

### Development Workflow

1. Start development server:
   ```bash
   npm run dev
   ```

2. Open browser to `http://localhost:3000`

3. Make your changes (hot reload enabled)

4. Before committing:
   ```bash
   npm run lint:fix
   npm run type-check
   npm run build
   ```

### Production Build

1. Create production build:
   ```bash
   npm run build
   ```

2. Preview production build:
   ```bash
   npm run preview
   ```

3. Build files will be in the `dist/` folder

## Configuration Files

- `package.json` - Dependencies and scripts
- `vite.config.ts` - Vite configuration
- `tsconfig.json` - TypeScript configuration
- `tailwind.config.js` - Tailwind CSS configuration
- `.npmrc` - npm configuration
- `eslint.config.js` - ESLint configuration

## Support

If you're still having issues:

1. Check Node.js version: `node --version`
2. Check npm version: `npm --version`
3. Try the automated setup scripts
4. Clear everything and reinstall:
   ```bash
   npm run reinstall
   ```

## Performance Tips

- Use `npm ci` instead of `npm install` in production
- Enable dependency pre-bundling in development
- Use `--host` flag to access dev server from other devices
- Enable polling for file watching on some systems
