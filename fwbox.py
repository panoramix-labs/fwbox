import cmd, sys


class FwBoxShell(cmd.Cmd):
    intro = 'Welcome to the fwbox shell. Type "help" or "?" to list commands.\n'
    prompt = "fwbox>>> "
    file = None

    # Actual commands

    def do_test(self, arg):
        "Test command"
        print(*parse(arg))

    # Internal operation

    def do_quit(self, arg):
        "Stop recording and exit"
        self.close()
        return True

    def do_eof(self, arg):
        'Called when hitting Ctrl+D, same as the "quit" command'
        print("")
        return self.do_quit(arg)

    # Record/playback-related operations

    def do_record(self, arg):
        "Save future commands to /tmp/fwbox.cmd"
        self.file = open("/tmp/fwbox.cmd", "w")

    def do_playback(self, arg):
        "Playback commands from /tmp/fwbox.cmd"
        self.close()
        with open("/tmp/fwbox.cmd") as f:
            self.cmdqueue.extend(f.read().splitlines())

    def precmd(self, line):
        line = line.lower()
        if self.file and "playback" not in line:
            print(line, file=self.file)
        return line

    def close(self):
        if self.file:
            self.file.close()
            self.file = None


def parse(arg):
    return tuple(map(int, arg.split()))


if __name__ == "__main__":
    FwBoxShell().cmdloop()
