from fastapi import APIRouter

router = APIRouter(prefix="/test")


@router.get("/test-error")
async def test_error():
    raise ValueError("This is a test error")


@router.get("/value-error")
def value_error():
    raise ValueError("This is a test ValueError")


@router.get("/zero-division")
def zero_division():
    return {"result": 10 / 0}


@router.get("/key-error")
def key_error():
    data = {"name": "Shreya"}
    return {"age": data["age"]}


@router.get("/index-error")
def index_error():
    numbers = [1, 2, 3]
    return {"value": numbers[10]}


@router.get("/type-error")
def type_error():
    return {"result": "10" + 5}


@router.get("/attribute-error")
def attribute_error():
    user = None
    return {"name": user.name}


@router.get("/file-error")
def file_error():
    with open("does_not_exist.txt") as f:
        return {"text": f.read()}
