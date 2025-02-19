from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
import pytz

db = SQLAlchemy()
    
class Member(db.Model, UserMixin):
    Memb_id = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(50), nullable = False)
    Password = db.Column(db.String(10), nullable=False)
    Address = db.Column(db.String(100), nullable = False)
    Memb_type = db.Column(db.String(50), nullable = False)

    def get_id(self):
        return str(self.Memb_id)

class Books(db.Model):
    Book_id = db.Column(db.Integer, primary_key=True)
    Author = db.Column(db.String(50), nullable = False)
    Price = db.Column(db.String(50), nullable = False)
    Title = db.Column(db.String(50), nullable = False)
    Genre = db.Column(db.String(50), nullable = False)
    Availability = db.Column(db.Integer, nullable=False)
    borrower = db.relationship('Member', backref = "issue", secondary = "relationship")

    def get_id(self):
        return str(self.Book_id)
    
class Relationship(db.Model):
    R_id = db.Column(db.Integer, primary_key=True)
    Memb_id = db.Column(db.Integer, db.ForeignKey("member.Memb_id"))
    Book_id = db.Column(db.Integer, db.ForeignKey("books.Book_id"))
    Issue_date = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone('Asia/Kolkata')))
    Return_date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')) + timedelta(days=7))
