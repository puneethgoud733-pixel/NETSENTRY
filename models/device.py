from extensions import db
from datetime import datetime


class Device(db.Model):

    __tablename__ = "devices"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    device_type = db.Column(
        db.String(50),
        nullable=False
    )

    hostname = db.Column(
        db.String(100),
        nullable=False
    )

    ip_address = db.Column(
        db.String(45),
        nullable=False,
        unique=True
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Unknown"
    )

    response = db.Column(
        db.String(50),
        nullable=False,
        default="Not checked"
    )

    last_checked = db.Column(
        db.DateTime,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    alerts = db.relationship(
        "Alert",
        backref="device",
        lazy=True,
        cascade="all, delete-orphan"
    )

    history = db.relationship(
        "CheckHistory",
        backref="device",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def to_dict(self):

        return {
            "id": self.id,
            "device_type": self.device_type,
            "hostname": self.hostname,
            "ip_address": self.ip_address,
            "status": self.status,
            "response": self.response,
            "last_checked": (
                self.last_checked.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                if self.last_checked
                else None
            ),
            "created_at": (
                self.created_at.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                if self.created_at
                else None
            )
        }

    def __repr__(self):

        return f"<Device {self.hostname}>"


class Alert(db.Model):

    __tablename__ = "alerts"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    device_id = db.Column(
        db.Integer,
        db.ForeignKey("devices.id"),
        nullable=False
    )

    message = db.Column(
        db.String(255),
        nullable=False
    )

    severity = db.Column(
        db.String(20),
        nullable=False,
        default="Warning"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    resolved = db.Column(
        db.Boolean,
        default=False
    )

    def to_dict(self):

        return {
            "id": self.id,
            "device_id": self.device_id,
            "hostname": (
                self.device.hostname
                if self.device
                else "Unknown"
            ),
            "message": self.message,
            "severity": self.severity,
            "created_at": (
                self.created_at.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                if self.created_at
                else None
            ),
            "resolved": self.resolved
        }


class CheckHistory(db.Model):

    __tablename__ = "check_history"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    device_id = db.Column(
        db.Integer,
        db.ForeignKey("devices.id"),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        nullable=False
    )

    response = db.Column(
        db.String(50),
        nullable=False
    )

    checked_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def to_dict(self):

        return {
            "id": self.id,
            "device_id": self.device_id,
            "status": self.status,
            "response": self.response,
            "checked_at": (
                self.checked_at.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                if self.checked_at
                else None
            )
        }