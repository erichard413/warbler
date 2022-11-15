import os

from flask import Flask, render_template, request, flash, redirect, session, g
# from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import UserAddForm, LoginForm, MessageForm, UserUpdateForm, UpdatePasswordForm, PrivacySettingsForm, AdminUserUpdateForm
from models import db, connect_db, User, Message, Likes, Notification, Block

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (os.environ.get('DATABASE_URL', 'postgresql:///warbler')).replace("://", "ql://", 1)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
# toolbar = DebugToolbarExtension(app)

connect_db(app)


##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
        g.msg_form = MessageForm()
    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)
        if user.following == []:
                flash(f"Hello, {user.username}. Let's get started! Follow some users below!", "success")
                return redirect("/users")
        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            do_login(user)
            if user.following == []:
                flash(f"Welcome back, {user.username}. Follow some users below!", "success")
                return redirect("/users")
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""
    do_logout()
    flash("You have been logged out.", "success")
    return redirect('/')
    


##############################################################################
# General user routes:

@app.route('/users')
def list_users():
    """Page with listing of users.

    Can take a 'q' param in querystring to search by that username.
    """

    search = request.args.get('q')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()

    return render_template('users/index.html', users=users)


@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile."""

    user = User.query.get_or_404(user_id)
    blocked = g.user.check_for_blocked(user)
    # snagging messages in order from the database;
    # user.messages won't be in order by default
    messages = (Message
                .query
                .filter(Message.user_id == user_id)
                .order_by(Message.timestamp.desc())
                .limit(100)
                .all())
    return render_template('users/show.html', user=user, messages=messages, blocked=blocked)


@app.route('/users/<int:user_id>/following')
def show_following(user_id):
    """Show list of people this user is following."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/following.html', user=user)


@app.route('/users/<int:user_id>/followers')
def users_followers(user_id):
    """Show list of followers of this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/followers.html', user=user)


@app.route('/users/follow/<int:follow_id>', methods=['POST'])
def add_follow(follow_id):
    """Add a follow for the currently-logged-in user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    followed_user = User.query.get_or_404(follow_id)
    g.user.following.append(followed_user)
    db.session.commit()

    return redirect(f"/users/{g.user.id}/following")

@app.route('/users/follow/request/<follow_id>', methods=["POST"])
def add_follow_request(follow_id):
    """sends a notification request to user"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    new_notification = Notification(notification_txt="follow_request", from_id=g.user.id, to_id=follow_id)
    db.session.add(new_notification)
    db.session.commit()
    flash('Follow request sent!', 'success')
    return redirect(f'/users/{follow_id}')


@app.route('/users/stop-following/<int:follow_id>', methods=['GET','POST'])
def stop_following(follow_id):
    """Have currently-logged-in-user stop following this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    followed_user = User.query.get(follow_id)
    g.user.following.remove(followed_user)
    db.session.commit()

    return redirect(f"/users/{g.user.id}/following")


@app.route('/users/profile', methods=["GET", "POST"])
def profile():
    """Update profile for current user."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    form = UserUpdateForm(obj=g.user)
    if form.validate_on_submit():

        pw = form.password.data
        if User.authenticate(g.user.username, pw):
            for fieldname, value in form.data.items():
                if fieldname != 'password':
                    setattr(g.user, fieldname, value)
            db.session.commit()
            flash(f'The user has been updated', 'success')
            return redirect('/users/profile')
        else:
            flash(f'Invalid password!', 'danger')
            return redirect('/')
    
    return render_template("users/edit.html", form=form)

@app.route('/users/<int:user_id>/edit', methods=["GET","POST"])
def admin_edit_profile(user_id):
    """GET - show edit form for user. POST - update form"""
    if not g.user.is_admin:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    user = User.query.get_or_404(user_id)
    form = AdminUserUpdateForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.image_url = form.image_url.data
        user.header_image_url = form.header_image_url.data
        user.is_private = form.is_private.data
        user.is_admin = form.is_admin.data
        user.is_verified = form.is_verified.data
        db.session.commit()
        flash('User updated successfully', 'success')
        return redirect(f'/users/{user_id}')
    else:
        user = User.query.get_or_404(user_id)
        return render_template('/users/adminedit.html', user=user, form=form)

@app.route('/users/delete', methods=["GET","POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")

@app.route('/users/<int:user_id>/delete', methods=["GET","POST"])
def delete_selected_user(user_id):
    """ADMIN ONLY Delete user."""

    if not g.user.is_admin:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect("/")

@app.route('/users/settings')
def settings_page():
    """show settings form"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    return render_template("users/settings.html")
@app.route('/users/privacy')
def privacy_settings():
    """show privacy settings form"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    form = PrivacySettingsForm(obj=g.user)
    return render_template('users/privacy.html', form=form)
    

@app.route('/users/privacy/<int:user_id>', methods=["GET","POST"])
def privacy_settings_edit(user_id):
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    form = PrivacySettingsForm()
    g.user.is_private = form.is_private.data
    db.session.commit()
    flash('Privacy settings updated successfully!', 'success')
    return redirect('/users/privacy')
    

@app.route('/users/changepw', methods=["GET","POST"])
def change_pw_form():
    form = UpdatePasswordForm()

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    if form.validate_on_submit():
        password = form.password.data
        new_password = form.new_password.data
        if User.change_password(g.user.username, password, new_password):
            db.session.commit()
            flash('Password change successful!', "success")
            return redirect('/users/settings')
        else:
            flash('Invalid credentials. Please check password & try again.', 'danger')
            return redirect('/users/changepw')    
    return render_template('users/changepw.html', form=form)
    
@app.route('/users/<user_id>/notifications')
def show_notification_page(user_id):
    """Show notification page"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    notifications = Notification.query.filter_by(to_id=user_id)
    return render_template('/users/notifications.html', notifications=notifications)

@app.route('/users/accept-follow/<int:from_id>/<int:notification_id>', methods=["POST"])
def accept_follow(from_id, notification_id):
    """accepts follow, adds new follow to user following list"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    from_user = User.query.get_or_404(from_id)
    n = Notification.query.get_or_404(notification_id)
    g.user.accept_follow_req(from_user, n)
    db.session.delete(n)
    db.session.commit()
    flash(f'Accepted follow request from {from_user.username}', 'success')
    return redirect(f'/users/{g.user.id}')
@app.route('/users/reject-follow/<int:from_id>/<int:notification_id>', methods=["POST"])
def reject_follow(from_id, notification_id):
    """rejects follow, clears notification"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    n = Notification.query.get_or_404(notification_id)
    g.user.notifications.remove(n)
    db.session.delete(n)
    db.session.commit()
    flash(f'Declined follow request from {from_user.username}', 'success')
    return redirect(f'/users/{g.user.id}')
    



##############################################################################
# Messages routes:

@app.route('/messages/new', methods=["GET", "POST"])
def messages_add():
    """Add a message:

    Show form if GET. If valid, update message and redirect to user page.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = MessageForm()

    if form.validate_on_submit():
        msg = Message(text=form.text.data)
        g.user.messages.append(msg)
        db.session.commit()
        flash('Message posted successfully!', 'success')
        return redirect('/')

    return render_template('messages/new.html', form=form)


@app.route('/messages/<int:message_id>', methods=["GET"])
def messages_show(message_id):
    """Show a message."""

    msg = Message.query.get(message_id)
    return render_template('messages/show.html', message=msg)


@app.route('/messages/<int:message_id>/delete', methods=["GET","POST"])
def messages_destroy(message_id):
    """Delete a message."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    msg = Message.query.get(message_id)
    db.session.delete(msg)
    db.session.commit()
    flash('Message deleted successfully', 'success')
    return redirect(f"/users/{g.user.id}")
@app.route('/messages/all')
def messages_show_all():
    """page to view all messages - even users who aren't followed"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    shown_msgs = Message.query.all()
    msg = [message for message in shown_msgs if g.user.check_for_blocked(message.user) == False]
    
    return render_template('home.html', messages=msg)


##############################################################################
# Like routes

@app.route('/users/add_like/<int:msg_id>', methods=["POST"])
def like_post(msg_id):
    """Route for liking a post"""
    msg = Message.query.get(msg_id)
    if msg in g.user.likes:
        g.user.likes.remove(msg)
        
        db.session.commit()
        return ("",201)
    else:
        g.user.likes.append(msg)
        db.session.commit()
        return ("",201)


@app.route('/users/<int:user_id>/likes')
def show_liked_posts(user_id):
    """Shows page with lists of liked posts"""
    user = User.query.get(user_id)
    user_likes = user.likes    
    return (render_template(f'/users/likes.html', messages=user_likes))
##############################################################################
# Homepage and error pages

#########################BLOCK USERS##########################################
@app.route('/users/block/<int:user_id>', methods=["GET","POST"])
def block_this_user(user_id):
    """Blocks user"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    user = User.query.get_or_404(user_id)
    if g.user.check_for_blocked(user):
        block = Block.query.filter_by(user=g.user.id, blocked_user=user.id).first()
        db.session.delete(block)
        db.session.commit()
        flash('User unblocked!', 'danger')
        return redirect(f'/users/{user_id}')    
    else:
        new_block = Block(user=g.user.id, blocked_user=user.id)
        db.session.add(new_block)
        db.session.commit()
        flash('User blocked!', 'danger')
        return redirect(f'/users/{user_id}')

@app.route('/users/blocked')
def show_blocked_users():
    if not g.user:
        flash("Access unauthorized.", 'danger')
        return redirect('/')
    block_list = g.user.get_blocked_users()
    return render_template("users/blockedusers.html", blocked_users = block_list)


@app.route('/')
def homepage():
    """Show homepage:

    - anon users: no messages
    - logged in: 100 most recent messages of followed_users
    """
    ## NOTE - I do not think this is the correct way to handle this request. But it is functionable!
    if g.user:
        all_messages = (Message.query.order_by(Message.timestamp.desc()).all())
        messages = [msg for msg in all_messages if g.user in msg.user.followers or msg.user == g.user and not g.user.check_for_blocked(msg.user)]
        messages = messages[:100]
    #    messages = g.user.get_messages()
        return render_template('home.html', messages=messages)
    else:
        return render_template('home-anon.html')
@app.errorhandler(404)
def not_found_err():
    """displays when 404'd"""
    flash("404 - Page not found!", "danger")
    return redirect("/")
@app.errorhandler(500)
def unexpected_request():
    """displays when 500'd"""
    flash("404 - Page not found!", "danger")
    return redirect("/")


##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req
