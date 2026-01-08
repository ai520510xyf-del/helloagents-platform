#!/bin/bash
cd /Users/anker/Desktop/work/mydocuments/project/agent-study/helloagents-platform/frontend
echo "Cleaning node_modules and package-lock.json..."
rm -rf node_modules package-lock.json
echo "Installing dependencies..."
npm install
echo "Starting dev server..."
npm run dev
