

from peewee import ForeignKeyField
from playhouse.postgres_ext import ServerSide
from collections import defaultdict

from osp.common import config
from osp.common.utils import parse_domain, query_bar
from osp.common.models import BaseModel
from osp.institutions.models import Institution
from osp.institutions.utils import seed_to_regex
from osp.corpus.models import Document


class Institution_Document(BaseModel):


    institution = ForeignKeyField(Institution)

    # TODO: unique?
    document = ForeignKeyField(Document)


    class Meta:
        database = config.get_table_db('institution_document')
        indexes = ((('institution', 'document'), True),)


    @classmethod
    def link(cls):

        """
        Link documents -> institutions.
        """

        # map domain -> list of (regex, inst)
        # for each doc, look up domain
        # step through pairs, look for match
        # take longest match

        domain_to_inst = defaultdict(list)

        # Map domain -> [(regex, inst), ...]
        for inst in ServerSide(Institution.select()):

            domain = parse_domain(inst.url)

            regex = seed_to_regex(inst.url)

            domain_to_inst[domain].append((regex, inst))

        for doc in query_bar(Document.select()):

            try:

                url = doc.syllabus.url

                domain = parse_domain(url)

                matches = []
                for pattern, inst in domain_to_inst[domain]:
                    match = pattern.search(url)
                    if match:
                        matches.append((match.group(), inst))

                if matches:

                    matches = sorted(
                        matches,
                        key=lambda x: len(x[0]),
                        reverse=True,
                    )

                    cls.create(institution=matches[0][1], document=doc)

            except Exception as e:
                print(e)
