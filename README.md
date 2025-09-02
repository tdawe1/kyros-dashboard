# Kyros Repurposer Dashboard

A modern React + Tailwind dashboard for the kyros Repurposer, replacing the existing Streamlit UI with a sleek, responsive interface that matches the kyros.solutions aesthetic.

## 🚀 Features

- **Modern Dashboard**: Clean, responsive UI with navy gradient header and teal accents
- **Content Generation**: Transform source content into multiple channel formats (LinkedIn, Twitter, Newsletter, Blog)
- **Variant Management**: Edit, accept, copy, and export generated content variants
- **Job Monitoring**: Track and manage content repurposing jobs
- **Preset Management**: Create and manage custom content generation presets
- **Real-time Updates**: Live KPI tracking and job status updates

## 🛠️ Tech Stack

### Frontend
- **React 19** with Vite for fast development
- **Tailwind CSS** for styling with custom kyros color scheme
- **React Router** for navigation
- **TanStack Query** for API state management
- **Lucide React** for icons
- **Axios** for HTTP requests

### Backend
- **FastAPI** for API endpoints
- **Pydantic** for data validation
- **Uvicorn** for ASGI server

## 📁 Project Structure

```
kyros-dashboard/
├── ui/                          # Frontend React application
│   ├── src/
│   │   ├── pages/              # Page components
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Jobs.jsx
│   │   │   ├── Studio.jsx
│   │   │   └── Settings.jsx
│   │   ├── ui/                 # Reusable UI components
│   │   │   ├── Sidebar.jsx
│   │   │   ├── Topbar.jsx
│   │   │   ├── KPICards.jsx
│   │   │   ├── JobTable.jsx
│   │   │   ├── StudioPanel.jsx
│   │   │   ├── VariantCard.jsx
│   │   │   ├── EditorModal.jsx
│   │   │   └── VariantsGallery.jsx
│   │   ├── hooks/              # Custom React hooks
│   │   │   ├── useKPIs.js
│   │   │   ├── useJobs.js
│   │   │   ├── useGenerate.js
│   │   │   └── usePresets.js
│   │   ├── lib/                # API client and utilities
│   │   │   └── api.js
│   │   └── layouts/            # Layout components
│   │       └── AppShell.jsx
│   ├── package.json
│   └── tailwind.config.js
├── api/                        # Backend FastAPI application
│   ├── main.py                 # FastAPI app with mock endpoints
│   └── requirements.txt
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+

### Frontend Setup

1. Navigate to the UI directory:
```bash
cd ui
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Backend Setup

1. Navigate to the API directory:
```bash
cd api
```

2. Create a virtual environment:
```bash
python -m venv .venv
```

3. Activate the virtual environment:
```bash
# On Linux/Mac
source .venv/bin/activate

# On Windows
.venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Start the FastAPI server:
```bash
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### Environment Variables

Create a `.env` file in the `ui` directory:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## 📱 Pages & Features

### Dashboard (`/`)
- KPI cards showing jobs processed, hours saved, average edit time, and export bundles
- Recent jobs table with sortable columns
- Quick studio panel for fast content generation

### Job Monitor (`/jobs`)
- Comprehensive job listing with search and filtering
- Real-time job status updates
- Bulk actions for job management

### Repurposer Studio (`/studio`)
- Source content input with character count validation
- Channel selection (LinkedIn, Twitter, Newsletter, Blog)
- Tone and preset configuration
- Generated variants gallery with inline editing
- Export functionality for selected variants

### Settings (`/settings`)
- Preset management (create, edit, delete)
- Glossary and terms management
- API configuration
- Export settings

## 🎨 Design System

### Colors
- **Primary Navy**: `#1e1b4b` to `#0f1724` (gradient)
- **Accent Teal**: `#07c6b7`
- **Background**: `#042f2e` (navy-950)
- **Cards**: `#1e293b` (navy-800) with `#334155` (navy-700) borders

### Typography
- System default fonts with 16px base size
- Font weights: 400 (normal), 500 (medium), 600 (semibold), 700 (bold)

### Components
- Rounded corners: 8px (lg) for buttons, 12px (xl) for cards
- Shadows: `shadow-sm` for subtle elevation
- Transitions: 150ms ease-in-out for hover states

## 🔌 API Endpoints

### Health & Status
- `GET /api/health` - Health check

### KPIs
- `GET /api/kpis` - Get dashboard KPIs

### Jobs
- `GET /api/jobs` - List all jobs
- `GET /api/jobs/{job_id}` - Get specific job

### Content Generation
- `POST /api/generate` - Generate content variants
- `POST /api/export` - Export selected variants

### Presets
- `GET /api/presets` - List presets
- `POST /api/presets` - Create preset
- `PUT /api/presets/{preset_id}` - Update preset
- `DELETE /api/presets/{preset_id}` - Delete preset

## 🧪 Testing

### Frontend Tests
```bash
cd ui
npm test
```

### API Tests
```bash
cd api
python -m pytest
```

## 🚀 Deployment

### Automatic Deployment
The project is configured for automatic deployment using GitHub Actions:

- **Production**: Merging to `main` branch automatically deploys to production
- **Staging**: Pushing to `develop` or `feature/*` branches deploys to staging
- **Quality Checks**: All PRs run comprehensive tests and security scans

### Manual Deployment

#### Frontend (Vercel)
1. Connect your GitHub repository to Vercel
2. Set environment variables:
   - `VITE_API_BASE_URL`: Your API base URL
3. Deploy from the `main` branch

#### Backend (Railway/Render)
1. Deploy the `api/` directory
2. Set environment variables as needed
3. Update frontend API base URL

### Setup Instructions
See [Deployment Guide](docs/DEPLOYMENT.md) for complete setup instructions including:
- GitHub Actions configuration
- Required secrets and environment variables
- Platform-specific setup (Vercel, Railway, Render)
- Troubleshooting guide

## 📝 Development Notes

- The current implementation uses mock data for demonstration
- Real backend integration requires updating API endpoints in `ui/src/lib/api.js`
- All components are responsive and follow accessibility best practices
- The design system is consistent with kyros.solutions branding

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is part of the kyros Repurposer suite. All rights reserved.
# Test change for branch protection setup
