from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask import session as login_session
import pyrebase


# save information needed to access firebase
config = {
  "apiKey": "AIzaSyA562lkynO-piJg82yGuVTQsaTIHHgYOR4",
  "authDomain": "meet-is-awesome.firebaseapp.com",
  "projectId": "meet-is-awesome",
  "storageBucket": "meet-is-awesome.appspot.com",
  "messagingSenderId": "64515992699",
  "appId": "1:64515992699:web:505e41b9d000f4415586de",
  "measurementId": "G-B8322H65HL",
  "databaseURL": "https://meet-is-awesome-default-rtdb.firebaseio.com/"
}



# start firebase authentication and database
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()



# start flask
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'super-secret-key'



# route for the default page
@app.route('/')
def index():
    return render_template('index.html')



# route for the sign-up page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # get information from web form is a post request is made
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']  
        
        try: 
            # create user, log them in, and save username information to the database
            auth.create_user_with_email_and_password(email, password)
            login_session['user'] = auth.sign_in_with_email_and_password(email, password)
            uid = login_session['user']['localId']

            # sign in to authentication
            username_dict = {'username': username, 'email': email}
            db.child('Users').child(uid).set(username_dict)

            # redirect to home page if authentication is successful.
            return redirect(url_for('home'))
        
        # print out error
        except Exception as e:
            print(e)   

    # render the signup form by default, or if any error occurs.
    return render_template('signup.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try: 
            login_session['user'] = auth.sign_in_with_email_and_password(email, password)
            return redirect(url_for('home'))
        except Exception as e:
            print(e)   
    return render_template('login.html')



@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        login_session['user'] = None
        return redirect(url_for('index'))
    
    # render the signup form by default for a get request if user is logged in.
    try:
        uid = login_session['user']['localId']
        username = db.child('Users').child(uid).get().val()['username']
        return render_template('home.html', username = username)
    
    # if error occurs (due to not loggin in, for example), go back to login page.
    except Exception as e:
        print(e) 
        return redirect(url_for('login'))



@app.route('/play', methods=['GET', 'POST'])
def play():
    try:
        uid = login_session['user']['localId']
        username = db.child('Users').child(uid).get().val()['username']
    
     # if error occurs (due to not loggin in, for example), go back to login page.
    except Exception as e:
        print(e) 
        return redirect(url_for('login'))
    
    # the html makes a post request containing all the times for clicking the circles. 
    # when this request is made, transform the times from a string to a list of floats. 
    # processes the itmes, and redirects to the results page
    if request.method == 'POST':
        times = request.form['jsvar']
        times = [float(time) for time in times.split(',')]

        # retrieve any existing times for the user. Add the current time to the list.
        # save update the best time for the user if needed.
        existing_times = db.child('Users').child(uid).child('Times').get().val()
        if existing_times:
            times = existing_times['all_times'] + times
            all_times = {'all_times': times}
            db.child('Users').child(uid).child('Times').update(all_times)
            db.child('Users').child(uid).child('best_time').update({'best_time': min(times)})
        else:
            all_times = {'all_times': times}
            db.child('Users').child(uid).child('Times').set(all_times)
            db.child('Users').child(uid).child('best_time').set({'best_time': min(times)})

        return redirect(url_for('results'))
    
    # render game by default
    return render_template('play.html')



@app.route('/results')
def results():
    try:
        uid = login_session['user']['localId']
        username = db.child('Users').child(uid).get().val()['username']
        user_times = db.child('Users').child(uid).child('Times').get().val()['all_times']
    
     # if error occurs (due to not loggin in, for example), go back to login page.
    except Exception as e:
        print(e) 
        return redirect(url_for('login'))

    # calculte values and pass to template.
    last_round = sum(user_times[-5:])
    last_round_avg = last_round/5
    avg_time = sum(user_times) / len(user_times)
    best_time = min(user_times)
    return render_template('results.html', 
                           username = username, last_round = last_round, last_round_avg = last_round_avg,
                           avg_time = avg_time, best_time = best_time)



@app.route('/leaderboard')
def leaderboard():
    try:
        uid = login_session['user']['localId']
        username = db.child('Users').child(uid).get().val()['username']
        time_to_username = []

        # build a leaderboard by looping through all users. skip the ones who has no best time 
        # (maybe they only made an account). save this data into a tuple of (reaction_time, username) 
        # to enable sort by time.
        # TO-DO: maintain a seperate leaderboard part of the database for efficiency
        for test_uid in db.child('Users').get().val():
            best_time_dict = db.child('Users').child(test_uid).child('best_time').get().val()
            if not best_time_dict:
                continue
            react_time = best_time_dict['best_time']
            test_user = db.child('Users').child(test_uid).get().val()['username']
            time_to_username.append((react_time, test_user))
        
        # transform leaderboard to be tuples of (rank, username, time)
        leaderboard = [(index + 1, user, time) for index, (time, user) in enumerate(sorted(time_to_username))]

    # if error occurs (due to not loggin in, for example), go back to login page.
    except Exception as e:
        print(e) 
        return redirect(url_for('login'))

    # pull out the info about the current user from the leaderboard
    my_info = [tup for tup in leaderboard if username in tup]
    if my_info:
        my_info = my_info[0]
        if my_info[0]<= 5:
            my_info = False
    else:
        my_info = False
    
    return render_template('leaderboard.html', username = username, leaderboard = leaderboard[:5], my_info = my_info)



if __name__ == '__main__':
    app.run(debug=True)
    
