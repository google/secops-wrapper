#!/bin/bash
# Script to deploy documentation to GitHub Pages without losing your working directory

set -e  # Exit on error

# Save current branch to return to it later
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "Current branch: $CURRENT_BRANCH"

# Check if there are uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "⚠️ WARNING: You have uncommitted changes."
    echo "It's recommended to commit your changes before deploying."
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Deployment aborted."
        exit 1
    fi
    
    # Stash changes to restore them later
    echo "Stashing changes to restore them after deployment..."
    git stash push -m "Pre-deployment stash"
    STASHED=true
else
    STASHED=false
fi

# Create docs directory if it doesn't exist
mkdir -p docs

# Recreate the docs structure if needed
if [ ! -d "docs/_static" ]; then
    mkdir -p docs/_static docs/img docs/chronicle docs/cli docs/advanced docs/api
fi

# Check if we need to create the basic documentation files
if [ ! -f "docs/conf.py" ]; then
    echo "Creating basic documentation structure..."
    # Add your code to recreate the basic documentation structure here
    # This is a placeholder - you'll need to add the actual content
fi

# Build the documentation
echo "Building documentation..."
# Use sphinx-build directly if Makefile doesn't exist
if [ -f "docs/Makefile" ]; then
    (cd docs && make html)
else
    # Fallback if Makefile doesn't exist
    sphinx-build -b html docs docs/_build/html
fi

# Create a temporary directory for the build
echo "Preparing for deployment..."
TMP_DIR=$(mktemp -d)
if [ -d "docs/_build/html" ]; then
    cp -r docs/_build/html/* $TMP_DIR/
else
    echo "Error: Build directory not found. Make sure documentation was built successfully."
    if [ "$STASHED" = true ]; then
        echo "Restoring your changes..."
        git stash pop
    fi
    exit 1
fi

# Switch to gh-pages branch, creating it if it doesn't exist
if git show-ref --verify --quiet refs/heads/gh-pages; then
    echo "Checking out existing gh-pages branch..."
    git checkout gh-pages
else
    echo "Creating gh-pages branch..."
    git checkout --orphan gh-pages
    git rm -rf .
fi

# Remove all files except .git
find . -maxdepth 1 ! -name '.git' ! -name '.' -exec rm -rf {} \;

# Copy the built documentation
echo "Copying documentation files..."
cp -r $TMP_DIR/* .
rm -rf $TMP_DIR

# Create .nojekyll file to prevent Jekyll processing
touch .nojekyll

# Add and commit changes
echo "Committing changes..."
git add .
git commit -m "Update documentation $(date)"

# Push to GitHub
echo "Pushing to GitHub..."
git push -f origin gh-pages

# Return to the original branch
echo "Returning to $CURRENT_BRANCH branch..."
git checkout $CURRENT_BRANCH

# Restore stashed changes if any
if [ "$STASHED" = true ]; then
    echo "Restoring your changes..."
    git stash pop
fi

echo "Documentation deployed successfully!"
echo "Visit https://dandye.github.io/google-secops-wrapper/ to view it."
