import os
import shutil
import subprocess
import tempfile

from app.shell.Shell import Shell


class DefaultShell(Shell):
    def get_current_working_directory(self) -> str:
        return str(subprocess.check_output("echo $PWD", shell=True)[:-1].decode()) + '/'

    def create_directory_recursively(self, directory: str):
        os.makedirs(directory)

    def remove_file(self, file_path: str) -> None:
        os.remove(file_path)

    def remove_directory(self, directory: str) -> None:
        shutil.rmtree(directory)

    def create_temporary_directory(self, prefix: str, suffix: str, directory: str):
        return tempfile.mkdtemp(prefix=prefix, suffix=suffix, dir=directory)

    def create_named_temporary_file(self, prefix: str, suffix: str, directory: str, delete_on_close: bool):
        return tempfile.NamedTemporaryFile(prefix=prefix, suffix=suffix, dir=directory, delete=delete_on_close)

    def isDirectory(self, name: str) -> bool:
        return os.path.isdir(name)

    def isFile(self, name: str) -> bool:
        return os.path.isfile(name)
