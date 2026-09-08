from streamlit.testing.v1 import AppTest


def test_streamlit_dashboard_starts_without_exceptions():
    app = AppTest.from_file("dashboard/app.py")
    app.run(timeout=30)
    assert len(app.exception) == 0, [str(exc.value) for exc in app.exception]
