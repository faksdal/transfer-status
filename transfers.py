#! .venv/bin/python3



def main():
    try:
        print("Inside main")

    except ValueError as e:
        return f"error: {e}"    # prints message, and exits with code 1



if __name__ == "__main__":
    raise SystemExit(main())
