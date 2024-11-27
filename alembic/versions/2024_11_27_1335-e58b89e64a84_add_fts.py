"""
add-fts

Revision ID: e58b89e64a84
Revises: 41d1c8bf967c
Create Date: 2024-11-27 13:35:20.870817

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e58b89e64a84"
down_revision: str | None = "41d1c8bf967c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade."""
    op.execute(sa.text("CREATE VIRTUAL TABLE fts_book USING fts5(id unindexed, isbn unindexed, title, content='book')"))
    op.execute(
        sa.text("""\
CREATE TRIGGER book_ai AFTER INSERT ON book BEGIN
    INSERT INTO fts_book(rowid, id, isbn, title) VALUES (new.rowid, new.id, new.isbn, new.title);
END;
                       """)
    )
    op.execute(
        sa.text("""\
CREATE TRIGGER book_ad AFTER DELETE on book BEGIN
    INSERT INTO fts_book(fts_book, rowid, id, isbn, title) VALUES ('delete', old.rowid, old.id, old.isbn, old.title);
END;
                       """)
    )
    op.execute(
        sa.text("""\
CREATE TRIGGER book_au AFTER UPDATE ON book BEGIN
    INSERT INTO fts_book(fts_book, rowid, id, isbn, title) VALUES('delete', old.rowid, old.id, old.isbn, old.title);
    INSERT INTO fts_book(rowid, id, isbn, title) VALUES(new.rowid, new.id, new.isbn, new.title);
END;""")
    )

    op.execute(sa.text("CREATE VIRTUAL TABLE fts_author USING fts5(id unindexed, name, content='author')"))
    op.execute(
        sa.text("""\
CREATE TRIGGER author_ai AFTER INSERT ON author BEGIN
    INSERT INTO fts_author(rowid, id, name) VALUES (new.rowid, new.id, new.name);
END;
                       """)
    )
    op.execute(
        sa.text("""\
CREATE TRIGGER author_ad AFTER DELETE on author BEGIN
    INSERT INTO fts_author(fts_author, rowid, id, name) VALUES ('delete', old.rowid, id, old.name);
END;
                       """)
    )
    op.execute(
        sa.text("""\
CREATE TRIGGER author_au AFTER UPDATE ON author BEGIN
    INSERT INTO fts_author(fts_author, rowid, id, title) VALUES('delete', old.rowid, old.id, old.name);
    INSERT INTO fts_author(rowid, id, title) VALUES(new.rowid, new.id, new.name);
END;""")
    )


def downgrade() -> None:
    """Downgrade."""
    op.drop_table("fts_book_idx")
    op.drop_table("fts_book_config")
    op.drop_table("fts_book_docsize")
    op.drop_table("fts_book")
    op.drop_table("fts_book_data")
    op.drop_table("fts_author_idx")
    op.drop_table("fts_author_config")
    op.drop_table("fts_author_docsize")
    op.drop_table("fts_author")
    op.drop_table("fts_author_data")
