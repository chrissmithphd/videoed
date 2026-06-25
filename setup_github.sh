#!/bin/bash
# Setup GitHub remote for videoed repository

echo "GitHub Repository Setup"
echo "======================="
echo ""
echo "Please provide your GitHub repository URL:"
echo "Example: https://github.com/yourusername/videoed.git"
echo "      or: git@github.com:yourusername/videoed.git"
echo ""
read -p "GitHub URL: " GITHUB_URL

if [ -z "$GITHUB_URL" ]; then
    echo "No URL provided. Exiting."
    exit 1
fi

# Add the remote
git remote add origin "$GITHUB_URL"

echo ""
echo "Remote added successfully!"
echo ""
echo "Now pushing to GitHub..."
git push -u origin master

echo ""
echo "✓ Done! Your code is now on GitHub."
