

import pytest

from osp.corpus.models.document import Document
from osp.corpus.jobs.ext_text import ext_text
from osp.dates.models.semester import Document_Date_Semester
from osp.dates.jobs.ext_semester import ext_semester


def test_link_with_document(models, mock_corpus):

    """
    If a semester marker is found, the metadata row should be linked with the
    document with the id that was passed to the job.
    """

    # 2 files.
    path1 = mock_corpus.add_file(content='')
    path2 = mock_corpus.add_file(content='Fall 2013')

    # 2 document rows.
    doc1 = Document.create(path=path1)
    doc2 = Document.create(path=path2)

    # Extract text for both documents.
    text1 = ext_text(doc1.id) # Won't write text.
    text2 = ext_text(doc2.id) # Will write text.

    # Since the first document has no text content, a text metadata row won't
    # get written, meaning that the ids in the `document` table will no longer
    # match up with the ids of the corresponding rows in `document_text`.

    assert text1 == None
    assert text2.id == 1
    assert text2.document.id == 2

    row = ext_semester(doc2.id)
    assert row.document == doc2


@pytest.fixture()
def ext(models, mock_corpus):

    """
    Returns:
        function: A helper that creates document / text rows, runs the job,
        and returns the new `document_date_semester` row.
    """

    def _ext(content):

        # Create a document.
        path = mock_corpus.add_file(content=content)
        document = Document.create(path=path)

        # Extract text, then date.
        ext_text(document.id)
        ext_semester(document.id)

        # Pop out the new row.
        return (
            Document_Date_Semester
            .select()
            .where(Document_Date_Semester.document==document)
            .first()
        )

    return _ext


def test_fall_semester(ext):

    """
    Fall 2012
    """

    row = ext('abc Fall 2012 def')

    assert row.offset == 4
    assert row.semester == 'Fall'
    assert row.year == '2012'


def test_winter_semester(ext):

    """
    Winter 2012
    """

    row = ext('abc Winter 2012 def')

    assert row.offset == 4
    assert row.semester == 'Winter'
    assert row.year == '2012'


def test_spring_semester(ext):

    """
    Spring 2012
    """

    row = ext('abc Spring 2012 def')

    assert row.offset == 4
    assert row.semester == 'Spring'
    assert row.year == '2012'


def test_summer_semester(ext):

    """
    Summer 2012
    """

    row = ext('abc Summer 2012 def')

    assert row.offset == 4
    assert row.semester == 'Summer'
    assert row.year == '2012'


def test_ignore_case(ext):

    """
    The case of the semester should be ignored.
    """

    cases = [
        'Summer',
        'SUMMER',
        'summer',
        'SuMmEr',
    ]

    for semester in cases:

        row = ext('abc %s 2012 def' % semester)

        assert row.offset == 4
        assert row.semester == semester
        assert row.year == '2012'


def test_two_digit_year(ext):

    """
    Fall 12
    """

    row = ext('abc Fall 12 def')

    assert row.offset == 4
    assert row.semester == 'Fall'
    assert row.year == '12'


def test_apostrophe_before_year(ext):

    """
    Fall '12
    """

    row = ext("abc Fall '12 def")

    assert row.offset == 4
    assert row.semester == 'Fall'
    assert row.year == '12'


def test_ignore_future_years(ext):

    """
    Fall 3000
    """

    row = ext("abc Fall 3000 def")
    assert row == None


def test_ignore_old_years(ext):

    """
    Fall 1979
    """

    row = ext("abc Fall 1979 def")
    assert row == None
