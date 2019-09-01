from abc import ABC, abstractmethod


class Shell(ABC):
    @abstractmethod
    def get_current_working_directory(self) -> str:
        pass

    @abstractmethod
    def remove_file(self, file_path: str) -> None:
        pass

    @abstractmethod
    def remove_directory(self, directory: str) -> None:
        pass

    @abstractmethod
    def create_temporary_directory(self, prefix: str, suffix: str, directory: str):
        pass

    @abstractmethod
    def create_directory_recursively(self, directory: str):
        pass

    @abstractmethod
    def create_named_temporary_file(self, prefix: str, suffix: str, directory: str, delete_on_close: bool):
        pass
