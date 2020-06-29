"""This script is used for initial export
data from csv files to the App DB Tables. (Import this script and
run add_data_to_db() at python console after db upgrade)
Run this script after flask DB migration and upgrade.
"""

import csv
import os
from flask.cli import AppGroup

from models import db, Category, Meal
from config import current_path

data_cli = AppGroup('add_data')


def add_categories():
    """Export data from csv categories file
    to SQL DB table 'categories'.
    """
    with open(os.path.join(current_path, 'delivery_categories.csv'), newline='') as csv_file:
        categories = [cat for cat in csv.reader(csv_file)][1:]

        for uid, title in categories:
            new_category = Category(title=title)
            db.session.add(new_category)

    db.session.commit()


def add_meals():
    """Export data from csv items file
        to SQL DB table 'meals'.
        """
    with open(os.path.join(current_path, 'delivery_items.csv'), newline='') as csv_file:
        meals = [meal for meal in csv.reader(csv_file)][1:]

        for meal in meals:
            uid, title, price, description, picture, category_id = meal
            category_query = Category.query.get(int(category_id))
            new_meal = Meal(
                title=title, price=price, description=description,
                picture=picture, category=category_query
            )
            db.session.add(new_meal)

    db.session.commit()


@data_cli.command('data')
def add_data_to_db():
    add_categories()
    add_meals()


if __name__ == '__main__':
    add_data_to_db()
