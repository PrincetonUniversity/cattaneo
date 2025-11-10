#!/bin/bash

# Visual Comparison Test Runner for Cattaneo Website
# This script sets up the environment and runs comprehensive visual tests

set -e  # Exit on error

echo "================================"
echo "Cattaneo Website Visual Testing"
echo "================================"
echo ""

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "❌ Conda not found. Please install Miniconda or Anaconda."
    exit 1
fi

echo "📦 Setting up conda environment..."

# Create/update conda environment
if conda env list | grep -q "^cattaneo-test "; then
    echo "  Environment exists, updating..."
    conda env update -f environment.yml --prune
else
    echo "  Creating new environment..."
    conda env create -f environment.yml
fi

echo ""
echo "✅ Environment ready"
echo ""

# Activate environment and run tests
echo "🚀 Running visual comparison tests..."
echo ""

# Run with conda run to ensure correct environment
conda run -n cattaneo-test playwright install chromium

echo ""
echo "🔍 Executing test suite..."
echo ""

conda run -n cattaneo-test python -m pytest test_visual_comparison.py \
    -v \
    --html=test_results/report.html \
    --self-contained-html \
    --tb=short

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
