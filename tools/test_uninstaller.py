from tools.clean_uninstall import Uninstaller


def setUp():
    # Initialize the Uninstaller with a test path
    test_path = r"C:\Program Files\AMD"
    uninstaller = Uninstaller(test_path)
    uninstaller.start_uninstaller()

setUp()