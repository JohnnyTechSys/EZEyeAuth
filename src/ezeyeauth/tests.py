# pyrefly: ignore [missing-import]
from __init__ import Authenticator
if __name__ == "__main__":
    try:
        auth = Authenticator()
        auth.enroll("../../example.jpg", "../../example.jpg")
        assert auth.auth("../../example.jpg", "../../example.jpg") == True
        assert auth.auth("../../example.jpg", "../../example_totallydiffrent.jpg") == False
        assert auth.is_enrolled("default") == True
        auth.clear("default")
        assert auth.is_enrolled("default") == False
        print("Tests passed!")
    except AssertionError as e:
        print("Tests failed:")
        raise e

else:

    raise ImportError("Please run this from a development environment")
