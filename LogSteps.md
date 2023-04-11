### Sessions 
- A session is a way to store user-specific data on the server between requests in a web application.
- In Flask, session data is stored on the server by default using a secure cookie.
- When a user sends a request to the Flask server, the server sends back a session ID in a cookie.
- The user's browser stores this session ID and sends it back to the server on subsequent requests.
- The server uses the session ID to retrieve the corresponding session data from the session store (e.g. session_files directory).
- Session data can be stored as key-value pairs and can contain any type of Python object that can be serialized.
- Session data can be accessed in Flask using the session object, which acts like a Python dictionary.
- Session files are typically stored on the server's file system in a designated directory.
- Session files are named using the session ID and have a ".session" extension (e.g. 123456.session).
- Tests that interact with Flask sessions need to include the requests.session object to simulate a client session.
- When a user closes their browser and reopens it, the browser automatically sends the session ID cookie back to the server, allowing the user to resume their session.
- The sid parameter in the session ID cookie is used to track the user's session and ensure that they are reconnected to the correct session.


### Pinecone Metadata 
- Idea 1 : Creating one namespace per sid, then deleting the whole namespace sid at the end of the session
  - problem: pinecone prevents you from querying multiple namespaces 
- Idea 2: Storing vectors with sid as key, then deleting all vectors for the sid at the end of the session
    - creating a unique vector_id = file_id + chunk_number
    - must make sure that file_id is actually unique for every user, so that removing all vectors for a given file_id will remove all chunks of that file for that specific user. 
      - maybe encode the username into the file_id
    - create a default sid for the pniecone preinstalled docs, so we can query from sid_base + sid_user 
    - 