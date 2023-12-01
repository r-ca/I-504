from ..base import Base
from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Boolean

class TwitterTweets(Base):

    __tablename__ = 'source_twitter_tweets'

    entry_id = Column(String(64), primary_key=True)
    created_at = Column(DateTime)
    full_text = Column(String(4096))
    user_rest_id = Column(Integer(64), ForeignKey('source_twitter_users.user_rest_id'))

class TwitterUsers(Base):
    __tablename__ = 'source_twitter_users'

    user_rest_id = Column(Integer(64), primary_key=True)
    screen_name = Column(String(64))
    name = Column(String(64))
    description = Column(String(4096))
    protected = Column(Boolean)
    banner_url = Column(String(1024))
    profile_image_url = Column(String(1024))


