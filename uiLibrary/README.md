# Data Validation Tool - UI Component Library

Reusable React + TypeScript component library for the data validation tool frontend.

## Overview

Independent, buildable component library providing UI primitives for building configuration interfaces.

## Components

- **AppShell**: Main layout container with header/footer
- **Stepper**: Multi-step wizard navigation
- **TextField**: Text input with label
- **Select**: Dropdown select
- **FileDropzone**: Drag-and-drop file upload zone
- **MappingTable**: SSIS-style column mapping interface
- **InlineAlert**: Inline notification/alert component

## Tech Stack

- **React 19** (peer dependency)
- **TypeScript 5.9+**
- **No external UI libraries** - Pure React components

## Development

```bash
# Install dependencies
npm install

# Build library
npm run build

# Watch mode (for development)
npm run dev
```

## Usage in FE App

The `frontEnd/` app imports components via path alias:

```typescript
import { AppShell, Stepper, TextField } from "ui";
```

Configured in `frontEnd/vite.config.ts`:
```typescript
resolve: {
  alias: {
    'ui': path.resolve(__dirname, '../uiLibrary/src'),
  },
}
```

## Build Output

- `dist/index.js` - Compiled JavaScript
- `dist/index.d.ts` - TypeScript declarations

## Design Principles

- **Clean Code**: SOLID principles, single responsibility
- **Type Safety**: Full TypeScript coverage
- **No Dependencies**: Only React as peer dependency
- **Accessible**: Semantic HTML, keyboard navigation support
- **Reusable**: Components are generic and configurable

## Component API

All components follow consistent patterns:
- Props interfaces exported for TypeScript
- Controlled components (value + onChange)
- Optional labels and placeholders
- Error state support
- Consistent styling via inline styles (no CSS dependencies)
