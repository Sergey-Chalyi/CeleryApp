"""Main application entry point for manual task execution and database initialization."""
import sys
import logging
from app.database import create_tables
from app.tasks import fetch_users_task, fetch_addresses_task, fetch_credit_cards_task, get_user_stats

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize database tables."""
    try:
        create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        sys.exit(1)

def run_manual_tasks():
    """Run tasks manually for testing."""
    try:
        logger.info("Running manual tasks...")
        
        # Fetch users
        logger.info("Fetching users...")
        result = fetch_users_task.delay()
        logger.info(f"Users task result: {result.get()}")
        
        # Fetch addresses
        logger.info("Fetching addresses...")
        result = fetch_addresses_task.delay()
        logger.info(f"Addresses task result: {result.get()}")
        
        # Fetch credit cards
        logger.info("Fetching credit cards...")
        result = fetch_credit_cards_task.delay()
        logger.info(f"Credit cards task result: {result.get()}")
        
        # Get stats
        logger.info("Getting user stats...")
        result = get_user_stats.delay()
        logger.info(f"User stats: {result.get()}")
        
    except Exception as e:
        logger.error(f"Error running manual tasks: {e}")
        sys.exit(1)

def show_help():
    """Show help message."""
    print("""
CeleryApp - User Data Supplementation Application

Usage:
    python main.py init-db          Initialize database tables
    python main.py run-tasks        Run all tasks manually
    python main.py stats            Show user statistics
    python main.py help             Show this help message

Docker Usage:
    docker-compose up               Start all services
    docker-compose up -d            Start all services in background
    docker-compose down             Stop all services
    docker-compose logs celery-worker    View worker logs
    docker-compose logs celery-beat      View scheduler logs
    """)

def show_stats():
    """Show user statistics."""
    try:
        result = get_user_stats.delay()
        stats = result.get()
        print(f"""
User Statistics:
- Total Users: {stats['total_users']}
- Total Addresses: {stats['total_addresses']}
- Total Credit Cards: {stats['total_credit_cards']}
        """)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "init-db":
        init_database()
    elif command == "run-tasks":
        run_manual_tasks()
    elif command == "stats":
        show_stats()
    elif command == "help":
        show_help()
    else:
        print(f"Unknown command: {command}")
        show_help()
        sys.exit(1)
