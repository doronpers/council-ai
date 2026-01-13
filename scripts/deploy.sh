#!/bin/bash
# Council AI - Build and Deploy Script

set -e

# Configuration
IMAGE_NAME="council-ai"
TAG="latest"
NAMESPACE="default"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🏗️  Step 1: Building Docker image...${NC}"
docker build -t ${IMAGE_NAME}:${TAG} .

echo -e "${BLUE}📦 Step 2: Preparing Kubernetes secrets...${NC}"
# Check if secret exists, if not, prompt for key
if ! kubectl get secret council-secrets &> /dev/null; then
    echo -e "${YELLOW}⚠️  Secret 'council-secrets' not found.${NC}"
    read -p "Enter your ANTHROPIC_API_KEY (or leave blank to skip): " API_KEY
    if [ ! -z "$API_KEY" ]; then
        kubectl create secret generic council-secrets --from-literal=api-key="$API_KEY"
        echo -e "${GREEN}✓ Secret created.${NC}"
    else
        echo -e "${YELLOW}ℹ️  Skipping secret creation. You'll need to create it manually.${NC}"
    fi
else
    echo -e "${GREEN}✓ Secret 'council-secrets' already exists.${NC}"
fi

echo -e "${BLUE}🚀 Step 3: Deploying to Kubernetes...${NC}"
kubectl apply -f k8s/deployment.yaml

echo -e "${GREEN}✅ Deployment complete!${NC}"
echo -e "Check status with: ${BLUE}kubectl get pods -l app=council-ai${NC}"
echo -e "Expose locally with: ${BLUE}kubectl port-forward service/council-ai 8080:80${NC}"
