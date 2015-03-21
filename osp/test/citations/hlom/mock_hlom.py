

import os
import tempfile
import shutil

from osp.citations.hlom.models.record import HLOM_Record
from contextlib import contextmanager
from pymarc import Record, Field, MARCWriter


def get_hlom(number, title, author):

    """
    Insert a HLOM record row.

    Args:
        number (str): The control number.
        title (str): The title.
        author (str): The author.

    Returns:
        HLOM_Record
    """

    marc = MockMARC()
    marc.set_control_number(number)
    marc.set_title(title)
    marc.set_author(author)

    return HLOM_Record.create(
        control_number=number,
        record=marc.as_marc()
    )


class MockMARC(Record):


    def set_control_number(self, control_number):

        """
        Set 001.

        Args:
            control_number (str): The control number.
        """

        field = Field(tag='001', data=control_number)
        self.add_field(field)


    def set_title(self, title):

        """
        Set 245.

        Args:
            title (str): The title.
        """

        field = Field(
            tag='245',
            indicators=['0', '1'],
            subfields=['a', title]
        )

        self.add_field(field)


    def set_author(self, author):

        """
        Set 100.

        Args:
            author (str): The author.
        """

        field = Field(
            tag='100',
            indicators=['0', '1'],
            subfields=['a', author]
        )

        self.add_field(field)


class MockHLOM:


    def __init__(self):

        """
        Create the temporary directory.
        """

        self.path = tempfile.mkdtemp()


    @contextmanager
    def writer(self, data_file):

        """
        Yield a MARCWriter instance.

        Args:
            data_file (str): The file basename.
        """

        path = os.path.join(self.path, data_file)

        with open(path, 'ab') as fh:
            yield MARCWriter(fh)


    def add_marc(self, data_file='hlom', control_number='',
                 title='', author=''):

        """
        Add a MARC record to a .dat file.

        Args:
            data_file (str): The file name.
            control_number (str): The control number.
            title (str): The title.
            author (str): The author.

        Returns:
            pymarc.Record
        """

        with self.writer(data_file) as writer:

            marc = MockMARC()
            marc.set_control_number(control_number)
            marc.set_title(title)
            marc.set_author(author)

            writer.write(marc)
            return marc


    def teardown(self):

        """
        Delete the temporary directory.
        """

        shutil.rmtree(self.path)