from scrapyduler.launcher import convert_interval, str_to_dict


def test_str_to_dict():
    assert str_to_dict("a=1 b=2") == {"a": "1", "b": "2"}
    assert str_to_dict("key=value") == {"key": "value"}
    assert str_to_dict("k1=v1 k2=v2 k3=v3") == {"k1": "v1", "k2": "v2", "k3": "v3"}


def test_convert_interval():
    assert convert_interval({"weeks": "1", "days": "foo"}) == {
        "weeks": 1,
        "days": "foo",
    }
    assert convert_interval({"hours": "24"}) == {"hours": 24}
    assert convert_interval({"minutes": "not_a_number"}) == {"minutes": "not_a_number"}
