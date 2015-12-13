

import pytest

from osp.citations.models import Text


def test_set_corpus(models, mock_jstor):

    mock_jstor.add_article()
    Text.ingest_jstor()

    assert Text.select().first().corpus == 'jstor'


def test_set_identifier(models, mock_jstor):

    mock_jstor.add_article(article_id='001')
    Text.ingest_jstor()

    assert Text.select().first().identifier == '001'


def test_set_title(models, mock_jstor):

    mock_jstor.add_article(article_title='Article Title')
    Text.ingest_jstor()

    assert Text.select().first().title == 'Article Title'


def test_set_single_author(models, mock_jstor):

    mock_jstor.add_article(author=[('David W.', 'McClure')])
    Text.ingest_jstor()

    assert Text.select().first().author == ['David W. McClure']


def test_set_multiple_authors(models, mock_jstor):

    mock_jstor.add_article(author=[
        ('David W.', 'McClure'),
        ('Kara G.', 'Weisman'),
    ])

    Text.ingest_jstor()

    assert Text.select().first().author == [
        'David W. McClure',
        'Kara G. Weisman',
    ]


def test_set_publisher(models, mock_jstor):

    mock_jstor.add_article(publisher_name='Chicago Journals')
    Text.ingest_jstor()

    assert Text.select().first().publisher == 'Chicago Journals'


def test_set_date(models, mock_jstor):

    mock_jstor.add_article(pub_year=1987, pub_month=6, pub_day=25)
    Text.ingest_jstor()

    assert Text.select().first().date == '1987-06-25'