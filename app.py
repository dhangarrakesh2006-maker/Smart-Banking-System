from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from decimal import Decimal
from werkzeug.utils import secure_filename

# App setup
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET', 'dev-secret')
# prefer to auto-reload templates during development
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('instance', exist_ok=True)

# Try to wire up a database if models.py is present
use_db = False
try:
  from models import db, User, ATM
  use_db = True
  # Use absolute path and forward slashes so SQLite opens correctly on Windows
  db_path = os.path.abspath(os.path.join('instance', 'smartbank.sqlite'))
  db_uri = 'sqlite:///' + db_path.replace('\\', '/')
  app.config.setdefault('SQLALCHEMY_DATABASE_URI', db_uri)
  app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)
  db.init_app(app)
except Exception:
  use_db = False


@app.route('/')
def home():
  users = []
  total_balance = '0.00'
  if use_db:
    try:
      users = User.query.all()
      total = sum([float(u.balance) if u.balance is not None else 0 for u in users])
      total_balance = f"{total:,.2f}"
    except Exception:
      users = []
      total_balance = '0.00'
  return render_template('project.html', users=users, total_balance=total_balance)


@app.route('/project')
def project():
  return render_template('project.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    balance_field = request.form.get('balance', '').strip()

    if not (name and email and password):
      flash('Name, email and password are required.', 'error')
      return redirect(url_for('register'))

    if not use_db:
      flash('Registration unavailable: database not configured on server.', 'error')
      return redirect(url_for('register'))

    # check existing
    existing = User.query.filter_by(email=email).first()
    if existing:
      flash('Email already registered.', 'error')
      return redirect(url_for('register'))

    u = User(name=name, email=email)
    try:
      u.set_password(password)
    except Exception:
      u.password_hash = password

    try:
      u.balance = Decimal(balance_field) if balance_field else Decimal('0.00')
    except Exception:
      u.balance = Decimal('0.00')

    db.session.add(u)
    db.session.commit()

    # redirect to upload face page
    flash('Account created. Please upload face image.', 'success')
    return redirect(url_for('upload_face', user_id=u.id))

  return render_template('register.html')



@app.route('/login', methods=['POST'])
def login():
  try:
    # Simple login: use email as user id
    if not use_db:
      flash('Login unavailable: database not configured.', 'error')
      return redirect(url_for('home'))
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    if not email or not password:
      flash('Please provide login id and password.', 'error')
      return redirect(url_for('home'))
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
      flash('Invalid credentials.', 'error')
      return redirect(url_for('home'))
    # login success
    session.clear()
    session['user_id'] = user.id
    flash(f'Welcome back, {user.name}!', 'success')
    return redirect(url_for('dashboard'))
  except Exception as e:
    # log and show friendly message
    print('Login error:', e)
    flash('Server error during login. Please try again.', 'error')
    return redirect(url_for('home'))


@app.route('/dashboard')
def dashboard():
  if not use_db:
    flash('Dashboard unavailable: database not configured.', 'error')
    return redirect(url_for('home'))
  uid = session.get('user_id')
  if not uid:
    flash('Please login to access your account.', 'error')
    return redirect(url_for('home'))
  user = User.query.get(uid)
  if not user:
    flash('User not found.', 'error')
    return redirect(url_for('home'))
  return render_template('dashboard.html', user=user)


@app.route('/logout')
def logout():
  session.clear()
  flash('You have been logged out.', 'info')
  return redirect(url_for('home'))


# face upload
ALLOWED_EXT = {'png', 'jpg', 'jpeg'}
def allowed_filename(filename):
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT


@app.route('/upload-face/<int:user_id>', methods=['GET', 'POST'])
def upload_face(user_id):
  if not use_db:
    flash('Database not configured', 'error')
    return redirect(url_for('home'))

  user = User.query.get_or_404(user_id)
  if request.method == 'POST':
    f = request.files.get('face')
    if not f or f.filename == '':
      flash('No file selected', 'error')
      return redirect(url_for('upload_face', user_id=user_id))
    if not allowed_filename(f.filename):
      flash('Invalid file type (png/jpg/jpeg only)', 'error')
      return redirect(url_for('upload_face', user_id=user_id))

    fname = secure_filename(f.filename)
    ext = fname.rsplit('.', 1)[1].lower()
    save_name = f'user_{user.id}.{ext}'
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], save_name)
    f.save(save_path)

    user.face_filename = save_name
    db.session.commit()
    flash('Face uploaded successfully', 'success')
    return redirect(url_for('home'))

  return render_template('upload_face.html', user=user)


@app.route('/api/atms')
def api_atms():
  """Return ATMs for a given pincode. Query param: pincode"""
  if not use_db:
    return {'error': 'database unavailable'}, 503
  pincode = request.args.get('pincode', '').strip()
  if not pincode:
    return {'error': 'pincode required'}, 400
  atms = ATM.query.filter_by(pincode=pincode).all()
  return {'pincode': pincode, 'count': len(atms), 'atms': [a.to_dict() for a in atms]}


if use_db:
  @app.cli.command('seed-atms')
  def seed_atms():
    """Seed sample ATMs for Shirpur and Shindkhed pincodes."""
    with app.app_context():
      # sample list
      samples = [
        {'name': 'Shirpur Bank ATM - Main Street', 'address': 'Near Market, Shirpur', 'pincode': '425405', 'latitude': 20.756000, 'longitude': 74.591000},
        {'name': "Shindkhed ATM - Central", 'address': 'Opposite Bus Stand, Shindkhed', 'pincode': '425403', 'latitude': 20.760500, 'longitude': 74.598200},
      ]
      created = 0
      for s in samples:
        exists = ATM.query.filter_by(name=s['name']).first()
        if not exists:
          a = ATM(name=s['name'], address=s['address'], pincode=s['pincode'], latitude=s['latitude'], longitude=s['longitude'])
          db.session.add(a)
          created += 1
      db.session.commit()
      print(f'Seeded {created} ATM(s)')


if use_db:
  @app.cli.command('init-db')
  def init_db():
    """Create database tables."""
    with app.app_context():
      db.create_all()
      print('Initialized the database.')


if __name__ == '__main__':
  # When running directly, enable debug and make static/template changes appear without restarting where possible
  app.run(host='127.0.0.1', port=5000, debug=True)


@app.after_request
def add_header_no_cache(response):
  """During development, prevent caching of static files so changes show immediately in browser."""
  try:
    if app.debug and request.path.startswith('/static/'):
      response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
  except Exception:
    pass
  return response