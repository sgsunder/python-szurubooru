# pyszuru
Python interface for szurubooru

Installation: `pip install pyszuru`

# Usage

### Creating API Instance
```python
import pyszuru
mybooru = pyszuru.API(
    "https://example.com/booru",
    username="alice",
    # Authenticate with a password
    password="hunter2",
    # Or use a token
    token="my-token-string",
    # Optionally specify a API base URL if it differs from the default configuration
    # api_url="/booru-api", <-- relative to base URL
    # api_url="https://api.example.com/booru", <-- new absolute base
)
```

### Working with tags
Note: it is reccomended to use the factory functions outlined below instead of calling the `Tag`
constructor directly.

#### Get existing tag
Get an existing tag from the booru by referencing it by name
```python
marvel_comics_tag = pyszuru.Tag.from_name(mybooru, "marvel_comics")
```

#### Create new tag
Create a new tag, must specifiy a primary name only
```python
spiderman_tag = pyszuru.Tag.new(mybooru, "spiderman")
```

#### Alter properties of tag
```python
spiderman_tag.implications = spiderman_tag.implications + [marvel_comics_tag]
```

### Working with posts

### Searching
