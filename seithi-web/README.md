# Seithi Web

SvelteKit frontend for the Seithi news aggregation platform.

## Tech Stack

- **Framework**: SvelteKit
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Components**: DaisyUI
- **API Client**: Fetch API

## Setup

1. **Install dependencies**:
```bash
bun install
```

2. **Configure API endpoint**:
The frontend connects to `http://localhost:8080/api` by default.
Update `src/lib/api.ts` if your backend runs on a different port.

3. **Run development server**:
```bash
bun dev
```

Open `http://localhost:5173`

## Features

- **Article Display**: Grid layout with article cards
- **Probability Scores**: Visual representation of ML scores across 3 axes
- **Filtering**: Adjust minimum thresholds for Facts, Calm, and Deep scores
- **User Feedback**: Click "Correct?" to provide feedback on ML classifications
- **Dark Mode**: Automatic dark mode support

## Components

- **ArticleCard**: Displays article with title, domain, date, and scores
- **ScoreBar**: Shows probability distribution with feedback UI
- **Main Page**: Article grid with filter controls

## Build for Production

```bash
bun run build
bun run preview
```

