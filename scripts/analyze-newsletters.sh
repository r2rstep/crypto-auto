#!/usr/bin/env bash
set -euo pipefail

NEWSLETTER_SENDERS=(
    "newsletters@coindesk.com"
)

PROMPT='You are a professional cryptocurrency market analyst. Analyze the following newsletter and provide a structured analysis in this exact JSON format (no markdown, just pure JSON):

{
  "overall_sentiment": "Bullish|Neutral|Bearish",
  "confidence": "High|Medium|Low",
  "score": <number 1-10, where 1=Extremely Bearish, 5=Neutral, 10=Extremely Bullish>,
  "key_insights": ["insight1", "insight2", "insight3"],
  "projects_mentioned": [
    {"name": "ProjectName", "sentiment": "positive|neutral|negative", "note": "brief note"}
  ],
  "investment_implication": "One sentence summary of what this means for portfolio"
}

Newsletter Content:
'

MAX_EMAILS="${MAX_EMAILS:-5}"
OUTPUT_DIR="${OUTPUT_DIR:-./data/sentiment}"

mkdir -p "$OUTPUT_DIR"

build_search_query() {
    local query="is:unread ("
    local first=true
    for sender in "${NEWSLETTER_SENDERS[@]}"; do
        if [ "$first" = true ]; then
            first=false
        else
            query+=" OR "
        fi
        query+="from:$sender"
    done
    query+=")"
    echo "$query"
}

mark_as_read() {
    local thread_id="$1"
    gog gmail thread modify "$thread_id" --remove UNREAD --force 2>/dev/null && \
        echo "Marked thread $thread_id as read" >&2 || \
        echo "Failed to mark thread $thread_id as read" >&2
}

analyze_email() {
    local msg_id="$1"
    local output_file="$2"

    echo "Fetching email $msg_id..." >&2

    local email_json
    email_json=$(gog gmail get "$msg_id" --json 2>/dev/null) || {
        echo "Failed to fetch email $msg_id" >&2
        return 1
    }

    local thread_id
    thread_id=$(echo "$email_json" | jq -r '.message.threadId // empty')

    local subject from date body
    subject=$(echo "$email_json" | jq -r '.headers.subject // "No Subject"')
    from=$(echo "$email_json" | jq -r '.headers.from // "Unknown"')
    date=$(echo "$email_json" | jq -r '.headers.date // ""')
    body=$(echo "$email_json" | jq -r '.body // ""' | tr -d '\0' | head -c 8000)

    if [ -z "$body" ]; then
        body=$(echo "$email_json" | jq -r '.message.snippet // ""')
    fi

    if [ -z "$body" ]; then
        echo "No body content for email $msg_id" >&2
        return 1
    fi

    echo "Body length: ${#body} chars" >&2

    echo "Analyzing with Gemini..." >&2
    local gemini_response sentiment_json
    gemini_response=$(gemini -p "${PROMPT}${body}" --output-format text 2>&1 | grep -v "^Hook registry")

    if echo "$gemini_response" | grep -qi "quota\|error\|failed"; then
        echo "Gemini API error for $msg_id: $(echo "$gemini_response" | head -1)" >&2
        return 1
    fi

    sentiment_json=$(echo "$gemini_response" | sed 's/```json//g; s/```//g' | grep -Pzo '\{[\s\S]*\}' | tr '\0' '\n' | head -1 2>/dev/null) || sentiment_json="{}"

    if [ -z "$sentiment_json" ] || ! echo "$sentiment_json" | jq empty 2>/dev/null; then
        echo "Failed to parse Gemini response for $msg_id" >&2
        return 1
    fi

    local timestamp
    timestamp=$(date -d "$date" -Iseconds 2>/dev/null || date -Iseconds)

    jq -n \
        --arg timestamp "$timestamp" \
        --arg source "$from" \
        --arg subject "$subject" \
        --argjson sentiment "$sentiment_json" \
        '{
            timestamp: $timestamp,
            source: $source,
            subject: $subject,
            overall_sentiment: ($sentiment.overall_sentiment // "Unknown"),
            confidence: ($sentiment.confidence // "Low"),
            score: ($sentiment.score // 5),
            key_insights: ($sentiment.key_insights // []),
            projects_mentioned: ($sentiment.projects_mentioned // []),
            investment_implication: ($sentiment.investment_implication // "Unable to analyze")
        }' > "$output_file"

    echo "Saved analysis to $output_file" >&2

    if [ -n "$thread_id" ]; then
        mark_as_read "$thread_id"
    fi
}

main() {
    echo "Searching for unread newsletter emails..." >&2

    local query
    query=$(build_search_query)
    echo "Query: $query" >&2

    local search_results
    search_results=$(gog gmail search "$query" --max "$MAX_EMAILS" --json 2>/dev/null) || {
        echo "No newsletters found or search failed" >&2
        exit 0
    }

    local message_ids
    message_ids=$(echo "$search_results" | jq -r '.threads[]?.id // empty' 2>/dev/null | head -n "$MAX_EMAILS")

    if [ -z "$message_ids" ]; then
        echo "No newsletter emails found" >&2
        exit 0
    fi

    local results=()
    local count=0

    while IFS= read -r msg_id; do
        [ -z "$msg_id" ] && continue

        local output_file="$OUTPUT_DIR/sentiment_${msg_id}.json"

        if [ -f "$output_file" ]; then
            echo "Skipping $msg_id (already analyzed)" >&2
            results+=("$(cat "$output_file")")
            continue
        fi

        if analyze_email "$msg_id" "$output_file"; then
            results+=("$(cat "$output_file")")
            ((count++))
        fi

        sleep 1
    done <<< "$message_ids"

    echo "Analyzed $count new emails" >&2

    local combined_file="$OUTPUT_DIR/sentiment_$(date +%Y%m%d_%H%M%S).json"

    if [ ${#results[@]} -gt 0 ]; then
        printf '%s\n' "${results[@]}" | jq -s '
            {
                analysis_date: (now | todate),
                count: length,
                sentiments: .,
                summary: {
                    avg_score: ([.[].score] | add / length),
                    bullish_count: ([.[] | select(.overall_sentiment == "Bullish")] | length),
                    bearish_count: ([.[] | select(.overall_sentiment == "Bearish")] | length),
                    neutral_count: ([.[] | select(.overall_sentiment == "Neutral")] | length)
                }
            }
        ' > "$combined_file"

        cat "$combined_file"
        echo "Combined analysis saved to $combined_file" >&2
    else
        echo '{"count": 0, "sentiments": [], "summary": {}}' | jq .
    fi
}

main "$@"
