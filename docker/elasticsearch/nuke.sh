#!/bin/bash

# Docker Complete Cleanup Script
# This script provides a tabla rasa (clean slate) by removing all Docker resources:
# - Containers (running and stopped)
# - Networks
# - Volumes
# - Images
# - Build cache

echo "=== Docker Complete Cleanup ==="
echo "WARNING: This will remove ALL Docker resources!"
echo "Press Ctrl+C within 5 seconds to cancel..."
sleep 5

echo -e "\n[1/6] Stopping all running containers..."
docker compose down 2>/dev/null || true
docker stop $(docker ps -q) 2>/dev/null || echo "No running containers to stop."

echo -e "\n[2/6] Removing all containers..."
docker rm -f $(docker ps -a -q) 2>/dev/null || echo "No containers to remove."

echo -e "\n[3/6] Removing all networks..."
docker network rm $(docker network ls -q) 2>/dev/null || echo "No networks to remove."
# Note: Default networks (bridge, host, none) cannot be removed

echo -e "\n[4/6] Removing all volumes..."
docker volume rm $(docker volume ls -q) 2>/dev/null || echo "No volumes to remove."

echo -e "\n[5/6] Removing all images..."
docker rmi -f $(docker images -a -q) 2>/dev/null || echo "No images to remove."

echo -e "\n[6/6] Pruning system (removing build cache)..."
docker system prune -a -f --volumes

echo -e "\n=== Docker Environment Reset Complete ==="
echo "Current Docker resources:"
echo -e "\nContainers:"
docker ps -a
echo -e "\nNetworks:"
docker network ls
echo -e "\nVolumes:"
docker volume ls
echo -e "\nImages:"
docker images -a

echo -e "\nYour Docker environment is now clean and ready for testing."
