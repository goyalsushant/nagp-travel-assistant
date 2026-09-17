import asyncio
import httpx

from mcp.server.mcpserver import MCPServer


server = MCPServer(
    name="Travel Currency",
    version="1.0.0",
)


@server.tool(
    name="convert_currency",
    description=(
        "Convert an amount from one currency to another using "
        "the latest available exchange rate from an external "
        "currency service."
    ),
)
async def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str,
) -> str:
    """
    Convert money between currencies.

    Args:
        amount: Amount to convert.
        from_currency: Source currency code, e.g. INR or USD.
        to_currency: Target currency code, e.g. SGD or INR.
    """

    from_currency = from_currency.upper().strip()
    to_currency = to_currency.upper().strip()

    if amount < 0:
        return "Amount must be greater than or equal to zero."

    url = (
        f"https://api.frankfurter.dev/v1/latest"
        f"?amount={amount}"
        f"&from={from_currency}"
        f"&to={to_currency}"
    )

    try:

        async with httpx.AsyncClient(timeout=15) as client:

            response = await client.get(url)

            response.raise_for_status()

            data = response.json()

    except httpx.HTTPError as exc:

        return (
            "Currency MCP tool could not retrieve the "
            f"exchange rate: {exc}"
        )

    rates = data.get("rates", {})

    if to_currency not in rates:
        return (
            f"Could not find an exchange rate from "
            f"{from_currency} to {to_currency}."
        )

    converted_amount = rates[to_currency]

    return (
        f"Currency conversion\n"
        f"Amount: {amount:,.2f} {from_currency}\n"
        f"Converted amount: {converted_amount:,.2f} "
        f"{to_currency}\n"
        f"Source: Frankfurter exchange-rate service"
    )


async def main():

    await server.run_stdio_async()


if __name__ == "__main__":
    asyncio.run(main())