

import pytest

from osp.citations.models import Text_Index

from .utils import score


pytestmark = pytest.mark.usefixtures('db', 'es')


def test_join_citation_count(add_text, add_citation):

    """
    Text_Index.rank_texts() should join the citation count for each text.
    """

    t1 = add_text()
    t2 = add_text()
    t3 = add_text()

    for i in range(3):
        add_citation(t1)

    for i in range(2):
        add_citation(t2)

    for i in range(1):
        add_citation(t3)

    texts = Text_Index.rank_texts()

    assert texts[0]['text'] == t1
    assert texts[0]['text'].count == 3

    assert texts[1]['text'] == t2
    assert texts[1]['text'].count == 2

    assert texts[2]['text'] == t3
    assert texts[2]['text'].count == 1


def test_compute_metrics(add_text, add_citation):

    """
    Zip ranks and scores with the texts.
    """

    t1 = add_text()

    t2 = add_text()
    t3 = add_text()

    t4 = add_text()
    t5 = add_text()
    t6 = add_text()

    for i in range(9):
        add_citation(text=t1)

    for i in range(3):
        add_citation(text=t2)
        add_citation(text=t3)

    for i in range(1):
        add_citation(text=t4)
        add_citation(text=t5)
        add_citation(text=t6)

    texts = Text_Index.rank_texts()

    assert texts == [

        dict(text=t1, rank=1, score=3/3),

        dict(text=t2, rank=2, score=2/3),
        dict(text=t3, rank=2, score=2/3),

        dict(text=t4, rank=4, score=1/3),
        dict(text=t5, rank=4, score=1/3),
        dict(text=t6, rank=4, score=1/3),

    ]


def test_only_consider_valid_texts(add_text, add_citation):

    """
    Only rank texts that have passed validation.
    """

    t1 = add_text(valid=None)
    t2 = add_text(valid=False)
    t3 = add_text(valid=True)

    add_citation(text=t1)
    add_citation(text=t2)
    add_citation(text=t3)

    texts = Text_Index.rank_texts()

    assert texts == [
        dict(text=t3, rank=1, score=1),
    ]


def test_only_consider_displayed_texts(add_text, add_citation):

    """
    Only rank texts that have been marked for display.
    """

    t1 = add_text(display=None)
    t2 = add_text(display=False)
    t3 = add_text(display=True)

    add_citation(text=t1)
    add_citation(text=t2)
    add_citation(text=t3)

    texts = Text_Index.rank_texts()

    assert texts == [
        dict(text=t3, rank=1, score=1),
    ]


def test_skip_uncited_texts(add_text, add_citation):

    """
    Texts without any citations should be excluded.
    """

    t1 = add_text()
    t2 = add_text()

    add_citation(text=t1)

    texts = Text_Index.rank_texts()

    assert texts == [
        dict(text=t1, rank=1, score=1),
        # Exclude t2.
    ]
