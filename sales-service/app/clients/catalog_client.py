import httpx
from fastapi import HTTPException, status
from app.config import settings


async def _request_to_catalog(
    method: str,
    path: str,
    json_data: dict | None = None,
) -> dict:
    url = f"{settings.catalog_service_url.rstrip('/')}{path}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.request(
                method=method,
                url=url,
                json=json_data,
            )

    except httpx.RequestError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Catalog-service недоступен",
        ) from error

    if response.status_code >= 400:
        detail = "Ошибка catalog-service"

        try:
            response_data = response.json()
            detail = response_data.get("detail", detail)
        except ValueError:
            pass

        raise HTTPException(
            status_code=response.status_code,
            detail=detail,
        )
    return response.json()


async def get_product(
    product_id: int,
) -> dict:
    return await _request_to_catalog(
        method="GET",
        path=f"/internal/products/{product_id}",
    )


async def reserve_product_stock(
    product_id: int,
    quantity: int,
) -> dict:
    return await _request_to_catalog(
        method="POST",
        path=f"/internal/products/{product_id}/reserve",
        json_data={
            "quantity": quantity,
        },
    )


async def restore_product_stock(
    product_id: int,
    quantity: int,
) -> dict:
    return await _request_to_catalog(
        method="POST",
        path=f"/internal/products/{product_id}/restore",
        json_data={
            "quantity": quantity,
        },
    )