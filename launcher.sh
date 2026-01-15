#!/bin/bash
# One-click launcher for Council AI system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Header
show_header() {
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║                                                           ║"
    echo "║                🏛️  Council AI Launcher                    ║"
    echo "║     Intelligent Advisory Council with AI-Powered Personas ║"
    echo "║                                                           ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Check if virtual environment exists
check_venv() {
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}⚠️  No virtual environment found.${NC}"
        echo -e "Run '${GREEN}./launcher.sh dev${NC}' to set up the development environment."
        return 1
    fi
    return 0
}

# Check environment file
check_env() {
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            echo -e "${YELLOW}⚠️  No .env file found. Creating from .env.example...${NC}"
            cp .env.example .env
            echo -e "${GREEN}✓ .env file created. Please edit it with your API keys.${NC}"
        else
            echo -e "${YELLOW}⚠️  No .env file found. Create one with your API keys.${NC}"
        fi
    fi
}

# DEV SETUP
setup_dev() {
    echo -e "${BLUE}🛠️  Setting up development environment...${NC}"

    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo -e "${GREEN}✓ Virtual environment created${NC}"
    fi

    # shellcheck disable=SC1091
    source venv/bin/activate
    pip install --upgrade pip
    pip install -e ".[dev]"

    check_env

    echo ""
    echo -e "${GREEN}✅ Development environment ready${NC}"
    echo -e "${YELLOW}Activate with: source venv/bin/activate${NC}"
}

# START Web App
start_web() {
    check_env
    echo -e "${BLUE}🚀 Starting Council AI web application...${NC}"
    
    if check_venv; then
        # shellcheck disable=SC1091
        source venv/bin/activate
    fi
    
    council web --reload &
    WEB_PID=$!
    
    echo ""
    echo -e "${GREEN}✅ Web app started!${NC}"
    echo ""
    echo -e "  • ${CYAN}Web UI:${NC}         http://127.0.0.1:8000"
    echo -e "  • ${CYAN}API Docs:${NC}       http://127.0.0.1:8000/docs"
    echo ""
    echo -e "${YELLOW}💡 Press Ctrl+C to stop the server${NC}"
    
    # Wait for the process
    wait $WEB_PID
}

# QUICKSTART Demo
run_quickstart() {
    echo -e "${BLUE}🎮 Running Council AI Quickstart Demo...${NC}"
    
    if check_venv; then
        # shellcheck disable=SC1091
        source venv/bin/activate
    fi
    
    council quickstart
}

# INTERACTIVE Mode
run_interactive() {
    check_env
    echo -e "${BLUE}💬 Starting Council AI Interactive Mode...${NC}"
    
    if check_venv; then
        # shellcheck disable=SC1091
        source venv/bin/activate
    fi
    
    council interactive
}

# INIT Setup Wizard
run_init() {
    echo -e "${BLUE}⚙️  Running Council AI Setup Wizard...${NC}"
    
    if check_venv; then
        # shellcheck disable=SC1091
        source venv/bin/activate
    fi
    
    council init
}

# RUN Tests
run_tests() {
    echo -e "${BLUE}🧪 Running Council AI Tests...${NC}"
    
    if check_venv; then
        # shellcheck disable=SC1091
        source venv/bin/activate
    fi
    
    pytest tests/ -v
}

# CHECK Readiness
check_readiness() {
    echo -e "${BLUE}🔍 Checking environment readiness...${NC}"

    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        echo -e "  [${GREEN}✓${NC}] ${PYTHON_VERSION}"
    else
        echo -e "  [${RED}✗${NC}] Python not found"
    fi

    # Check virtual environment
    if [ -d "venv" ]; then
        echo -e "  [${GREEN}✓${NC}] Virtual environment exists"
    else
        echo -e "  [${YELLOW}!${NC}] Virtual environment missing (run: ./launcher.sh dev)"
    fi

    # Check .env
    if [ -f .env ]; then
        echo -e "  [${GREEN}✓${NC}] .env file exists"
    else
        echo -e "  [${YELLOW}!${NC}] .env file missing"
    fi

    # Check if council command is available
    if command -v council &> /dev/null; then
        echo -e "  [${GREEN}✓${NC}] council CLI installed"
    else
        echo -e "  [${YELLOW}!${NC}] council CLI not in PATH (activate venv or run: ./launcher.sh dev)"
    fi

    echo ""
    echo -e "${GREEN}✓ Readiness check complete.${NC}"
}

# USAGE / Interactive Menu
show_menu() {
    show_header
    echo "Select an option:"
    echo ""
    echo -e "  ${GREEN}1)${NC} web        - Start the web application"
    echo -e "  ${CYAN}2)${NC} interactive - Start interactive CLI mode"
    echo -e "  ${MAGENTA}3)${NC} quickstart - Run the demo (no API key required)"
    echo -e "  ${YELLOW}4)${NC} init       - Run the setup wizard"
    echo -e "  ${BLUE}5)${NC} dev        - Setup development environment"
    echo -e "  6) test       - Run tests"
    echo -e "  7) check      - Check environment readiness"
    echo -e "  ${RED}q)${NC} quit       - Exit"
    echo ""
    read -p "Enter choice [1-7 or q]: " choice
    
    case "$choice" in
        1|web)         start_web ;;
        2|interactive) run_interactive ;;
        3|quickstart)  run_quickstart ;;
        4|init)        run_init ;;
        5|dev)         setup_dev ;;
        6|test)        run_tests ;;
        7|check)       check_readiness ;;
        q|quit)        echo "Goodbye!"; exit 0 ;;
        *)             echo -e "${RED}Invalid option${NC}"; show_menu ;;
    esac
}

# USAGE for command-line mode
show_usage() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  ${GREEN}web${NC}         - Start the web application"
    echo "  ${CYAN}interactive${NC} - Start interactive CLI mode"
    echo "  ${MAGENTA}quickstart${NC}  - Run the demo (no API key required)"
    echo "  ${YELLOW}init${NC}        - Run the setup wizard"
    echo "  ${BLUE}dev${NC}         - Setup development environment"
    echo "  test        - Run tests"
    echo "  check       - Check environment readiness"
    echo ""
    echo "Run without arguments for interactive menu."
    exit 1
}

# Main Logic
case "${1:-}" in
    web)         start_web ;;
    interactive) run_interactive ;;
    quickstart)  run_quickstart ;;
    init)        run_init ;;
    dev)         setup_dev ;;
    test)        run_tests ;;
    check)       check_readiness ;;
    help|-h|--help) show_usage ;;
    "")          show_menu ;;
    *)           echo -e "${RED}Unknown command: $1${NC}"; show_usage ;;
esac
