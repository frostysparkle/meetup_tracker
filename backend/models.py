from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Attendee(db.Model):
    id = db.Column(db.String(256), primary_key=True) # SHA256 hashed string
    name = db.Column(db.String(120), nullable=False)
    smail = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_present = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'smail': self.smail,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_present': self.is_present
        }
