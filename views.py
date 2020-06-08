import locale
from collections import Counter
from functools import wraps
from random import sample

from flask import flash, render_template, redirect, session

from app import app, db
from models import Category, Meal, User, Order
from forms import OrderForm, RegistrationForm, LoginForm
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView

# set language for datetime object
locale.setlocale(locale.LC_ALL, 'ru_RU')


# Декоратор авторизации
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user'):
            return redirect('/login/')
        return f(*args, **kwargs)

    return decorated_function


def cart_info():
    """
    Function is used for compute data
    for render in nav_menu and 'cart.html'.
    """
    cart = session.get('cart', [])
    meals = [Meal.query.filter_by(id=pos).first() for pos in cart]
    unique_meals = Counter(meals)
    total_price = sum([meal.price for meal in meals])
    return cart, unique_meals, total_price


@app.route('/')
def main():
    # Get session cart and total_price for nav_menu
    cart, _, total_price = cart_info()

    # Get categories from DB
    categories_query = Category.query.all()
    # Create dictionary with 3 random meal from each category
    random_meals = {}
    for cat in categories_query:
        random_meals[cat.title] = sample(cat.meals, 3)

    return render_template('main.html', random_meals=random_meals,
                           meals_count=len(cart), total_price=total_price)


@app.route('/addtocart/<int:meal_id>')
def add_to_cart(meal_id):
    # Save user food choice in session
    cart = session.get('cart', [])
    cart.append(meal_id)
    session['cart'] = cart
    # If user previously delete position from cart, change state for banner
    if session.get('del_banner'):
        session['del_banner'] = False
    return redirect('/cart/')


@app.route('/delete/')
def delete_meal():
    cart = session.get('cart')
    cart.pop()
    session['cart'] = cart
    # This is used to display 'delete' banner at 'cart.html'
    session['del_banner'] = True
    return redirect('/cart/')


@app.route('/cart/', methods=['GET', 'POST'])
def cart_page():
    # Get session based user data
    cart, unique_meals, total_price = cart_info()

    form = OrderForm()
    # Insert user mail in form if user is logged in
    if session.get('user'):
        form.mail.data = session['user']['mail']
    if form.validate_on_submit():
        # Get user from DB
        user = User.query.filter_by(mail=form.mail.data).first()
        # Create order for user
        order = Order(name=form.name.data, address=form.address.data,
                      phone=form.phone.data, total_cost=total_price)
        order.status = 'Done'
        order.user = user
        order.meals = [Meal.query.filter_by(id=pos).first() for pos in cart]
        # If cart is empty - don't create empty order in DB
        if not cart:
            flash('В корзине пусто. Выберите блюдо для заказа.')
            return redirect('/')
        # If cart is not empty - create order for user in DB
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
    cart, _, total_price = cart_info()
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
            form.mail.errors.append('Такого пользователя не существует. Проверьте введенную почту.')
        else:
            form.password.errors.append('Неверный пароль.')

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


# Hide Admin panel from unauthorized users
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        if not session.get('user'):
            return False
        return True


class MyUserView(ModelView):
    column_exclude_list = ['password_hash']
    column_searchable_list = ['mail']

    can_create = True
    can_edit = False
    can_delete = True

    def is_accessible(self):
        if not session.get('user'):
            return False
        return True


class MyCategoryView(ModelView):
    def is_accessible(self):
        if not session.get('user'):
            return False
        return True


class MyMealView(ModelView):
    def is_accessible(self):
        if not session.get('user'):
            return False
        return True


class MyOrderView(ModelView):
    def is_accessible(self):
        if not session.get('user'):
            return False
        return True


admin = Admin(app, index_view=MyAdminIndexView())
admin.add_view(MyUserView(User, db.session))
admin.add_view(MyCategoryView(Category, db.session))
admin.add_view(MyMealView(Meal, db.session))
admin.add_view(MyOrderView(Order, db.session))
