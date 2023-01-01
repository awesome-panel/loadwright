from loadwright import User

def test_constructor():
    user = User()

    assert user.host
    assert user.event
    assert user.sleep_time
    assert user.endpoint
    assert user.url

def clone():
    user = User()
    user2 = user.clone(host="http://www.google.com")
    assert user2.host=="http://www.google.com"