# Make.com Integration Guide

This document describes how to set up Make.com (formerly Integromat) to automatically analyze cryptocurrency newsletters using AI and extract sentiment data.

## Overview

The Make.com integration complements the core Python automation by:
- Monitoring email newsletters (RealVision, Glassnode, Kanga Exchange, etc.)
- Analyzing content with Gemini 1.5 Flash API (free tier)
- Extracting key insights and sentiment scores
- Optionally writing results to Google Sheets or sending notifications

## Prerequisites

1. **Make.com Account**: Sign up at [make.com](https://www.make.com) (free tier available)
2. **Gemini API Key**: Get free API access at [Google AI Studio](https://makersuite.google.com/app/apikey)
3. **Email Access**: Gmail account or other email provider supported by Make.com

## Scenario Setup

### Step 1: Create New Scenario

1. Log in to Make.com
2. Click "Create a new scenario"
3. Name it "Crypto Newsletter Sentiment Analysis"

### Step 2: Configure Email Trigger

1. **Add Module**: Gmail → "Watch Emails"
2. **Configuration**:
   - **Folder**: INBOX
   - **Criteria**: From contains
   - **Filter by sender**:
     - `newsletter@glassnode.com`
     - `newsletter@realvision.com`
     - `newsletter@kanga.exchange`
     - (Add more senders as needed)
   - **Maximum results**: 1
   - **Processing time**: Check every 15 minutes

### Step 3: Add Gemini API Module

1. **Add Module**: HTTP → "Make a Request"
2. **Configuration**:
   - **URL**: `https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key=YOUR_API_KEY`
   - **Method**: POST
   - **Headers**:
     ```
     Content-Type: application/json
     ```
   - **Body**:
     ```json
     {
       "contents": [{
         "parts": [{
           "text": "You are a professional cryptocurrency analyst. Analyze the following newsletter and provide:\n\n1. Three most important insights (bullet points)\n2. Overall market sentiment (Bullish/Neutral/Bearish)\n3. Sentiment score (1-10, where 1=Very Bearish, 10=Very Bullish)\n4. Key projects mentioned with their sentiment\n\nNewsletter content:\n\n{{1.text}}"
         }]
       }]
     }
     ```

**Replace**:
- `YOUR_API_KEY` with your Gemini API key
- `{{1.text}}` is the email body from Step 2 (adjust mapping number as needed)

### Step 4: Parse Gemini Response

1. **Add Module**: Tools → "Text Parser"
2. **Configuration**:
   - **Pattern**: Extract JSON from Gemini response
   - **Text**: `{{2.body}}`

**Expected Response Structure**:
```json
{
  "candidates": [{
    "content": {
      "parts": [{
        "text": "1. Insight one\n2. Insight two\n3. Insight three\n\nSentiment: Bullish\nScore: 8/10\n\nKey Projects:\n- Bitcoin: Positive institutional accumulation\n- Ethereum: ..."
      }]
    }
  }]
}
```

### Step 5: Format and Store Results

**Option A: Write to Google Sheets**

1. **Add Module**: Google Sheets → "Add a Row"
2. **Configuration**:
   - **Spreadsheet**: Your crypto analysis spreadsheet
   - **Sheet**: "Sentiment Analysis"
   - **Values**:
     - Date: `{{now}}`
     - Source: `{{1.sender}}`
     - Sentiment: Extract from parsed text
     - Score: Extract from parsed text
     - Insights: Extract from parsed text

**Option B: Send Notification**

1. **Add Module**: Telegram/Discord/Slack → "Send a Message"
2. **Configuration**:
   - **Message**:
     ```
     📧 New Newsletter Analysis
     From: {{1.sender}}
     Sentiment: [Extracted]
     Score: [Extracted]/10

     Key Insights:
     [Extracted insights]
     ```

### Step 6: Error Handling

1. Click on the router between modules
2. Add "Error Handler" route
3. **Add Module**: Tools → "Send Email"
4. Configure to send you an alert if sentiment analysis fails

## Gemini API Prompt Template

Use this optimized prompt for best results:

```
You are a professional cryptocurrency market analyst. Analyze the following newsletter and provide a structured analysis in this exact format:

## Key Insights
1. [First major insight]
2. [Second major insight]
3. [Third major insight]

## Market Sentiment
Overall: [Bullish/Neutral/Bearish]
Confidence: [High/Medium/Low]

## Sentiment Score
[Number from 1-10, where 1=Extremely Bearish, 5=Neutral, 10=Extremely Bullish]

## Projects Mentioned
- [Project Name]: [Brief sentiment/development note]

## Investment Implications
[One sentence summary of what this means for portfolio]

---
Newsletter Content:
{email_body}
```

## Google Sheets Structure (Optional)

If using Option A (Google Sheets integration), create a sheet with these columns:

| Column | Description |
|--------|-------------|
| Timestamp | Auto-populated with current date/time |
| Source | Newsletter sender |
| Overall Sentiment | Bullish/Neutral/Bearish |
| Sentiment Score | 1-10 numeric score |
| Key Insight 1 | First major takeaway |
| Key Insight 2 | Second major takeaway |
| Key Insight 3 | Third major takeaway |
| Projects Mentioned | Comma-separated list |
| Raw Analysis | Full Gemini response |

## Free Tier Limitations

### Make.com Free Tier
- **Operations**: 1,000 operations/month
- **Execution Time**: 5 minutes per execution
- **Scenario Runs**: Every 15 minutes minimum

**Impact**: You can process ~1,000 emails/month. Most users receive 5-10 relevant newsletters/week = 40-80/month, well within limits.

### Gemini 1.5 Flash Free Tier
- **Requests**: 15 requests/minute, 1,500/day
- **Tokens**: 1 million tokens/minute

**Impact**: Newsletter analysis uses ~5,000 tokens each. You can process 200+ newsletters/day for free.

## Testing the Scenario

1. Save the scenario
2. Click "Run once" to test manually
3. Send yourself a test email matching your filter criteria
4. Watch the execution log in Make.com
5. Verify Gemini response is parsed correctly
6. Check that data appears in Google Sheets (if configured)

## Advanced Features

### Sentiment Trend Analysis

Add a module to calculate 7-day and 30-day sentiment averages:

```
Average Score (7d): =AVERAGE(C2:C8)
Average Score (30d): =AVERAGE(C2:C31)
```

### Project-Specific Alerts

Configure filters to only trigger notifications when:
- Sentiment score changes by ±2 points
- Specific projects (BTC, ETH) are mentioned with negative sentiment
- Overall sentiment shifts from Bullish → Bearish (or vice versa)

### Integration with Main System

The sentiment data can be manually referenced from Google Sheets when making DCA decisions, or you can extend the Python script to read from the sentiment sheet and include it in the final analysis report.

## Troubleshooting

### Common Issues

**Problem**: Gemini API returns 429 error
- **Solution**: You hit rate limits. Reduce check frequency to every 30 minutes.

**Problem**: Email not triggering scenario
- **Solution**: Check sender filter is exact match. Gmail may use different addresses for different campaigns.

**Problem**: Sentiment extraction inconsistent
- **Solution**: Make the prompt more specific. Use JSON response format in Gemini:
  ```json
  {
    "sentiment": "Bullish",
    "score": 8,
    "insights": ["insight1", "insight2", "insight3"]
  }
  ```

### Support Resources

- **Make.com Documentation**: https://www.make.com/en/help
- **Gemini API Docs**: https://ai.google.dev/docs
- **Community Forum**: https://community.make.com

## Security Best Practices

1. **Never share API keys** in Make.com scenario screenshots
2. **Use environment variables** in Make.com for sensitive values
3. **Limit Gmail access** to read-only for specific labels
4. **Regular audits**: Review Make.com execution logs monthly
5. **Revoke unused integrations**: If you stop using a newsletter source, remove the filter

## Cost Estimate

| Service | Free Tier | Paid Tier (if needed) |
|---------|-----------|----------------------|
| Make.com | 1,000 ops/month | $9/month for 10,000 ops |
| Gemini API | 1,500 requests/day | Gemini Pro: $0.002/1K tokens |
| Gmail | Unlimited | Included with Google account |

**Total**: $0/month for typical use (5-10 newsletters/week)

## Conclusion

The Make.com integration provides automated sentiment analysis without requiring code changes to the main Python system. It's designed to complement the weekly GitHub Actions workflow by providing ongoing qualitative insights between data updates.

For questions or improvements to this guide, please open an issue in the GitHub repository.
