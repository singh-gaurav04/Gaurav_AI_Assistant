from app.utils.slug import slugify

def test_slugify(sample_title):
    assert slugify(sample_title)=="ai-personal-assistant"
