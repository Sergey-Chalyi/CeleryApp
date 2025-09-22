# CeleryApp - User Data Supplementation Application

A robust Celery-based application that fetches user data from external APIs and supplements it with address and credit card information. The application runs periodic tasks to continuously update and enrich user data.

## 🚀 Features

- **Periodic Data Fetching**: Automatically fetches users from JSONPlaceholder API
- **Data Supplementation**: Enriches user data with addresses and credit cards from Random Data API
- **Scalable Architecture**: Built with Celery for distributed task processing
- **Database Integration**: PostgreSQL for reliable data storage
- **Redis Broker**: High-performance message broker for task queuing
- **Docker Support**: Complete containerization with Docker Compose
- **Comprehensive Testing**: Full test coverage with pytest
- **Monitoring**: Flower web UI for task monitoring
- **Clean Architecture**: Service layer pattern with proper separation of concerns

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL 15+ (if running locally)
- Redis 7+ (if running locally)

## 🚀 Quick Start

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd CeleryApp
   ```

2. **Start all services**
   ```bash
   docker-compose up -d
   ```

3. **Initialize the database**
   ```bash
   docker-compose run --rm db-init
   ```

4. **Monitor the application**
   - Flower UI: http://localhost:5555
   - View logs: `docker-compose logs -f celery-worker`

### Local Development

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Start PostgreSQL and Redis**
   ```bash
   # Using Docker
   docker run -d --name postgres -e POSTGRES_PASSWORD=password -p 5432:5432 postgres:15
   docker run -d --name redis -p 6379:6379 redis:7-alpine
   ```

4. **Initialize database**
   ```bash
   python main.py init-db
   ```

5. **Start Celery worker**
   ```bash
   celery -A app.celery_app worker --loglevel=info
   ```

6. **Start Celery beat (in another terminal)**
   ```bash
   celery -A app.celery_app beat --loglevel=info
   ```

## 📊 API Endpoints

The application uses the following external APIs:

- **JSONPlaceholder**: https://jsonplaceholder.typicode.com/users
- **Random Data API - Addresses**: https://random-data-api.com/api/address/random_address
- **Random Data API - Credit Cards**: https://random-data-api.com/api/business_credit_card/random_card

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://postgres:password@localhost:5432/celeryapp` | PostgreSQL connection string |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |
| `FETCH_USERS_INTERVAL` | `300` | Users fetch interval (seconds) |
| `FETCH_ADDRESSES_INTERVAL` | `600` | Addresses fetch interval (seconds) |
| `FETCH_CREDIT_CARDS_INTERVAL` | `900` | Credit cards fetch interval (seconds) |

### Task Intervals

- **Users**: Every 5 minutes
- **Addresses**: Every 10 minutes  
- **Credit Cards**: Every 15 minutes

## 🗄️ Database Schema

### Users Table
- `id` (Primary Key)
- `external_id` (Unique, from JSONPlaceholder)
- `name`, `username`, `email`
- `phone`, `website`
- `company_name`, `company_catchphrase`, `company_bs`
- `created_at`, `updated_at`

### Addresses Table
- `id` (Primary Key)
- `user_id` (Foreign Key to Users)
- `street_number`, `street_name`
- `city`, `state`, `country`, `postal_code`
- `created_at`, `updated_at`

### Credit Cards Table
- `id` (Primary Key)
- `user_id` (Foreign Key to Users)
- `card_number`, `card_type`, `expiry_date`
- `created_at`, `updated_at`

## 🧪 Testing

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=app --cov-report=html
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Slow tests only
pytest -m slow
```

### Test Structure
- `tests/test_database.py` - Database model tests
- `tests/test_tasks.py` - Celery task tests
- `tests/test_services.py` - Service layer tests
- `tests/test_integration.py` - End-to-end integration tests

## 📈 Monitoring

### Flower Web UI
Access the Flower monitoring interface at http://localhost:5555 to:
- View active tasks
- Monitor task history
- Check worker status
- View task results

### Logs
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f celery-worker
docker-compose logs -f celery-beat
docker-compose logs -f postgres
```

## 🛠️ Manual Operations

### Initialize Database
```bash
python main.py init-db
```

### Run Tasks Manually
```bash
python main.py run-tasks
```

### Get Statistics
```bash
python main.py stats
```

### Show Help
```bash
python main.py help
```

## 🔍 Service Layer

The application includes a comprehensive service layer for data operations:

### UserService
- `get_user_by_external_id(external_id)`
- `get_user_with_relations(user_id)`
- `get_all_users(limit, offset)`

### AddressService
- `get_addresses_by_user_id(user_id)`

### CreditCardService
- `get_credit_cards_by_user_id(user_id)`

### StatsService
- `get_comprehensive_stats()`

## 🐳 Docker Services

| Service | Description | Port |
|---------|-------------|------|
| `postgres` | PostgreSQL database | 5432 |
| `redis` | Redis message broker | 6379 |
| `celery-worker` | Celery worker process | - |
| `celery-beat` | Celery scheduler | - |
| `celery-flower` | Monitoring web UI | 5555 |
| `db-init` | Database initialization | - |

## 🚨 Error Handling

The application includes comprehensive error handling:

- **API Failures**: Automatic retry with exponential backoff
- **Database Errors**: Graceful handling with rollback
- **Network Timeouts**: Configurable timeout settings
- **Data Validation**: Input validation and sanitization

## 📝 Development Patterns

### Clean Architecture
- **Models**: Database entities (`app/database.py`)
- **Tasks**: Celery task definitions (`app/tasks.py`)
- **Services**: Business logic layer (`app/services.py`)
- **Configuration**: Environment and settings (`app/config.py`)

### Testing Patterns
- **Fixtures**: Reusable test data and mocks
- **Mocking**: External API calls and database operations
- **Isolation**: Each test runs in isolation
- **Coverage**: Comprehensive test coverage

## 🔧 Troubleshooting

### Common Issues

1. **Database Connection Error**
   ```bash
   # Check if PostgreSQL is running
   docker-compose ps postgres
   
   # View database logs
   docker-compose logs postgres
   ```

2. **Redis Connection Error**
   ```bash
   # Check if Redis is running
   docker-compose ps redis
   
   # Test Redis connection
   docker-compose exec redis redis-cli ping
   ```

3. **Task Not Executing**
   ```bash
   # Check worker status
   docker-compose logs celery-worker
   
   # Check beat scheduler
   docker-compose logs celery-beat
   ```

4. **API Rate Limiting**
   - Adjust task intervals in configuration
   - Implement exponential backoff (already included)

### Performance Optimization

1. **Database Indexing**: Ensure proper indexes on foreign keys
2. **Connection Pooling**: Configure database connection pool
3. **Task Batching**: Process multiple records in single tasks
4. **Memory Management**: Monitor worker memory usage

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the logs for error details
