#!/bin/bash

# Helper script to run the complete English demo
# Usage: ./run_demo_en.sh

set -e

echo "🚀 Demo: Complex Correlation - Wealth + Digital Channel + Longevity"
echo "===================================================================="
echo ""

# Check required files
if [ ! -f "demo_config_en.yml" ]; then
    echo "❌ Error: demo_config_en.yml not found"
    exit 1
fi

if [ ! -f "demo_analysis_en.py" ]; then
    echo "❌ Error: demo_analysis_en.py not found"
    exit 1
fi

if [ ! -f "generate_demo_data_en.py" ]; then
    echo "❌ Error: generate_demo_data_en.py not found"
    exit 1
fi

# Step 1: Generate data
echo "📊 Step 1: Generating data..."
echo "   → Activating virtual environment..."
source venv/bin/activate
echo "   → Running data generation script (unbuffered output)..."
echo ""

# Use PYTHONUNBUFFERED to see logs in real-time
export PYTHONUNBUFFERED=1

# Create a temporary file to capture output while still showing it
TEMP_OUTPUT=$(mktemp)
trap "rm -f $TEMP_OUTPUT" EXIT

# Run the script and tee output to both console and file
python -u generate_demo_data_en.py 2>&1 | tee "$TEMP_OUTPUT"
EXIT_CODE=${PIPESTATUS[0]}

if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "❌ Error during data generation (exit code: $EXIT_CODE)"
    exit 1
fi

echo ""
echo "   ✓ Data generation completed"

# Extract timestamp from output
echo "   → Extracting timestamp..."
TIMESTAMP=$(grep "📅 Timestamp:" "$TEMP_OUTPUT" | sed -E 's/.*folder: ([0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{2}-[0-9]{2}).*/\1/' || echo "")

# If not found, try to extract from the zip file path (most recent)
if [ -z "$TIMESTAMP" ]; then
    ZIP_FILE=$(ls -t demo_output/*/demo_data_en_*.zip 2>/dev/null | head -1)
    if [ -n "$ZIP_FILE" ]; then
        TIMESTAMP=$(basename $(dirname "$ZIP_FILE"))
    fi
fi

# If still not found, use the most recent directory in demo_output
if [ -z "$TIMESTAMP" ]; then
    TIMESTAMP=$(ls -t demo_output/ 2>/dev/null | grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{2}-[0-9]{2}$' | head -1)
fi

if [ -z "$TIMESTAMP" ]; then
    echo "   ⚠ Warning: Could not extract timestamp, will use fallback"
else
    echo "   ✓ Timestamp extracted: $TIMESTAMP"
fi
echo ""

# Step 2: Analyze data
echo "🔍 Step 2: Analyzing complex correlation..."
if [ -n "$TIMESTAMP" ]; then
    ZIP_FILE="demo_output/$TIMESTAMP/demo_data_en_$TIMESTAMP.zip"
    echo "   → Using ZIP file: $ZIP_FILE"
    if [ ! -f "$ZIP_FILE" ]; then
        echo "   ⚠ Warning: ZIP file not found, trying symlink..."
        ZIP_FILE="demo_data_en.zip"
    fi
    echo "   → Running analysis script..."
    python -u demo_analysis_en.py "$ZIP_FILE" 3 "$TIMESTAMP"
else
    # Fallback to symlink
    echo "   → Using fallback symlink: demo_data_en.zip"
    echo "   → Running analysis script..."
    python -u demo_analysis_en.py demo_data_en.zip
fi

ANALYSIS_EXIT=$?
if [ $ANALYSIS_EXIT -ne 0 ]; then
    echo "❌ Error during analysis (exit code: $ANALYSIS_EXIT)"
    exit 1
fi

echo "   ✓ Analysis completed successfully"

echo ""
echo "✅ Demo completed successfully!"
echo ""
if [ -n "$TIMESTAMP" ]; then
    echo "📁 Results available in: demo_output/$TIMESTAMP/"
    echo "   - complex_correlation_analysis.png"
    echo "   - scatter_complex_correlation.png"
    echo "   - complex_analysis_data.csv (consolidated analysis data)"
    echo "   - complex_analysis_data_salesforce.csv (consolidated analysis - Salesforce NPC)"
    echo "   - Gift_Transaction_Raw_Salesforce.csv (raw transactions - one row per transaction - Salesforce NPC)"
    echo "   - transactions_raw.csv (raw transactions - original format)"
    echo "   - demo_data_en_$TIMESTAMP.zip"
else
    echo "📁 Results available in: demo_output/"
fi
echo ""

