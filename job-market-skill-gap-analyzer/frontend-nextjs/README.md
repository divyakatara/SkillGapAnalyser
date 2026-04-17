# Job Market Skill Gap Analyzer - Next.js Frontend

Modern, interactive frontend built with Next.js 14, React, TypeScript, and Tailwind CSS.

## Features

✨ **Interactive Dashboard**
- Real-time skill demand visualization
- Responsive bar and pie charts with Recharts
- Dynamic filtering and search
- Adjustable number of displayed skills (5-50)

🔍 **Smart Search**
- Search by skill name or category
- Instant filtering
- Highlighted results

📊 **Synchronized Charts**
- Bar chart and pie chart update together
- Filter applies to all visualizations
- Smooth animations

🎯 **Gap Analysis**
- Upload resume for skill analysis
- Identify missing skills
- Personalized recommendations

## Getting Started

### Prerequisites
- Node.js 18+ and npm/yarn
- FastAPI backend running on http://localhost:8000

### Installation

```bash
cd frontend-nextjs
npm install
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
frontend-nextjs/
├── app/
│   ├── layout.tsx          # Root layout with navigation
│   ├── page.tsx            # Home page (Market Overview)
│   ├── gap-analysis/       # Gap Analysis page
│   └── globals.css         # Global styles
├── components/
│   ├── Navbar.tsx          # Navigation bar
│   ├── StatsCard.tsx       # Statistics cards
│   ├── SearchBar.tsx       # Search component
│   ├── SkillDemandChart.tsx    # Bar chart
│   └── SkillCategoryChart.tsx  # Pie chart
├── public/
│   └── data/               # JSON data fallback
└── package.json
```

## API Integration

The frontend connects to your FastAPI backend:

- `GET /api/skill-demand` - Get skill demand data
- `GET /api/job-stats` - Get statistics
- `POST /api/analyze-resume` - Analyze resume

## Customization

### Colors
Edit `tailwind.config.js`:
```js
colors: {
  primary: '#1f77b4',    // Main brand color
  secondary: '#ff7f0e',  // Secondary color
}
```

### Charts
Charts are built with Recharts. Customize in:
- `components/SkillDemandChart.tsx`
- `components/SkillCategoryChart.tsx`

## Technologies

- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Recharts** - Charts and graphs
- **Axios** - HTTP client
- **Lucide React** - Icons
