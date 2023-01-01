from loadwright import User

def test_constructor():
    user = User()

    assert user.host
    assert user.event
    assert user.reaction_time
    assert user.endpoint
    assert user.url