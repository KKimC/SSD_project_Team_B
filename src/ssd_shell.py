class SsdShell:
    def __init__(self):
        pass

    def run(self):
        command = self.make_command()
        print("[Write] Done")

    def make_command(self) -> str:
        command = "write 3 0xAAAABBBB"
        print(f"Shell> {command}")
        return command
