from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import *

# ============================ Configuration ============================

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///LibraryData.sqlite3"
app.config['SECRET_KEY'] = "MyLibrary"

db.init_app(app)
app.app_context().push()

# Create login manager
login_manager = LoginManager(app)

# Configure login manager for admin
@login_manager.user_loader
def load_user(memb_id):
    return Member.query.get(int(memb_id))

@login_manager.unauthorized_handler
def unauthorized():
    return redirect('/login')

# ============================ Controllers ==============================

@app.route('/', methods=['GET', 'POST'])
def main_page():
    return render_template('main_page.html')

# ======================== Login/out & Signup ============================

#Define login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', msg = 0)
    if request.method == 'POST':
        role = username = request.form['role']
        username = request.form['username']
        password = request.form['password']
        member = Member.query.filter_by(Username=username).first()
        if member and member.Password == password:
            if member.Memb_type == role:
                if role == 'admin':
                    login_user(member)
                    return redirect('/admin')
                if role == 'user':
                    login_user(member)
                    return redirect('/user')
            else:
                return render_template('login.html', msg = 'Wrong role selected 💀')
        else:
            return render_template('login.html', msg = 'Invalid credentials')
        
# Define user signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html', msg = 0)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        address = request.form['address']
        member = Member.query.filter_by(Username=username).first()
        if member:
            return render_template('signup.html', msg = 'Username already exists')  
        else:
            u = Member(Username = username, Password = password, Address = address, Memb_type = 'user')
            db.session.add(u)
            db.session.commit()
            return render_template('login.html', msg2 = 'Signup Successful! Please login to continue')

#Define logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

# ============================== Admin Side ================================

#Admin dashboard
@app.route('/admin', methods = ['GET', 'POST'])
@login_required
def admin_home():
    admin = current_user.Username
    return render_template('admin_home.html', admin = admin)

#All books
@app.route('/admin/all_books', methods = ['GET', 'POST'])
@login_required
def all_books():
    books = Books.query.all()
    return render_template('all_books.html', books = books)

#Add book
@app.route('/admin/all_books/add_books', methods = ['GET', 'POST'])
@login_required
def add_books():
    if request.method == 'GET':
        return render_template('add_books.html', msg = 0)
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')      
        price = float(request.form.get('price'))
        genre = request.form.get('genre')
        availability = int(request.form.get('availability'))
        b1 = Books.query.filter_by(Title = title, Author = author, Price = price, Genre = genre).first()
        if b1:
            return render_template('add_books.html', msg = 'Book already exists')
        else:
            b = Books(Title = title, Author = author, Price = price, Genre = genre, Availability = availability)
            db.session.add(b)
            db.session.commit()
        return redirect('/admin/all_books')
    
#Update book
@app.route('/admin/all_books/upd_book/<int:id>', methods = ['GET', 'POST'])
@login_required
def upd_book(id):
    s = Books.query.get(id)
    if request.method == 'GET':
        return render_template('upd_book.html', s = s)
    if request.method == 'POST':    
        s.Title = request.form.get('title')
        s.Author = request.form.get('author')
        s.Price = float(request.form.get('price'))        
        s.Genre = request.form.get('genre')
        s.Availability = int(request.form.get('availability'))
        db.session.commit()
        return redirect('/admin/all_books')
    
#Delete book- del_warning.html
@app.route('/admin/all_books/del_book/<int:id>', methods = ['GET', 'POST'])
@login_required
def del_book(id):
    b = Books.query.get(id)
    if not b:
        return redirect('/admin/all_books')
    form_act = "/admin/all_books/del_book/" + str(id)
    No = "/admin/all_books"
    what = "Book Id"
    if request.method == 'GET':
        return render_template('del_warning.html', id = id, form_act = form_act, No = No, what = what)
    if request.method == 'POST':
        db.session.delete(b)
        db.session.commit()
        return redirect('/admin/all_books')
    
#Check Issue Records
@app.route('/admin/issue_record', methods = ['GET'])
@login_required
def issue_record():
    rec = Relationship.query.all()
    return render_template('issue_record.html', rec = rec)

#Delete Issue Records
@app.route('/admin/issue_record/del_rec/<int:id>', methods = ['GET', 'POST'])
@login_required
def del_rec(id):
    r = Relationship.query.get(id)
    if not r:
        return redirect('/admin/issue_record')
    form_act = "/admin/issue_record/del_rec/" + str(id)
    No = "/admin/issue_record"
    what = "Issue Id"
    if request.method == 'GET':
        return render_template('del_warning.html', id = id, form_act = form_act, No = No, what = what)
    if request.method == 'POST':
        b = Books.query.get(r.Book_id)
        b.Availability += 1
        db.session.delete(r)
        db.session.commit()
        return redirect('/admin/issue_record')
    
#All Members
@app.route('/admin/all_members', methods = ['GET', 'POST'])
@login_required
def all_members():
    memb = Member.query.all()
    return render_template('all_members.html', memb = memb)

#Update Members
@app.route('/admin/all_members/upd_member/<int:id>', methods = ['GET', 'POST'])
@login_required
def upd_member(id):
    memb = Member.query.get(id)
    if memb.Memb_type == 'user':
        code = '''<input type="radio" name="role" value="admin" id="role">Admin<input type="radio" name="role" value="user" checked>User'''
    else:
        code = '''<input type="radio" name="role" value="admin" checked>Admin<input type="radio" name="role" value="user" id="role">User'''
    if request.method == 'GET':
        return render_template('upd_member.html', memb = memb, code = code)
    if request.method == 'POST':    
        memb.Username = request.form.get('username')
        memb.Address = request.form.get('address')
        memb.Memb_type = request.form.get('role')
        db.session.commit()
        return redirect('/admin/all_members')
    
#Delete Members
@app.route('/admin/all_members/del_member/<int:id>', methods = ['GET', 'POST'])
@login_required
def del_member(id):
    b = Member.query.get(id)
    if not b:
        return redirect('/admin/all_members')
    form_act = "/admin/all_members/del_member/" + str(id)
    No = "/admin/all_members"
    what = "Member Id"
    if request.method == 'GET':
        return render_template('del_warning.html', id = id, form_act = form_act, No = No, what = what)
    if request.method == 'POST':
        db.session.delete(b)
        db.session.commit()
        return redirect('/admin/all_members')

# ============================== User Side ================================

#User dashboard
@app.route('/user', methods = ['GET'])
@login_required
def user_home():
    user = current_user
    books = Books.query.all()
    err01 = request.args.get('err01')
    err02 = request.args.get('err02')
    msg01 = request.args.get('msg01')
    return render_template('user_home.html', books = books, user = user, err01 = err01, err02 = err02, msg01 = msg01)

#Borrow a book
@app.route('/user/borrow/<int:id>', methods = ['GET'])
@login_required
def borrow(id):
    b = Books.query.get(id)
    if not b:
        return redirect('/user')
    user = current_user
    # books = Books.query.all()
    if b.Availability == 0:
        return redirect(url_for('user_home', err01 = 1))
        # return render_template('user_home.html', books = books, user = user, msg = 'Sorry! The book is not available')
    else:
        r = Relationship.query.filter_by(Memb_id = user.Memb_id, Book_id = id).first()
        if r:
            return redirect(url_for('user_home', err02 = 1))
            # return render_template('user_home.html', books = books, user = user, msg = 'Book already borrowed! Check the details in the My Books tab.')
        else:
            b.Availability =  b.Availability - 1
            b.borrower.append(user)
            db.session.commit()
            return redirect(url_for('user_home', msg01 = 1))
            #return render_template('user_home.html', books = books, user = user, msg2 = 'Book borrowed successfully! Check the return date in the My Books tab.')
            
#My Books record
@app.route('/user/issue_record/<int:id>', methods = ['GET'])
@login_required
def my_books(id):
    user = current_user
    rec = Relationship.query.filter_by(Memb_id = id).all() 
    return render_template('my_books.html', rec = rec, user = user)

# ============================ Debugging ==============================

if __name__ == "__main__":
    app.run(debug = True)