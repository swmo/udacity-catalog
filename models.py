from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import json

BaseDb = declarative_base()


class User(BaseDb):
    __tablename__ = 'user'

    id = Column(
        Integer,
        primary_key=True
        )
    email = Column(
        String(250),
        nullable=False,
        unique=True
        )
    name = Column(
        String(80)
        )
    picture = Column(
        String(250),
        default='/static/images/default_avatar.png'
        )
    password = Column(
        String(250),
        nullable=True
        )
    items = relationship(
        'CatalogItem',
        backref='user',
        lazy=True
        )

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name
        }


class CatalogCategory(BaseDb):
        __tablename__ = 'catalog_category'

        id = Column(
            Integer,
            primary_key=True
            )
        name = Column(
            String(80),
            nullable=False
            )
        background = Column(
            String(250),
            default='default.jpg'
            )
        items = relationship(
            'CatalogItem',
            backref='category',
            lazy=True
            )

        @property
        def serialize(self):
            items = ([i.serialize for i in self.items])
            return {
                'id': self.id,
                'name': self.name,
                'items': items
            }


class CatalogItem(BaseDb):
        __tablename__ = 'catalog_item'

        id = Column(
            Integer,
            primary_key=True
            )
        name = Column(
            String(80),
            nullable=False
            )
        description = Column(
            String(1000)
            )
        user_id = Column(
            Integer,
            ForeignKey('user.id')
            )
        category_id = Column(
            Integer,
            ForeignKey('catalog_category.id')
            )

        @property
        def serialize(self):
            user = ([self.user.serialize])
            return {
                'id': self.id,
                'name': self.name,
                'description': self.description,
                'created_by': user
            }


engine = create_engine('sqlite:///catalog.db')

BaseDb.metadata.create_all(engine)
