from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
BaseDb = declarative_base()

class User(BaseDb):
  __tablename__ = 'user'

  id = Column(Integer, primary_key = True)
  email = Column(String(250),nullable=False,unique=True)
  name = Column(String(80))
  picture = Column(String(250),default='default.jpg')
  password = Column(String(250),nullable=True)

  gplus_access_token = Column(String(250))
  gplus_id = Column(String(250))
  gplus_expired_at = Column(String(250))

  facebook_access_token = Column(String(250))
  facebook_id = Column(String(250))
  facebook_expired_at = Column(String(250))

  items = relationship('CatalogItem', backref='user', lazy=True)

class CatalogCategory(BaseDb):
    __tablename__ = 'catalog_category'

    id = Column(Integer, primary_key = True)
    name =Column(String(80), nullable = False)
    background = Column(String(250))
    items = relationship('CatalogItem', backref='catalog_category', lazy=True)

class CatalogItem(BaseDb):
    __tablename__ = 'catalog_item'

    id = Column(Integer, primary_key = True)
    name =Column(String(80), nullable = False)
    description = Column(String(250))
  
    user_id = Column(Integer,ForeignKey('user.id'))

    category_id = Column(Integer,ForeignKey('catalog_category.id'))


    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'id'           : self.id,
           'name'         : self.name,
           'description'  : self.description
       }

engine = create_engine('sqlite:///catalog.db')
 
BaseDb.metadata.create_all(engine)