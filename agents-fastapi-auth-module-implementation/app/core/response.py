from fastapi.responses import JSONResponse

class ResponseHandler:

    @staticmethod
    def success(
        message: str,
        data=None,
        status_code: int = 200
    ):
        return JSONResponse(
            status_code=status_code,
            content={
                "success": True,
                "message": message,
                "data": data
            }
        )

    @staticmethod
    def error(
        message: str,
        errors=None,
        status_code: int = 400
    ):
        return JSONResponse(
            status_code=status_code,
            content={
                "success": False,
                "message": message,
                "errors": errors
            }
        )