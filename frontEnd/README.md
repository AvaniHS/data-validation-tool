# Data Validation Tool - Frontend Web Application

React + TypeScript web application for building validation configuration files through an intuitive UI.

## Features

- **File Upload & Parsing**: Upload CSV, Excel (.xlsx), or JSON files and automatically extract column names
- **Visual Column Mapping**: Drag-and-drop or select-based mapping interface (SSIS-style)
- **Join Keys Configuration**: Define join keys with type specifications
- **Additional Columns**: Select extra columns to include from each file
- **Metrics Configuration**: Define metric lists for numeric comparison
- **Aggregation Settings**: Configure aggregation rules (optional)
- **Config Management**: 
  - Upload existing JSON config files
  - Download generated config files
  - Download config template

## Tech Stack

- **React 19** with TypeScript
- **Vite** for build tooling
- **UI Component Library** (`../uiLibrary`) - Reusable components
- **File Parsing**: 
  - `papaparse` for CSV
  - `xlsx` for Excel
  - Native JSON parsing

## Development

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Deployment

### Static Hosting (Recommended)

The app builds to static files in `dist/`. Deploy to:

- **Netlify**: Connect repo, set build command: `npm run build`, publish directory: `dist`
- **Vercel**: Connect repo, framework preset: Vite, output directory: `dist`
- **AWS S3 + CloudFront**: Upload `dist/` contents to S3 bucket, configure CloudFront
- **GitHub Pages**: Use GitHub Actions to build and deploy `dist/` to `gh-pages` branch

### Docker (Alternative)

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Environment Variables

No environment variables required for basic deployment. All file parsing happens client-side.

## Project Structure

```
frontEnd/
├── src/
│   ├── App.tsx              # Main app component with stepper
│   ├── app/
│   │   ├── config/          # Config types and utilities
│   │   ├── parsing/         # File parsing logic (CSV/Excel/JSON)
│   │   └── utils/           # Utilities (download, logger)
│   └── main.tsx             # Entry point
├── public/
│   └── config_template.json # Template config for download
└── dist/                     # Production build output
```

## Usage

1. **Select Data Sources**: Choose file format, number of files, upload files
2. **Configure Mapping**: Map columns between files, set join keys
3. **Review & Download**: Preview generated config JSON and download

The generated config file can be used with the Python CLI tool:
```bash
python run_validation.py --config <downloaded-config.json>
```

## Multi-User Support

The app is stateless and can handle multiple concurrent users. No authentication required. Each user session is independent.

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

File parsing uses modern browser APIs. Large files (>50MB) may cause performance issues.
