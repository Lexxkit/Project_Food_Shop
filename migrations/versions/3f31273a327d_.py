"""empty message

Revision ID: 3f31273a327d
Revises: 
Create Date: 2020-06-02 11:45:34.353411

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3f31273a327d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=16), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('title')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('mail', sa.String(length=128), nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('mail')
    )
    op.create_table('meals',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=32), nullable=False),
    sa.Column('price', sa.Numeric(precision=6, scale=2), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('picture', sa.String(length=32), nullable=True),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('title')
    )
    op.create_table('orders',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date_created', sa.Date(), nullable=True),
    sa.Column('total_cost', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('status', sa.String(length=16), nullable=False),
    sa.Column('name', sa.String(length=32), nullable=False),
    sa.Column('phone', sa.String(length=32), nullable=False),
    sa.Column('address', sa.Text(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('orders_meals',
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.Column('meal_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['meal_id'], ['meals.id'], ),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('orders_meals')
    op.drop_table('orders')
    op.drop_table('meals')
    op.drop_table('users')
    op.drop_table('categories')
    # ### end Alembic commands ###
