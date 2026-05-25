# EZEyeAuth

### Authentication Using Iris-Scanner


#### How to enroll
```python
from ezeyeauth import Authenticator
auth = Authenticator()
auth.enroll("/path/to/left/iris.png", "/path/to/right/iris.png")
```

#### How to authenticate
```python
from ezeyeauth import Authenticator
auth = Authenticator()
match = auth.auth("/path/to/left/iris.png", "/path/to/right/iris.png")
print(match)

```


