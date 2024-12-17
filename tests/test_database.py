import pytest
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import text

def test_create_language(test_session: Session):
    query = text("""
        INSERT INTO languages (code, name, region)
        VALUES (:code, :name, :region)
        RETURNING id, code, name
    """)
    result = test_session.execute(query, {
        'code': 'xho',
        'name': 'isiXhosa',
        'region': 'South Africa'
    })
    test_session.commit()
    language = result.fetchone()
    assert language is not None
    assert language.code == 'xho'

def test_create_term(test_session: Session):
    # First create a language
    lang_query = text("""
        INSERT INTO languages (code, name, region)
        VALUES (:code, :name, :region)
        RETURNING id
    """)
    lang_result = test_session.execute(lang_query, {
        'code': 'xho',
        'name': 'isiXhosa',
        'region': 'South Africa'
    })
    language_id = lang_result.fetchone().id

    # Create object
    obj_query = text("""
        INSERT INTO objects (label, category)
        VALUES (:label, :category)
        RETURNING id
    """)
    obj_result = test_session.execute(obj_query, {
        'label': 'tree',
        'category': 'nature'
    })
    object_id = obj_result.fetchone().id

    # Create term
    term_query = text("""
        INSERT INTO indigenous_terms 
        (language_id, object_id, term, pronunciation)
        VALUES (:language_id, :object_id, :term, :pronunciation)
        RETURNING id, term
    """)
    result = test_session.execute(term_query, {
        'language_id': language_id,
        'object_id': object_id,
        'term': 'umthi',
        'pronunciation': 'um-thi'
    })
    test_session.commit()
    term = result.fetchone()
    assert term is not None
    assert term.term == 'umthi'