#!/bin/bash

# Simplified Visual Comparison Test Runner
set -e

echo "================================"
echo "Cattaneo Website Visual Testing"
echo "================================"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "📦 Activating virtual environment..."
source venv/bin/activate

echo "📦 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo "📦 Installing Playwright browsers..."
playwright install chromium

echo ""
echo "🔍 Running visual comparison tests..."
echo ""

python -m pytest test_visual_comparison.py \
    -v \
    --html=test_results/report.html \
    --self-contained-html \
    --tb=short \
    -W ignore::DeprecationWarning

echo ""
echo "================================"
echo "✅ Tests complete!"
echo "================================"
echo ""
echo "📊 View detailed results:"
echo "   HTML Report: test_results/report.html"
echo "   Screenshots: test_results/"
echo "   Font Report: test_results/fonts_detected.json"
echo ""
