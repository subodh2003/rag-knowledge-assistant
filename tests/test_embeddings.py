import math

from embeddings import hash_embed


def cosine(a, b):
    return sum(x * y for x, y in zip(a, b))


def test_dimension_and_unit_norm():
    v = hash_embed("webhook retries with exponential backoff")
    assert len(v) == 384
    assert math.isclose(sum(x * x for x in v), 1.0, rel_tol=1e-6)


def test_deterministic():
    assert hash_embed("same text") == hash_embed("same text")


def test_related_text_scores_higher_than_unrelated():
    q = hash_embed("how do I refund a payment")
    related = hash_embed("You can refund a payment in full or in part")
    unrelated = hash_embed("Webhook signatures use HMAC with SHA-256")
    assert cosine(q, related) > cosine(q, unrelated)


def test_empty_text_gives_zero_vector():
    assert hash_embed("the and of") == [0.0] * 384
