import locale
from functools import wraps
from collections import Counter

from flask import Flask, render_template, redirect, session, flash
from flask_migrate import Migrate

from models import db, Category, Meal, User, Order
from forms import OrderForm, RegistrationForm, LoginForm


app = Flask(__name__)
app.secret_key = 'randomstring'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)
# set language for datetime object
locale.setlocale(locale.LC_ALL, 'ru_RU')


# Декоратор авторизации
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print('login_required')
        if not session.get('user'):
            return redirect('/login/')
        return f(*args, **kwargs)
    return decorated_function

# TODO: try to add routes where nav_bar is used
def cart_info():
    cart = session.get('cart', [])
    meals = [Meal.query.filter_by(id=pos).first() for pos in cart]
    unique_meals = Counter(meals)
    total_price = sum([meal.price for meal in meals])
    return cart, unique_meals, total_price


@app.route('/')
def main():
    current_user = session.get('user')
    print(current_user)
    cart, _, total_price = cart_info()
    categories_query = Category.query.all()
    categories = [cat for cat in categories_query]

    return render_template('main.html', categories=categories, meals_count=len(cart), total_price=total_price)


@app.route('/addtocart/<int:meal_id>')
def add_to_cart(meal_id):
    cart = session.get('cart', [])
    cart.append(meal_id)
    session['cart'] = cart
    if session.get('del_banner'):
        session['del_banner'] = False
    return redirect('/cart/')


@app.route('/delete/')
def delete_meal():
    cart = session.get('cart')
    cart.pop()
    session['cart'] = cart
    session['del_banner'] = True
    return redirect('/cart/')


@app.route('/cart/', methods=['GET', 'POST'])
def cart_page():
    cart, unique_meals, total_price = cart_info()

    form = OrderForm()
    if session.get('user'):
        form.mail.data = session['user']['mail']
    if form.validate_on_submit():
        user = User.query.filter_by(mail=form.mail.data).first()

        order = Order(name=form.name.data, address=form.address.data,
                      phone=form.phone.data, total_cost=total_price)
        order.status = 'Done'
        order.user = user
        order.meals = [Meal.query.filter_by(id=pos).first() for pos in cart]
        if not cart:
            flash('В корзине пусто. Выберите блюдо для заказа.')
            return redirect('/')
        db.session.add(order)
        db.session.commit()

        # delete session cart for user after order
        if cart:
            session.pop('cart')
        return redirect('/ordered/')

    return render_template('cart.html', form=form, meals=unique_meals, meals_count=len(cart), total_price=total_price)


@app.route('/account/')
@login_required
def account():
    cart, unique_meals, total_price = cart_info()
    mail = session.get('user')['mail']
    user = User.query.filter_by(mail=mail).first()
    client_orders = {}
    orders = Order.query.filter_by(user=user).order_by(Order.date_created.desc()).all()
    for order in orders:
        client_orders[order.id] = []
        client_orders[order.id].append(Counter(order.meals))
        client_orders[order.id].append(order.total_cost)
        client_orders[order.id].append(order.date_created.strftime('%-d %B'))

    return render_template('account.html', meals_count=len(cart),
                           total_price=total_price, orders=client_orders)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(mail=form.mail.data).first()
        if user and user.password_valid(form.password.data):
            session['user'] = {'id': user.id,
                               'mail': user.mail
                               }
            flash('Рады видеть Вас снова!')
            return redirect('/account/')
        elif not user:
            # TODO: Add errors instead flash
            flash('Такого пользователя не существует. Проверьте почту или зарегистрируйтесь!')
            return render_template('login.html', form=form)
        # TODO: Delete
        '''Delete code
        elif not user:
            flash('Такого пользователя не существует. Зарегистрируйтесь!')
            return redirect('/register/')'''

    return render_template('login.html', form=form)


@app.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User()
        user.mail = form.mail.data
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        session['user'] = {'id': user.id,
                           'mail': user.mail
                           }
        flash(f'Пользователь: {form.mail.data} с паролем: {form.password.data} зарегистрирован')
        return redirect('/')
    return render_template('register.html', form=form)


@app.route('/logout/')
def logout():
    session.clear()
    return redirect('/')


@app.route('/ordered/')
def ordered():
    return render_template('ordered.html')


if __name__ == '__main__':
    app.run(debug=True, port=8080)
