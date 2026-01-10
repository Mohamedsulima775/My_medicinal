#!/bin/bash
# =============================================================================
# Healthcare Provider Environment Setup Script
# سكريبت تهيئة بيئة مقدم الرعاية الصحية
# =============================================================================
# Quick setup script for Healthcare Provider environment
# Usage: ./setup_provider_env.sh [site-name]
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                                                                    ║"
echo "║          Healthcare Provider Environment Setup                    ║"
echo "║          تهيئة بيئة مقدم الرعاية الصحية                          ║"
echo "║                                                                    ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if site name is provided
SITE_NAME=${1:-my_medicinal.local}

echo -e "${YELLOW}[INFO]${NC} Using site: ${SITE_NAME}"
echo ""

# Step 1: Check if .env.provider exists
echo -e "${BLUE}[1/5]${NC} Checking environment configuration..."
if [ ! -f .env.provider ]; then
    echo -e "${YELLOW}[INFO]${NC} Creating .env.provider from example..."
    cp .env.provider.example .env.provider
    echo -e "${GREEN}[OK]${NC} .env.provider created. Please configure it before running the initialization."
    echo -e "${YELLOW}[INFO]${NC} Edit .env.provider and set your desired configuration."
    echo ""
else
    echo -e "${GREEN}[OK]${NC} .env.provider already exists"
    echo ""
fi

# Step 2: Verify Python files
echo -e "${BLUE}[2/5]${NC} Verifying Python files..."
if python3 -m py_compile my_medicinal/my_medicinal/provider_environment.py 2>/dev/null; then
    echo -e "${GREEN}[OK]${NC} provider_environment.py - Valid"
else
    echo -e "${RED}[ERROR]${NC} provider_environment.py - Syntax error"
    exit 1
fi

if python3 -m py_compile my_medicinal/my_medicinal/provider_middleware.py 2>/dev/null; then
    echo -e "${GREEN}[OK]${NC} provider_middleware.py - Valid"
else
    echo -e "${RED}[ERROR]${NC} provider_middleware.py - Syntax error"
    exit 1
fi
echo ""

# Step 3: Check if bench is available
echo -e "${BLUE}[3/5]${NC} Checking Frappe bench..."
if command -v bench &> /dev/null; then
    echo -e "${GREEN}[OK]${NC} Bench found"
else
    echo -e "${RED}[ERROR]${NC} Bench not found. Please install Frappe bench first."
    exit 1
fi
echo ""

# Step 4: Check if site exists
echo -e "${BLUE}[4/5]${NC} Checking site existence..."
if bench --site ${SITE_NAME} list-apps &> /dev/null; then
    echo -e "${GREEN}[OK]${NC} Site ${SITE_NAME} exists"
else
    echo -e "${RED}[ERROR]${NC} Site ${SITE_NAME} not found"
    echo -e "${YELLOW}[INFO]${NC} Available sites:"
    bench list-sites
    exit 1
fi
echo ""

# Step 5: Initialize provider environment
echo -e "${BLUE}[5/5]${NC} Initializing Healthcare Provider environment..."
echo -e "${YELLOW}[INFO]${NC} This will:"
echo "  - Create Healthcare Provider role"
echo "  - Setup permissions"
echo "  - Create workspace (if supported)"
echo "  - Configure dashboard"
echo "  - Setup notifications"
echo ""

read -p "$(echo -e ${YELLOW}'Continue? (y/n): '${NC})" -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}[RUNNING]${NC} Initializing environment..."

    # Use Python import method for better reliability
    if bench --site ${SITE_NAME} console <<EOF
from my_medicinal.my_medicinal.provider_environment import initialize_provider_environment
result = initialize_provider_environment()
print("=" * 80)
print("Setup completed successfully!")
print("=" * 80)
EOF
    then
        echo ""
        echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║                                                                ║${NC}"
        echo -e "${GREEN}║  ✓ Healthcare Provider Environment Ready!                     ║${NC}"
        echo -e "${GREEN}║    بيئة مقدم الرعاية الصحية جاهزة!                           ║${NC}"
        echo -e "${GREEN}║                                                                ║${NC}"
        echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
        echo ""
        echo -e "${BLUE}Next Steps:${NC}"
        echo "  1. Configure .env.provider with your settings"
        echo "  2. Create Healthcare Provider records"
        echo "  3. Assign Healthcare Provider role to users"
        echo "  4. Access provider portal at: /app/healthcare-provider-portal"
        echo ""
        echo -e "${BLUE}Documentation:${NC}"
        echo "  See PROVIDER_ENVIRONMENT.md for complete guide"
        echo ""
    else
        echo -e "${RED}[ERROR]${NC} Initialization failed. Check error log."
        exit 1
    fi
else
    echo -e "${YELLOW}[CANCELLED]${NC} Setup cancelled by user."
    exit 0
fi

# Check environment status
echo -e "${BLUE}[STATUS]${NC} Checking environment status..."
bench --site ${SITE_NAME} execute "my_medicinal.my_medicinal.provider_environment.get_provider_environment_status" || echo -e "${YELLOW}[INFO]${NC} Status check completed"

echo ""
echo -e "${GREEN}[DONE]${NC} Setup complete!"
echo ""
