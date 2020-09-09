"""Seed file to create db tables"""
from models import db, Symbol
from app import app

# Create all tables
db.drop_all()
db.create_all()


# Add default symbol
symbol = Symbol(symbol="<i class='symbol fas fa-seedling' style='color:#228B22;'></i>")
db.session.add(symbol)
db.session.commit()
