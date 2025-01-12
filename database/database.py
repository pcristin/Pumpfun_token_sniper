from sqlalchemy import create_engine, Column, String, Integer, DateTime, Float, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
import json
import os
from contextlib import contextmanager

from utils.logger_config import logger
from config import DATABASE_URL

Base = declarative_base()

class Token(Base):
    __tablename__ = 'tokens'
    id = Column(Integer, primary_key=True)
    mint = Column(String, unique=True, index=True)
    symbol = Column(String)
    score = Column(Integer)
    risks = Column(String)

class TraderAnalysis(Base):
    __tablename__ = 'trader_analysis'
    id = Column(Integer, primary_key=True)
    token_address = Column(String, index=True)
    wallet_address = Column(String, index=True)
    balance = Column(Float)
    total_transactions = Column(Integer)
    successful_trades = Column(Integer)
    failed_trades = Column(Integer)
    unique_tokens_traded = Column(Integer)
    last_active = Column(DateTime)
    analyzed_at = Column(DateTime, index=True)

class DatabaseManager:
    _instance = None

    def __new__(cls, db_url: str = DATABASE_URL):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_url: str = DATABASE_URL):
        if self._initialized:
            return

        try:
            # Ensure database directory exists
            db_dir = os.path.dirname(db_url.replace('sqlite:///', ''))
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)
                logger.info(f"Created database directory: {db_dir}")

            # Configure engine with connection pooling
            self.engine = create_engine(
                db_url,
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=1800
            )
            
            self._verify_database()
            self.SessionLocal = scoped_session(sessionmaker(bind=self.engine))
            self._initialized = True
            logger.info("Database initialized successfully with connection pooling.")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def _verify_database(self):
        """Verify database and tables existence, create if necessary."""
        inspector = inspect(self.engine)
        
        try:
            # Create tables if they don't exist
            Base.metadata.create_all(self.engine)
            
            # Verify that all required tables were created
            required_tables = {table.__tablename__ for table in [Token, TraderAnalysis]}
            existing_tables = set(inspector.get_table_names())
            
            missing_tables = required_tables - existing_tables
            if missing_tables:
                raise Exception(f"Failed to create tables: {missing_tables}")
                
            logger.debug(f"Database verification complete. All required tables exist: {required_tables}")
        except Exception as e:
            logger.error(f"Database verification failed: {e}")
            raise

    @contextmanager
    def get_session(self):
        """Context manager for database sessions."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

    def store_token(self, token_data: dict):
        with self.get_session() as session:
            token = Token(
                mint=token_data.get('mint'),
                symbol=token_data.get('tokenMeta', {}).get('symbol'),
                score=token_data.get('score'),
                risks=json.dumps(token_data.get('risks'))
            )
            session.add(token)
            try:
                session.commit()
                logger.info(f"Stored token data: {token}", extra={'token_name': token.symbol})
            except Exception as e:
                logger.error(f"Failed to store token data: {e}", extra={'token_name': token.symbol})
                raise

    def store_trader_analysis(self, analysis_data: dict):
        with self.get_session() as session:
            analysis = TraderAnalysis(
                token_address=analysis_data.get('token_address'),
                wallet_address=analysis_data.get('wallet_address'),
                balance=analysis_data.get('balance'),
                total_transactions=analysis_data.get('total_transactions'),
                successful_trades=analysis_data.get('successful_trades'),
                failed_trades=analysis_data.get('failed_trades'),
                unique_tokens_traded=analysis_data.get('unique_tokens_traded'),
                last_active=analysis_data.get('last_active'),
                analyzed_at=analysis_data.get('analyzed_at')
            )
            session.add(analysis)
            try:
                session.commit()
                logger.info(f"Stored trader analysis", 
                        extra={'module_name': 'TraderAnalytics', 
                                'wallet': analysis_data.get('wallet_address')})
            except Exception as e:
                logger.error(f"Failed to store trader analysis: {e}", 
                            extra={'module_name': 'TraderAnalytics', 
                                'wallet': analysis_data.get('wallet_address')})
                raise

    def close(self):
        self.SessionLocal.remove()
        self.engine.dispose()
        logger.info("Database connections closed.") 