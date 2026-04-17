# Course Recommendation API Integration

This document describes how the Chrome extension integrates with various course provider APIs.

## Supported Platforms

### 1. Coursera
- **API**: Coursera Catalog API
- **Features**: Search courses, get recommendations
- **Integration**: Direct search URLs

### 2. edX
- **API**: edX Course Discovery API
- **Features**: Browse courses, filter by topic
- **Integration**: Direct search URLs

### 3. Udemy
- **API**: Udemy Affiliate API
- **Features**: Course search and recommendations
- **Integration**: Search URLs with affiliate tracking

### 4. LinkedIn Learning
- **API**: LinkedIn Learning API
- **Features**: Professional courses
- **Integration**: Direct search URLs

### 5. Pluralsight
- **API**: Pluralsight Catalog
- **Features**: Tech-focused courses
- **Integration**: Direct search URLs

## Implementation

### Current Implementation (v1.0)
- Direct URL construction for search
- No API keys required
- Simple and reliable
- Instant redirects to course pages

### Future Enhancement (v2.0)
- Real API integration with actual course data
- Pricing information
- Course ratings and reviews
- Personalized recommendations based on learning style
- Progress tracking

## Adding New Providers

To add a new course provider:

1. Update `background.js`:
```javascript
const course_providers = {
  'NewProvider': 'https://newprovider.com/search?q='
};
```

2. Add provider-specific logic if needed
3. Update documentation
4. Test integration

## API Keys (Future)

For production use with real APIs, you'll need:
- Coursera Partner credentials
- edX OAuth tokens
- Udemy Affiliate API key
- LinkedIn Learning API access

Store in environment variables or Chrome extension storage.
