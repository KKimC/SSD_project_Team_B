class SsdShell:
    def __init__(self):
        pass

    def run(self):
        pass

    def make_command(self, command: str) -> str or list[str]:
        if command == "fullread":
            list_cmd = []
            for i in range(100):
                list_cmd.append(f"ssd.py R {i}")
            return list_cmd
        return f"ssd.py {command}"
