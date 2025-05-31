"""Add password reset fields

Revision ID: password_reset_001
Revises: 738847637a24
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'password_reset_001'
down_revision = '738847637a24'
branch_labels = None
depends_on = None

def upgrade():
    # Add reset token and expiry columns to users table
    op.add_column('users', sa.Column('reset_token', sa.String(), nullable=True))
    op.add_column('users', sa.Column('reset_token_expires', sa.DateTime(timezone=True), nullable=True))

def downgrade():
    # Remove the columns
    op.drop_column('users', 'reset_token_expires')
    op.drop_column('users', 'reset_token')
