from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time
from models import BaseDb, User, CatalogCategory, CatalogItem

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
BaseDb.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

BaseDb.metadata.drop_all(engine)
BaseDb.metadata.create_all(engine)

# Create dummy user
user01 = User(
      email="test."+str(time.time())+"@udacity.com",
      name="Demo User",
      picture='https://pbs.twimg.com/profile_images/' +
      '2671170543/18debd694829ed78203a5a36dd364160_400x400.png'
      )
session.add(user01)
session.commit()

# Basketball
# Basketball
# Frisbee
# Snowboarding
# Rock Climbing
# Football
# Skating
# Hockey

cat01 = CatalogCategory(
      name="Soccer",
      background="soccer.jpg"
      )
session.add(cat01)
session.commit()

item01 = CatalogItem(
      user=user01,
      name="Nike FC Barcelonae",
      description="WM Ball 2019!",
      category=cat01
      )

session.add(item01)
session.commit()


cat02 = CatalogCategory(
       name="Basketball",
       background="basketball.jpg"
       )
session.add(cat02)
item02 = CatalogItem(
       user=user01,
       name="Jordon Basketball",
       description="Soft nice ball",
       category=cat02
       )
session.add(item02)

item02_02 = CatalogItem(
       user=user01,
       name="Cap",
       description="beautiful cap",
       category=cat02
       )
session.add(item02_02)

session.commit()


cat03 = CatalogCategory(
       name="Rock Climbing",
       background="climbing.jpg"
       )
session.add(cat03)
item03 = CatalogItem(
       user=user01,
       name="GridLock Magnetron Carabiner",
       description="Our innovative belay biner featuring Magnetron",
       category=cat03
       )
session.add(item03)

session.commit()


cat04 = CatalogCategory(
       name="Frisbee"
       )
session.add(cat04)
item04 = CatalogItem(
       user=user01,
       name="Frisbee Superfly",
       description="Here comes the descrpiton",
       category=cat04
       )
session.add(item04)

session.commit()


cat05 = CatalogCategory(
       name="Snowboarding",
       background="snowboarding.jpg"
       )
session.add(cat05)
item05 = CatalogItem(
       user=user01,
       name="Snowboard Jimmy",
       description="be fast in the snow",
       category=cat05
       )
session.add(item05)

cat06 = CatalogCategory(
       name="Skating",
       background="skating.jpg"
       )
session.add(cat06)
item06 = CatalogItem(
       user=user01,
       name="Skates Underground",
       description="nice skates",
       category=cat06
       )
session.add(item06)

session.commit()

print "added data!"
