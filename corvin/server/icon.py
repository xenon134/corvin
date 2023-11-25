while True:
    try:
        exec(input('>>> '))
    except EOFError:
        break
    except Exception as exc:
        print(exc)
