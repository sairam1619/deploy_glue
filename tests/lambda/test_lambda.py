from src.lambda_code.app import lambda_handler

def test_lambda_handler():

    response = lambda_handler({}, {})

    assert response["statusCode"] == 200
