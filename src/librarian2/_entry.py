import lionscliapp as app


def main():
    app.declare_app('librarian', '0.1')
    app.describe_app('Graphical editor for Librarian2 resource registries')
    app.declare_projectdir('.librarian2')

    app.declare_key('path.registry', '')
    app.describe_key('path.registry', 'Registry file to open on launch (empty = prompt on startup)')

    app.declare_key('path.scripts', '')
    app.describe_key('path.scripts', 'Directory containing user-defined record scripts')

    app.declare_key('patchboard.title', "Lion's Librarian - Registry Editor")
    app.describe_key('patchboard.title', 'Component title announced to Patchboard Atlas in the component ID card')

    app.declare_key('patchboard.pollinginterval', '500')
    app.describe_key('patchboard.pollinginterval', 'Milliseconds between INBOX polls (integer)')

    app.declare_key('json.indent.registry', 2)
    app.describe_key('json.indent.registry', 'Indentation for saved registry files (0=compact, 2=pretty)')

    def cmd_edit():
        from librarian2.ui.main_window import run_editor
        run_editor()

    app.declare_cmd('', cmd_edit)
    app.declare_cmd('edit', cmd_edit)
    app.describe_cmd('edit', 'Open the registry editor GUI')

    app.main()
