#source: https://www.section.io/engineering-education/user-login-web-system/

#creating a new user from form
@app.route('/new-user')
def create_user():
    username_new = ""
    password_new = sha256_crypt.encrypt("")
    email_new = ""
    first_name_new = ""
    last_name_new = ""

    cur = g.conn.cursor()
    try:
        cur.execute('INSERT INTO Users (username, first_name, last_name, email, passwor) VALUES (%s, %s, %s)', (username_new, first_name_new, last_name_new, email_new, password_new))
    except:
        print("database entry failed")
    g.conn.commit()
    cur.close()

    return "Account created"

#logging in
@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('index.html')

@app.route('/login', methods=['POST'])
def user_login():
    login = request.form

    username = login['username']
    password = login['password']

    cur = g.conn.cursor(buffered=True)
    data = cur.execute('SELECT * FROM Login WHERE username=%s', (username))
    data = cur.fetchone()[2]

    if sha256_crypt.verify(password, data):
        account = True

    if account:
        session['logged_in'] = True
    else:
       flash('wrong password!')

    return home()

@app.route('logout')
def logout():
    session['logged_in'] = False
    return home()
