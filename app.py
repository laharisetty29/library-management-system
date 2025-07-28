from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'library_secret_key'

# --- Database Setup ---
def init_db():
    with sqlite3.connect('library.db') as con:
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            author TEXT,
            genre TEXT,
            quantity INTEGER
        )''')
        cur.execute('''CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT
        )''')
        cur.execute('''CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            member_id INTEGER,
            issue_date TEXT,
            return_date TEXT,
            returned INTEGER DEFAULT 0,
            FOREIGN KEY(book_id) REFERENCES books(id),
            FOREIGN KEY(member_id) REFERENCES members(id)
        )''')
        con.commit()

# --- Home/Login ---
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    current_time = datetime.now()
    return render_template('dashboard.html', timedelta=timedelta, now=current_time)





# --- Book Management ---
@app.route('/books')
def books():
    con = sqlite3.connect('library.db')
    books = con.execute("SELECT * FROM books").fetchall()
    return render_template('books.html', books=books)

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        
        # Save to database
        with sqlite3.connect('library.db') as con:
            cur = con.cursor()
            cur.execute("INSERT INTO books (title, author) VALUES (?, ?)", (title, author))
            con.commit()
        
        flash('Book added successfully.')
        return redirect(url_for('dashboard'))

    return render_template('add_book.html')


# --- Member Management ---
@app.route('/members')
def members():
    con = sqlite3.connect('library.db')
    members = con.execute("SELECT * FROM members").fetchall()
    return render_template('members.html', members=members)

@app.route('/add_member', methods=['GET', 'POST'])
def add_member():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        con = sqlite3.connect('library.db')
        con.execute("INSERT INTO members (name, email, phone) VALUES (?, ?, ?)",
                    (name, email, phone))
        con.commit()
        flash('Member added successfully!')
        return redirect(url_for('members'))
    return render_template('add_member.html')

# --- Issue Book ---
@app.route('/issue_book', methods=['GET', 'POST'])
def issue_book():
    con = sqlite3.connect('library.db')
    books = con.execute("SELECT * FROM books WHERE quantity > 0").fetchall()
    members = con.execute("SELECT * FROM members").fetchall()
    if request.method == 'POST':
        book_id = request.form['book_id']
        member_id = request.form['member_id']
        issue_date = datetime.now().strftime('%Y-%m-%d')
        return_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
        con.execute("INSERT INTO transactions (book_id, member_id, issue_date, return_date) VALUES (?, ?, ?, ?)",
                    (book_id, member_id, issue_date, return_date))
        con.execute("UPDATE books SET quantity = quantity - 1 WHERE id = ?", (book_id,))
        con.commit()
        flash('Book issued successfully!')
        return redirect(url_for('transactions'))
    return render_template('issue_book.html', books=books, members=members)

# --- Return Book ---
@app.route('/return_book/<int:transaction_id>')
def return_book(transaction_id):
    con = sqlite3.connect('library.db')
    transaction = con.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,)).fetchone()
    con.execute("UPDATE transactions SET returned = 1 WHERE id = ?", (transaction_id,))
    con.execute("UPDATE books SET quantity = quantity + 1 WHERE id = ?", (transaction[1],))
    con.commit()
    flash("Book returned successfully!")
    return redirect(url_for('transactions'))

# --- Transactions ---
@app.route('/transactions')
def transactions():
    con = sqlite3.connect('library.db')
    transactions = con.execute('''SELECT t.id, b.title, m.name, t.issue_date, t.return_date, t.returned
        FROM transactions t
        JOIN books b ON t.book_id = b.id
        JOIN members m ON t.member_id = m.id''').fetchall()
    return render_template('transactions.html', transactions=transactions)

# --- Reports ---
@app.route('/reports')
def reports():
    con = sqlite3.connect('library.db')
    today = datetime.now().strftime('%Y-%m-%d')
    daily = con.execute("SELECT COUNT(*) FROM transactions WHERE issue_date = ?", (today,)).fetchone()[0]
    weekly = con.execute("SELECT COUNT(*) FROM transactions WHERE issue_date >= date('now', '-7 days')").fetchone()[0]
    monthly = con.execute("SELECT COUNT(*) FROM transactions WHERE issue_date >= date('now', '-30 days')").fetchone()[0]
    return render_template('reports.html', daily=daily, weekly=weekly, monthly=monthly)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # You can handle registration form here
        username = request.form['username']
        password = request.form['password']
        # Save user (optional: add user table to DB)
        flash('User registered successfully!')
        return redirect(url_for('login'))
    return render_template('register.html')


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
