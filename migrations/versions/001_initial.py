"""Initial migration

Revision ID: 001
Create Date: 2024-12-18
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Languages table
    op.create_table(
        'languages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=10), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('region', sa.String(length=100)),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )

    # Objects table
    op.create_table(
        'objects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('label', sa.String(length=100), nullable=False),
        sa.Column('category', sa.String(length=50)),
        sa.Column('description', sa.Text()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('label')
    )

    # Indigenous terms table
    op.create_table(
        'indigenous_terms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('language_id', sa.Integer(), nullable=False),
        sa.Column('object_id', sa.Integer(), nullable=False),
        sa.Column('term', sa.String(length=100), nullable=False),
        sa.Column('pronunciation', sa.String(length=100)),
        sa.Column('context', sa.Text()),
        sa.Column('source', sa.String(length=200)),
        sa.Column('verified', sa.Boolean(), server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['language_id'], ['languages.id']),
        sa.ForeignKeyConstraint(['object_id'], ['objects.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('language_id', 'object_id', 'term')
    )

    # Captured images table
    op.create_table(
        'captured_images',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('captured_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('processed', sa.Boolean(), server_default=sa.text('false')),
        sa.Column('metadata', sa.JSON()),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('idx_terms_language', 'indigenous_terms', ['language_id'])
    op.create_index('idx_terms_object', 'indigenous_terms', ['object_id'])

def downgrade():
    op.drop_index('idx_terms_object')
    op.drop_index('idx_terms_language')
    op.drop_table('captured_images')
    op.drop_table('indigenous_terms')
    op.drop_table('objects')
    op.drop_table('languages')