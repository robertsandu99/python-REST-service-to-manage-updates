import pytest

testdata = [(0, "Hello, World!"), (1, "Hello, John Doe!")]


@pytest.mark.parametrize("parameters, expected", testdata)
@pytest.mark.asyncio
async def test_http_endpoint(http_client, parameters, expected):
    response = await http_client.get(f"/temp/hello?name_id={parameters}")
    assert response.status_code == 200
    assert response.json() == expected
