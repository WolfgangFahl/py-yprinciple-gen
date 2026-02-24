# py-yprinciple-gen

CRITICAL: NEVER EVER DO ANY ACTION READING, MODIFYING OR RUNNING without explaing the plan Each set of intended actions needs to be explained in the format: I understood that <YOUR ANALYSIS> so that i plan to <GOALS YOU PURSUE> by <ACTIONS TO BE CONFIRMED> confirm with go! YOU WILL NEVER PROCEED WITH OUT POSITIVE CONFIRMATION by go!

## Sources of Information

This project uses **multiple sources** for context and guidance:

1. **Wiki** (id: `wiki`) via the `wikipush` tool — project documentation at https://wiki.bitplan.com/index.php/Py-yprinciple-gen primary source of information
2. **This AGENTS.md file** — seconary agent instructions
3. **Codebase** — the actual Python source in `yprinciple/` and tests in `tests/`

## SYSTEMATIC APPROACH AND ABSTRACTION
We are not Hackers but Software Architects. Therefore we use Abstractions if available. We love clean reaable python code.
We hate debugging bits and bytes of non working libraries  that is only a last restort
POKING AROUND IS STRICTLY FORBIDDEN!

Every tool execution has a real cost in time and money. We keep track of what we did in the past in our wikis so ask for information sources instead
of searching yourself. 


## Project Overview

- **Name:** py-yprinciple-gen
- **Package:** `yprinciple` (entry point: `ypgen`)
- **GitHub:** https://github.com/WolfgangFahl/py-yprinciple-gen
- **Owner:** Wolfgang Fahl / BITPlan
- **License:** Apache-2.0
- **Python:** >= 3.10
- **Build system:** hatchling

Python implementation of the Y-Principle generator, migrated from Java. Uses [ngwidgets](https://pypi.org/project/ngwidgets/) for the web UI (NiceGUI-based, no separate JS frontend).

## Key Dependencies

- `ngwidgets>=0.30.5` — UI framework (NiceGUI-based)
- `py-3rdparty-mediawiki>=0.19.2` — MediaWiki/SMW access via `wikipush`
- `pyMetaModel>=0.6.7` — meta-model support
- `search-engine-parser>=0.6.8`
- `beautifulsoup4`

## Project Structure

```
yprinciple/       # main package
  ypgen.py        # CLI entry point (ypgen command)
  ypgenapp.py     # web application
  genapi.py       # generation API
  gengrid.py      # grid generation
  target.py       # target base classes
  smw_targets.py  # SMW-specific targets
  ypcell.py       # Y-Principle cell logic
  profiler.py     # profiling support
  version.py      # version info

tests/            # test suite
  basetest.py     # base test class
  basemwtest.py   # MediaWiki base test
  basesmwtest.py  # SMW base test
  test_issues.py
  test_python.py
  test_smw.py
  test_smw_generate.py
```

## Running Tests

```bash
python -m pytest tests/
# or
green tests/
```

## CLI Usage

```bash
ypgen -h
ypgen --context MetaModel --wikiId wiki --serve
```

## Coding Conventions

### Test First

Always write the test before the fix. Tests use `unittest` via a `Basetest` base class. Test classes are named `TestXxx` and test methods `test_xxx`. Construct the object under test directly, set only the fields needed, then assert the expected outcome.

```python
class TestTopic(Basetest):
    def test_pluralName_from_wiki(self):
        """test that pluralName loaded from SiDIF is used, not the default fallback"""
        topic = Topic()
        topic.name = "Property"
        topic.pluralName = "Properties"
        pluralName = topic.getPluralName()
        self.assertEqual(pluralName, "Properties")

    def test_pluralName_default_fallback(self):
        """test that getPluralName falls back to name+s when pluralName not set"""
        topic = Topic()
        topic.name = "Topic"
        pluralName = topic.getPluralName()
        self.assertEqual(pluralName, "Topics")
```

### Return Variable Style

Always assign the return value to a named local variable before returning it. Never return an expression directly.

```python
# correct
def getLabelText(self) -> str:
    labelText = self.target.getLabelText(self.modelElement)
    return labelText

# wrong
def getLabelText(self) -> str:
    return self.target.getLabelText(self.modelElement)
```

**Rationale:** The named variable serves as a natural debugger breakpoint location. You can inspect or print the value before it is returned without restructuring the code.

The variable name should reflect what the value represents (e.g. `labelText`, `markup`, `pageTitle`, `ptype`), not a generic name like `result`.

### Single Return Point

Each function should have a single `return` statement at the end, achieved by initializing the return variable before any branching and updating it through the logic, rather than returning early from multiple places. The exception is early-exit guard clauses at the very top of a function (e.g. returning `None` when a precondition is not met), which are acceptable when the alternative would create deeply nested `if/else` blocks that harm readability.

```python
# correct — single return, no excessive nesting
def getColor(self, value: int) -> str:
    color = "grey"
    if value > 0:
        color = "green"
    elif value < 0:
        color = "red"
    return color

# acceptable — early-exit guard avoids deep nesting
def process(self, data) -> str:
    if data is None:
        return None
    markup = self.render(data)
    return markup

# wrong — multiple returns scattered through logic
def getColor(self, value: int) -> str:
    if value > 0:
        return "green"
    elif value < 0:
        return "red"
    return "grey"
```


## Wiki Tool Usage

Use the `wikipush` tool with `wiki_id="wiki"` to read/write wiki pages relevant to this project.
