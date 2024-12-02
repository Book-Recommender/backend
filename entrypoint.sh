#!/bin/sh
python -m alembic upgrade head && python -m fastapi run src/openbook/server.py
