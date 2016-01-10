

from osp.common import config
from osp.constants import redis_keys

from osp.citations.models import Citation_Index
from osp.citations.models import Text
from osp.citations.models import Text_Index
from osp.institutions.models import Institution_Index
from osp.fields.models import Field_Index
from osp.fields.models import Subfield_Index

from colour import Color


def rank_texts(filters={}, query=None, size=1000):

    """
    Filter and rank texts.

    Args:
        filters (dict): Citation metadata filters.
        query (str): A text metadata search query.

    Returns:
        dict: Elasticsearch hits.
    """

    # Filter and rank the texts.
    ranks = Citation_Index.compute_ranking(filters)

    # Materialize the text metadata.
    texts = Text_Index.materialize_ranking(ranks, query, size)

    return texts


def assigned_with(text_id, size=1000):

    """
    Given a "seed" text, rank other texts assigned on the same syllabi.

    Args:
        text_id (int): The text id.

    Returns:
        dict: Elasticsearch hits.
    """

    # Get syllabi that assign the text.
    doc_ids = Citation_Index.docs_with_text(text_id)

    # Rank texts assigned by those sylalbi.
    ranks = Citation_Index.compute_ranking(dict(
        document_id=doc_ids
    ))

    # Omit the seed text.
    ranks.pop(str(text_id))

    # Materialize the text metadata.
    texts = Text_Index.materialize_ranking(ranks, size=size)

    return texts


def corpus_facets():

    """
    Materialize corpus facets with counts.

    Returns:
        dict: {label, value, count}
    """

    counts = Citation_Index.count_facets('corpus')
    return Text_Index.materialize_corpus_facets(counts)


def subfield_facets():

    """
    Materialize subfield facets with counts.

    Returns:
        dict: {label, value, count}
    """

    counts = Citation_Index.count_facets('subfield_id')
    return Subfield_Index.materialize_facets(counts)


def field_facets():

    """
    Materialize field facets with counts.

    Returns:
        dict: {label, value, count}
    """

    counts = Citation_Index.count_facets('field_id')
    return Field_Index.materialize_facets(counts)


def institution_facets():

    """
    Materialize institution facets with counts.

    Returns:
        dict: {label, value, count}
    """

    counts = Citation_Index.count_facets('institution_id')
    return Institution_Index.materialize_institution_facets(counts)


def state_facets():

    """
    Materialize state facets with counts.

    Returns:
        dict: {label, value, count}
    """

    counts = Citation_Index.count_facets('state')
    return Institution_Index.materialize_state_facets(counts)


def country_facets():

    """
    Materialize state facets with counts.

    Returns:
        dict: {label, value, count}
    """

    counts = Citation_Index.count_facets('country')
    return Institution_Index.materialize_country_facets(counts)


def text_count(text_id):

    """
    Get the total citation count for a text.

    Returns: int
    """

    count = config.redis.hget(
        redis_keys.OSP_WWW_COUNTS,
        text_id,
    )

    return int(count)


def text_score(text_id):

    """
    Get the teaching score for a text.

    Returns: float
    """

    pct = config.redis.hget(
        redis_keys.OSP_WWW_SCORES,
        text_id,
    )

    return round(float(pct)*100, 1)


def text_color(score, steps=100):

    """
    Convert a text score into a green -> red color.

    Args:
        steps (int) The number of gradient steps.

    Returns:
        str: A hex color.
    """

    r = Color('#f04124')
    g = Color('#43ac6a')

    gradient = list(r.range_to(g, steps))
    idx = round(score) - 1

    return gradient[idx].get_hex()


def bootstrap_facets():

    """
    Bootstrap all facets for the front-end.
    """

    return dict(
        corpus      = corpus_facets(),
        subfield    = subfield_facets(),
        field       = field_facets(),
        institution = institution_facets(),
        state       = state_facets(),
        country     = country_facets(),
    )


def index_elasticsearch():

    """
    Populate public-facing Elasticsearch indexes.
    """

    for index in [
        Citation_Index,
        Text_Index,
        Subfield_Index,
        Field_Index,
        Institution_Index,
    ]:

        index.es_insert()


def index_redis():

    """
    Index text counts and percentiles.
    """

    config.redis.hmset(
        redis_keys.OSP_WWW_COUNTS,
        Citation_Index.compute_ranking(),
    )

    config.redis.hmset(
        redis_keys.OSP_WWW_SCORES,
        Citation_Index.compute_scores(),
    )
