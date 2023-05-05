# from frontend.frontend import app as frontend_app
# from backend.backend import app as backend_app

# if __name__ == '__main__':
#     frontend_app.run(port=5000, debug=True)
#     backend_app.run(port=5001, debug=True)


from concurrent.futures import ThreadPoolExecutor
from frontend.frontend import app as frontend_app
from backend.backend import app as backend_app

if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(frontend_app.run, port=5000)
        executor.submit(backend_app.run, port=5001)
