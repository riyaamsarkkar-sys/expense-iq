from flask import Flask, render_template, request,redirect,session
from datetime import date, datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import extract,func,create_engine
from calendar import monthrange
from werkzeug.security import generate_password_hash, check_password_hash
import os



starting = Flask(__name__)
starting.secret_key = "mysecretkey123"

basedir = os.path.abspath(os.path.dirname(__file__))

starting.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'sqlite:///' + os.path.join(basedir, 'practice1.db')
)

print("Base dir:", basedir)

starting.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300
}

db = SQLAlchemy(starting)





class Prac(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(200), nullable=False)
    Category = db.Column(db.String(200), nullable=False)
    Amount = db.Column(db.Integer, nullable=False)
    Description = db.Column(db.String(200), nullable=False)
    

    expense_date = db.Column(
        db.Date,
        nullable=False,
        default=date.today)
    

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False)






class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)



with starting.app_context():
    db.create_all()





###this the login page of the file###

@starting.route('/', methods=['GET', 'POST'])
def login():
    


    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(
            username=username
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):
            session['user_id'] = user.id
            return redirect('/dashboard')

        return "Invalid Username or Password"

    return render_template('login.html')



### new user signup ###

@starting.route('/signup', methods=['GET', 'POST'])
def signup():



    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            return "Username already exists"

        existing_email = User.query.filter_by(email=email).first()

        if existing_email:
            return "Email already registered"

        user = User(
            username=username,
            email=email,
           
            password=generate_password_hash(password)

        )

        db.session.add(user)
        db.session.commit()

        return redirect('/')

    return render_template('signup.html')




### dashboard ###
from collections import defaultdict

@starting.route('/dashboard')
def dashboard():

    if 'user_id' not in session:
        return redirect('/')

    expenses = Prac.query.filter_by(
        user_id=session['user_id']
    ).all()

    lifetime_spent = sum(exp.Amount for exp in expenses)

    total_transactions = len(expenses)

    monthly_totals = defaultdict(int)

    for exp in expenses:

        month_key = exp.expense_date.strftime("%Y-%m")

        monthly_totals[month_key] += exp.Amount


    highest_month_spend = 0
    highest_month_name = "N/A"

    if monthly_totals:

        highest_key = max(
            monthly_totals,
            key=monthly_totals.get
        )

        highest_month_spend = monthly_totals[highest_key]

        highest_month_name = datetime.strptime(
            highest_key,
            "%Y-%m"
        ).strftime("%B %Y")
    user = User.query.get(session['user_id'])
    return render_template(
        'dashboard.html',
        lifetime_spent=lifetime_spent,
        total_transactions=total_transactions,
        highest_month_spend=highest_month_spend,
        highest_month_name=highest_month_name,
        username=user.username
    )





###this is for the data entry part of the project###
@starting.route('/data_entry', methods=['GET', 'POST'])
def hello():

    if 'user_id' not in session:
        return redirect('/')

    today = datetime.today()
    if request.method == 'POST':

        title = request.form['Title']
        category = request.form['Category']
        amount = request.form['Amount']
        description = request.form['Description']
        
    
        prac = Prac(
            Title=title,
            Category=category,
            Amount=amount,
            Description=description,
            user_id=session['user_id']
        )
       

        db.session.add(prac)
        db.session.commit()

        return redirect('/data_entry')

    total_expense = db.session.query(
        db.func.sum(Prac.Amount)
    ).filter(
        Prac.user_id == session['user_id'],
        db.extract('month', Prac.expense_date) == today.month,
        db.extract('year', Prac.expense_date) == today.year

    ).scalar() or 0

    total_entries = Prac.query.filter(
        Prac.user_id == session['user_id'],
        db.extract('month', Prac.expense_date) == today.month,
        db.extract('year', Prac.expense_date) == today.year
    ).count()
         
    filter_type = request.args.get("filter", "all")
    selected_date = request.args.get("selected_date")

    query = Prac.query.filter_by(
        user_id=session['user_id']
    )

    

    if filter_type == "date" and selected_date:

        query = query.filter(
        Prac.expense_date == selected_date
    )


    elif filter_type == "this_month":
    
        query = query.filter(
        db.extract('month', Prac.expense_date) == today.month,
db.extract('year', Prac.expense_date) == today.year
    )

    elif filter_type == "last_month":

        month = today.month - 1
        year = today.year

        if month == 0:
            month = 12
            year -= 1

        query = query.filter(
            db.extract('month', Prac.expense_date) == month,
            db.extract('year', Prac.expense_date) == year
        )

    expenses = Prac.query.filter_by(
    user_id=session['user_id']
     ).order_by(
    Prac.expense_date.desc(),
    Prac.sno.desc()
    ).limit(10).all()

    return render_template(
        'data_entry.html',
        total_expense=total_expense,
        total_entries=total_entries,
        expenses=expenses
)





     


###logout###
@starting.route('/logout')
def logout():

    if 'user_id' not in session:
        return redirect('/')
    session.clear()
    return redirect('/')






###curent month spent analysis###
@starting.route('/current_month')
def current_month():

    if 'user_id' not in session:
        return redirect('/')

    today = datetime.today()

    selected_date = request.args.get("selected_date")

    current_month_name = today.strftime("%B %Y")

    # Base query: current month only
    query = Prac.query.filter(
        Prac.user_id == session['user_id'],
        db.extract('month', Prac.expense_date) == today.month,
        db.extract('year', Prac.expense_date) == today.year
    )

    # Additional date filter (inside current month)
    if selected_date:

        filter_date = datetime.strptime(
            selected_date,
            "%Y-%m-%d"
        ).date()

        query = query.filter(
            Prac.expense_date == filter_date
        )

    expenses = query.order_by(
        Prac.expense_date.desc(),
        Prac.sno.desc()
    ).all()

    total_expense = sum(exp.Amount for exp in expenses)

    total_entries = len(expenses)

    avg_per_day = (
        round(total_expense / today.day)
        if total_entries > 0 else 0
    )

    categories = [
        'Food',
        'Travel',
        'Entertainment',
        'Shopping',
        'Education',
        'Bills',
        'Other'
    ]

    chart_data = [
        sum(
            exp.Amount
            for exp in expenses
            if exp.Category == cat
        )
        for cat in categories
    ]

    return render_template(
        "current_month.html",
        expenses=expenses,
        month_name=current_month_name,
        categories=categories,
        chart_data=chart_data,
        total_expense=total_expense,
        total_entries=total_entries,
        avg_per_day=avg_per_day,
        selected_date=selected_date
    )







###spending history###
@starting.route('/spending_history')
def spending_history():

    if 'user_id' not in session:
        return redirect('/')

    month = request.args.get('month', 'all')

    year = request.args.get(
        'year',
        str(datetime.now().year)
    )

    selected_date = request.args.get(
        'selected_date'
    )

    query = Prac.query.filter_by(
        user_id=session['user_id']
    )

    # YEAR FILTER

    query = query.filter(
        extract(
            'year',
            Prac.expense_date
        ) == int(year)
    )

    # MONTH FILTER

    if month != "all":

        query = query.filter(
            extract(
                'month',
                Prac.expense_date
            ) == int(month)
        )

    # DATE FILTER

    if selected_date:

        selected_date = datetime.strptime(
            selected_date,
            "%Y-%m-%d"
        ).date()

        query = query.filter(
            Prac.expense_date == selected_date
        )

    # TABLE DATA

    expenses = query.order_by(
        Prac.expense_date.desc(),
        Prac.sno.desc()
    ).all()



    # AVAILABLE DATES FOR DATE DROPDOWN

    available_dates = db.session.query(
        Prac.expense_date
    ).filter_by(
        user_id=session['user_id']
    )

    if month != "all":

        available_dates = available_dates.filter(
            extract(
                'month',
                Prac.expense_date
            ) == int(month)
        )

    available_dates = available_dates.filter(
        extract(
            'year',
            Prac.expense_date
        ) == int(year)
    )

    available_dates = available_dates.distinct().order_by(
        Prac.expense_date.desc()
    ).all()

    # TOTALS

    total_transactions = len(expenses)

    total_spent = sum(
        expense.Amount
        for expense in expenses
    )

    # HIGHEST EXPENSE

    highest_expense = None

    if expenses:

        highest_expense = max(
            expenses,
            key=lambda x: x.Amount
        )

    # TOP CATEGORY
    category_query = db.session.query(
        Prac.Category,
        func.sum(Prac.Amount)
    ).filter_by(
        user_id=session['user_id']
    )

    category_query = category_query.filter(
        extract(
            'year',
            Prac.expense_date
        ) == int(year)
    )

    if month != "all":
        category_query = category_query.filter(
            extract(
                'month',
                Prac.expense_date
            ) == int(month)
        )

    if selected_date:
        category_query = category_query.filter(
            Prac.expense_date == selected_date
        )

    top_category = category_query.group_by(
        Prac.Category
    ).order_by(
        func.sum(Prac.Amount).desc()
    ).first()

    

    trend_scope = request.args.get(
    'trend_scope',
    'lifetime'
    )

    # AVERAGE DAILY SPEND

    average_daily_spend = 0

    average_daily_spend = 0

    if month != "all":

        days_in_month = monthrange(
            int(year),
            int(month)
        )[1]

        average_daily_spend = round(
            total_spent / days_in_month,
            2
        )

    # MONTHLY TREND DATA

    trend_query = db.session.query(

    extract(
        'month',
        Prac.expense_date
    ),

    func.sum(
        Prac.Amount
    )

    ).filter_by(
        user_id=session['user_id']
    )

    if trend_scope != "lifetime":

        trend_query = trend_query.filter(
            extract(
            'year',
            Prac.expense_date
        ) == int(trend_scope)
    )

    monthly_data = trend_query.group_by(
    extract(
        'month',
        Prac.expense_date
    )
    ).all()
      # PIE CHART DATA

    category_query = db.session.query(

        Prac.Category,

        func.sum(
            Prac.Amount
        ).label('total')

    ).filter_by(
        user_id=session['user_id']
    )

# YEAR FILTER

    category_query = category_query.filter(
        extract(
            'year',
            Prac.expense_date
        ) == int(year)
    )

# MONTH FILTER

    if month != "all":

        category_query = category_query.filter(
        extract(
            'month',
            Prac.expense_date
        ) == int(month)
    )

# DATE FILTER

    if selected_date:

        category_query = category_query.filter(
            Prac.expense_date == selected_date
    )

    category_data = category_query.group_by(
        Prac.Category
    ).all()
    # HIGHEST / LOWEST MONTH

    month_summary = db.session.query(

        extract(
            'month',
            Prac.expense_date
        ),

        func.sum(
            Prac.Amount
        )

    ).filter_by(
        user_id=session['user_id']
    ).group_by(
        extract(
            'month',
            Prac.expense_date
        )
    ).all()

    highest_month = None
    lowest_month = None

    if month_summary:

        highest_month = max(
            month_summary,
            key=lambda x: x[1]
        )

        lowest_month = min(
            month_summary,
            key=lambda x: x[1]
        )

    monthly_labels = [
    datetime(2000, int(month_num), 1).strftime("%b")
    for month_num, total in monthly_data
    ]

    monthly_values = [
        float(total)
        for month_num, total in monthly_data
    ]


    if category_data:

        category_labels = [
        category
        for category, total in category_data
        ]

        category_values = [
           float(total)
           for category, total in category_data
    ]

    else:

       category_labels = ["No Data"]

       category_values = [1]
    
    month_names = {
    1:"January",
    2:"February",
    3:"March",
    4:"April",
    5:"May",
    6:"June",
    7:"July",
    8:"August",
    9:"September",
    10:"October",
    11:"November",
    12:"December"
}

    highest_month_name = None
    lowest_month_name = None

    if highest_month:
        highest_month_name = month_names[int(highest_month[0])]

    if lowest_month:
        lowest_month_name = month_names[int(lowest_month[0])]
    
    
    return render_template(

        "spending_history.html",

        expenses=expenses,

        month=month,
        year=year,
        selected_date=selected_date,
        available_dates=available_dates,

        total_transactions=total_transactions,
        total_spent=total_spent,

        highest_expense=highest_expense,

        top_category=top_category,

        average_daily_spend=average_daily_spend,

        monthly_data=monthly_data,
        trend_scope=trend_scope,

        category_data=category_data,

        highest_month=highest_month,

        lowest_month=lowest_month,

        monthly_labels=monthly_labels,
        monthly_values=monthly_values,

        category_labels=category_labels,
        category_values=category_values,

        highest_month_name=highest_month_name,
        lowest_month_name=lowest_month_name

    )


if __name__ == "__main__":
    starting.run(debug=False,host='0.0.0.0')
    