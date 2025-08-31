#! .venv/bin/python3

# --- import section ---------------------------------------------------------------------------------------------------
from url_helper import URLHelper
# --- END OF import section --------------------------------------------------------------------------------------------



def main():
    DEFAULT_URL = "https://www3.mpifr-bonn.mpg.de/cgi-bin/showtransfers.cgi"
    try:
        transfers_respons = URLHelper(DEFAULT_URL)
        bs = transfers_respons.soup
        bs_pretty = transfers_respons.soup_pretty()
        print("Jon Leithe")

    except ValueError as e:
        return f"error: {e}"    # prints message, and exits with code 1



if __name__ == "__main__":
    raise SystemExit(main())
