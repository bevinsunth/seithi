#!/bin/bash

echo "🚀 Building Backend for Oracle Cloud (x86_64)..."

# Navigate to backend directory
cd ../seithi-backend || exit

# Cross-compile for Linux x86_64
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o ../deploy/oracle/seithi-backend-x86 .

if [ $? -eq 0 ]; then
    echo "✅ Build successful: deploy/oracle/seithi-backend-x86"
else
    echo "❌ Build failed"
    exit 1
fi
