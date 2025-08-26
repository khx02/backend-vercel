# Backend

Please see https://medium.com/@yashika51/write-robust-apis-in-python-with-three-layer-architecture-fastapi-and-pydantic-models-3ef20940869c for discussion on the architecture of the project.

## API Layer
This layer is where the endpoints live. Functions here will call related service functions where the business logic lives.

## Service Layer
This layer is where the business logic lives. It processes requests sent from the API layer and calls relevant DB layer functions to modify the database as necessary. Exception handling is done here, but do not catch any unexpected errors.

## DB Layer
This layer is where the database operations live. Any CRUD operations done on the database are to be done here.

As there are a few ways to handle queries, we will define a straightforward approach to function returns.

Create
- Inject the new ObjectID before returning
- Return what was just created (multiple in a List if necessary)

Read
- If reading one object, return Type | None
- If reading multiple objects, return List of Type | Empty List

Update
- If updating one object, return Type | None
- If updating multiple objects, return List of Type | Empty List

Delete
- If deleting one object, return True | False
- If deleting multiple objects, return Int (count of objects deleted)