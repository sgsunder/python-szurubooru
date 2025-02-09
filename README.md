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
Note: it is reccomended to use the factory functions outlined below instead of calling the `Tag` constructor directly.

#### Get existing tag
Get an existing tag from the booru by referencing it by name
```python
marvel_comics_tag = mybooru.getTag("marvel_comics")
```

#### Create new tag
Create a new tag, must specifiy a primary name only
```python
spiderman_tag = mybooru.createTag("spiderman")
```

#### Alter properties of tag
```python
spiderman_tag.implications = spiderman_tag.implications + [marvel_comics_tag]
spiderman_tag.push()
```

### Working with posts
Note: it is reccomended to use the factory functions outlined below instead of calling the `Post` constructor directly.

#### Get existing post
```python
my_old_post = mybooru.getPost(1337)
```

#### Create a post
```python
with open("image.jpg", "rb") as f:
    file_token = mybooru.upload_file(f)
my_new_post = mybooru.createPost(file_token, "safe")
```

#### Alter tags of a post
```python
my_new_post.tags = [marvel_comics_tag, spiderman_tag]
my_new_post.push()
```

### Working with pools
Note: it is reccomended to use the factory functions outlined below instead of calling the `Pool` constructor directly.

#### Get existing pool
Get an existing pool from the booru by referencing it by name
```python
some_pool = mybooru.getPool("some_pool")
```

#### Create new pool
Create a new pool, must specifiy a primary name only
```python
other_pool = mybooru.createPool("other_pool")
```

#### Alter properties of pool
```python
other_pool.posts = [my_old_post, my_new_post]
other_pool.push()
```


### Searching

#### Searching across tags, posts, and pools
```python
unused_tags = mybooru.search_tag("usages:0")

for post in mybooru.search_post(
    "marvel_comics type:image special:fav", show_progress_bar=True
):
    wget.download(post.content)

for pool in mybooru.search_pool(my_query):
    pool.category = "coolpool"
    pool.push()
```

#### Reverse image search
```python
with open("similar.jpg", "rb") as f:
    similar_file_token = mybooru.upload_file(f)
result = mybooru.search_by_image(similar_file_token)
if result:
    if any(x.exact for x in result):
        raise Exception("Found an exact match")
    else:
        warnings.warn(f"Found {len(result)} similar posts")
```
