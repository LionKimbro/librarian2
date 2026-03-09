# Lion's Librarian

A graphical registry editor for Librarian2 resource registries.

---

<!-- Screenshot -->
![Lion's Librarian screenshot]([docs/screenshot.png](https://github.com/LionKimbro/librarian2/raw/main/docs/screenshot.png))

---

## What is it?

Lion's Librarian is a desktop GUI for editing [**Librarian2 resource registries**](docs/raw/0002__librarian2-registry-schema.json) — JSON files that catalogue resources like files, folders, URLs, and programs with structured metadata (purpose, tags, type, location, and more).

Think of it as a personal card catalogue: each entry describes one resource and where to find it, and the registry is the collection. Lion's Librarian makes it easy to browse, add, edit, reorder, and delete entries without hand-editing JSON.

## Why would you want it?

The primary purpose is to maintain **a single resource you can point LLMs at**. Instead of explaining your environment to every new AI session — what files exist, where tools live, what each thing is for — you keep one registry file that answers all of those questions. Point an LLM at it and it immediately knows what's around and where to find it.

Beyond that:

- You maintain a collection of documents, specs, datasets, or tools and want a structured index of them
- You work with [Patchboard](https://github.com/LionKimbro) components and want to emit registry entries onto the message bus
- You want a lightweight alternative to a database for personal resource management
- You prefer a form-based editor to raw JSON but still want direct access when needed (Ctrl+J toggles between form and raw JSON views)

## Installation

Requires Python 3.10 or later.

```
pip install lions-librarian
```

## Running

```
librarian
```

To open a specific registry file on launch:

```
librarian --path.registry path/to/registry.json
```

To configure the default registry path persistently:

```
librarian set path.registry path/to/registry.json
```

## Basic usage

| Action | How |
|---|---|
| Add an entry | Entry → Add File / Folder / URL / Program |
| Edit an entry | Select it in the index, edit fields, press Ctrl+Enter or Apply |
| Save | Ctrl+S |
| Open a registry | Ctrl+O |
| Toggle form / raw JSON | Ctrl+J |
| Reorder entries | Ctrl+Up / Ctrl+Down |
| Delete an entry | Select it, press Delete |
| Emit to Patchboard | Ctrl+E |

## Configuration

Configuration is stored in `.librarian2/config.json` in your working directory. Use the built-in `set` command to adjust settings:

```
librarian set path.registry path/to/registry.json
librarian set patchboard.title "My Librarian"
librarian set patchboard.pollinginterval 1000
librarian keys
```
