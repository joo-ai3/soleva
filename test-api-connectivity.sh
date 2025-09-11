#!/bin/bash

echo "=== Soleva API Connectivity Test ==="
echo "Testing backend connectivity from inside nginx container"
echo ""

# Test basic backend health endpoint
echo "1. Testing backend health endpoint..."
curl -s -w "\nStatus: %{http_code}\nTime: %{time_total}s\n" http://backend:8000/api/health/

echo ""
echo "2. Testing backend API root..."
curl -s -w "\nStatus: %{http_code}\nTime: %{time_total}s\n" http://backend:8000/api/

echo ""
echo "3. Testing products endpoint..."
curl -s -w "\nStatus: %{http_code}\nTime: %{time_total}s\n" http://backend:8000/api/products/

echo ""
echo "4. Testing authentication endpoint..."
curl -s -w "\nStatus: %{http_code}\nTime: %{time_total}s\n" http://backend:8000/api/auth/

echo ""
echo "5. Testing admin endpoint..."
curl -s -w "\nStatus: %{http_code}\nTime: %{time_total}s\n" http://backend:8000/admin/

echo ""
echo "6. Testing frontend connectivity..."
curl -s -w "\nStatus: %{http_code}\nTime: %{time_total}s\n" http://frontend/

echo ""
echo "=== Test Complete ==="
