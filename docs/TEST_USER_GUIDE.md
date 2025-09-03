# 🚀 Kyros Dashboard - Test User Guide

Welcome! This guide will help you quickly set up and test the Kyros Repurposer Dashboard locally.

## 📋 Quick Start (5 minutes)

### Prerequisites
- Node.js 18+ and npm
- Python 3.12+
- Git

### 1. Start the Backend API

```bash
# Navigate to the backend directory
cd backend

# Install dependencies
poetry install

# Start the API server
poetry run uvicorn main:app --reload --port 8000
```

The API will be available at: **http://localhost:8000**

### 2. Start the Frontend

Open a new terminal:

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at: **http://localhost:3001**

## 🎯 What You Can Test

### 1. Dashboard Overview
- **URL**: http://localhost:3001
- **Features**: KPI cards, recent jobs table, quick studio panel
- **Test**: Navigate around the dashboard to see the modern UI

### 2. Content Generation (Main Feature)
- **URL**: http://localhost:3001/studio
- **Test Content** (copy and paste this):
```
Artificial Intelligence is revolutionizing the way businesses operate, from automating routine tasks to providing deep insights through data analysis. Companies that embrace AI technologies are seeing significant improvements in efficiency, customer satisfaction, and competitive advantage. The key to successful AI implementation lies in understanding your specific use cases, ensuring data quality, and gradually scaling your AI initiatives. As we move forward, AI will become an essential tool for businesses of all sizes, not just tech giants.
```

**Steps to test**:
1. Paste the test content into the text area
2. Select channels: LinkedIn, Twitter, Newsletter
3. Choose tone: Professional
4. Click "Generate Content"
5. Watch the AI create channel-specific variants

### 3. Job Monitoring
- **URL**: http://localhost:3001/jobs
- **Features**: Job listing, search, filtering, status updates
- **Test**: View generated jobs and their status

### 4. Settings & Presets
- **URL**: http://localhost:3001/settings
- **Features**: Preset management, configuration
- **Test**: Create custom presets for different content types

## 🔧 Configuration Options

### Demo Mode (Default)
The app runs in demo mode by default, which means:
- ✅ No OpenAI API key required
- ✅ Mock data and responses
- ✅ All features work for testing
- ✅ No rate limits or quotas

### Real API Mode (Optional)
To test with real OpenAI API:

1. Get an OpenAI API key from https://platform.openai.com/api-keys
2. Create a `.env` file in the `backend` directory:
```bash
# In backend/.env
OPENAI_API_KEY=your_api_key_here
API_MODE=real
DEFAULT_MODEL=gpt-4o-mini
```

## 🎨 Key Features to Explore

### Content Generation
- **Multi-channel output**: LinkedIn, Twitter, Newsletter, Blog
- **Tone customization**: Professional, Casual, Technical, Engaging
- **Real-time generation**: Watch variants appear as they're created
- **Character counting**: Input validation and limits

### Variant Management
- **Inline editing**: Click "Edit" on any variant
- **Bulk selection**: Select multiple variants for export
- **Export options**: CSV, Word document formats
- **Copy to clipboard**: Quick copying of individual variants

### Dashboard Analytics
- **KPI tracking**: Jobs processed, hours saved, productivity metrics
- **Job history**: Complete audit trail of all content generation
- **Real-time updates**: Live status updates and notifications

## 🐛 Troubleshooting

### Common Issues

**Frontend won't start**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

**Backend won't start**:
```bash
cd backend
poetry install
poetry run uvicorn main:app --reload --port 8000
```

**API connection issues**:
- Check that backend is running on port 8000
- Check browser console for CORS errors
- Verify both services are running

### Port Conflicts
If ports 8000 or 3001 are in use:
- Backend: `uvicorn main:app --reload --port 8001`
- Frontend: `npm run dev -- --port 3002`

## 📊 Test Scenarios

### Scenario 1: Basic Content Generation
1. Go to Studio page
2. Paste test content
3. Select 2-3 channels
4. Generate and review variants
5. Edit one variant
6. Export selected variants

### Scenario 2: Job Management
1. Generate multiple jobs with different content
2. Go to Jobs page
3. Search and filter jobs
4. View job details
5. Check job status updates

### Scenario 3: Preset Management
1. Go to Settings page
2. Create a new preset
3. Use the preset in content generation
4. Edit and delete presets

## 🎯 Success Criteria

After testing, you should have experienced:
- ✅ Modern, responsive UI design
- ✅ Smooth content generation workflow
- ✅ Real-time job monitoring
- ✅ Variant editing and export
- ✅ Settings and customization
- ✅ Mobile-responsive design

## 📞 Support

If you encounter any issues:
1. Check the browser console for errors
2. Check the terminal running the backend for API errors
3. Verify both services are running on the correct ports
4. Try refreshing the browser

## 🚀 Next Steps

Once you've tested the basic functionality:
1. Try different content types and lengths
2. Test all channel combinations
3. Explore the preset system
4. Test the export functionality
5. Check mobile responsiveness

Happy testing! 🎉
