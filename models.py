"""SQLAlchemy models for Warbler."""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

class Notification(db.Model):
    """notifications for users"""

    __tablename__ = 'notifications'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    notification_txt = db.Column(db.String(20), nullable=False)

    date = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow(),
    )

    from_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False,
        
    )
    to_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False,
    )
    from_user = db.relationship('User', foreign_keys=[from_id])
    user = db.relationship('User', foreign_keys=[to_id], backref="notifications")

class Block(db.Model):
    """Blocked user lists"""

    __tablename__ = 'blocks'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    user = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False,
        
    )
    blocked_user = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False,
    )
    blocked = db.relationship('User', foreign_keys=[blocked_user])
    users = db.relationship('User', foreign_keys=[user], backref="blocks")

    def __repr__(self):
        return f"<Block #{self.id}: {self.user}, {self.blocked_user}>"

class Follows(db.Model):
    """Connection of a follower <-> followed_user."""

    __tablename__ = 'follows'

    user_being_followed_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )

    user_following_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )


class Likes(db.Model):
    """Mapping user likes to warbles."""

    __tablename__ = 'likes' 

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade')
    )

    message_id = db.Column(
        db.Integer,
        db.ForeignKey('messages.id', ondelete='cascade')
    )


class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    image_url = db.Column(
        db.Text,
        default="/static/images/default-pic.png",
    )

    header_image_url = db.Column(
        db.Text,
        default="/static/images/warbler-hero.jpg"
    )

    bio = db.Column(
        db.Text,
    )

    location = db.Column(
        db.Text,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )
    is_private = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )
    is_verified = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )
    is_admin = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    messages = db.relationship('Message', cascade="all, delete-orphan")

    followers = db.relationship(
        "User",
        secondary="follows",
        primaryjoin=(Follows.user_being_followed_id == id),
        secondaryjoin=(Follows.user_following_id == id)
    )

    following = db.relationship(
        "User",
        secondary="follows",
        primaryjoin=(Follows.user_following_id == id),
        secondaryjoin=(Follows.user_being_followed_id == id)
    )

    likes = db.relationship(
        'Message',
        secondary="likes"
    )


    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    def is_followed_by(self, other_user):
        """Is this user followed by `other_user`?"""

        found_user_list = [user for user in self.followers if user == other_user]
        return len(found_user_list) == 1

    def is_following(self, other_user):
        """Is this user following `other_use`?"""

        found_user_list = [user for user in self.following if user == other_user]
        return len(found_user_list) == 1
    def accept_follow_req(self, other_user, n):
        self.notifications.remove(n)
        self.followers.append(other_user)
        db.session.commit()
    # def get_messages():
    #     all_messages = (Message.query.order_by(Message.timestamp.desc()).all())
    #     messages = [msg for msg in all_messages if g.user in msg.user.followers or msg.user == g.user]
    #     messages = messages[:100]
    #     return messages
    def check_for_blocked(self, other_user):
        """this will iterate of the blocks list for user, returns true or false if blocked."""
        is_blocked = Block.query.filter_by(user=self.id, blocked_user=other_user.id).first()
        if is_blocked in self.blocks:
            return True
        return False
    def get_blocked_users(self):
        """Will output a list of blocked users for self user"""
        block_list = [User.query.get(block.blocked_user) for block in self.blocks]
        return block_list

    @classmethod
    def signup(cls, username, email, password, image_url):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False
    @classmethod
    def change_password(cls, username, password, new_password):
        """Authenticate username & password, then encrypt new password & store it into db"""
        if cls.authenticate(username, password):
            user = cls.query.filter_by(username=username).first()
            new_hashed_pwd = bcrypt.generate_password_hash(new_password).decode('UTF-8')
            user.password = new_hashed_pwd
            db.session.add(user)
            return user
        else:
            return False


class Message(db.Model):
    """An individual message ("warble")."""

    __tablename__ = 'messages'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    text = db.Column(db.String(280), nullable=False)

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow(),
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    user = db.relationship('User')





def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)
