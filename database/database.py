from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json

from utils.logger_config import logger  # Centralized logger

Base = declarative_base()

class Token(Base):
    __tablename__ = 'tokens'
    id = Column(Integer, primary_key=True)
    mint = Column(String, unique=True, index=True)
    symbol = Column(String)
    score = Column(Integer)
    risks = Column(String)

class DatabaseManager:
    def __init__(self, db_url: str = 'sqlite:///tokens.db'):
        self.engine = create_engine(db_url)  # Update the URI if using a different database
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.session = self.SessionLocal()
        logger.debug("Database initialized.")

    def store_token(self, token_data: dict):
        token = Token(
            mint=token_data.get('mint'),
            symbol=token_data.get('tokenMeta', {}).get('symbol'),
            score=token_data.get('score'),
            risks=json.dumps(token_data.get('risks'))
        )
        self.session.add(token)
        try:
            self.session.commit()
            logger.info(f"Stored token data: {token}", extra={'token_name': token.symbol})
        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to store token data: {e}", extra={'token_name': token.symbol})

    def close(self):
        self.session.close()
        logger.info("Database session closed.") 