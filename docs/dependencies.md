# Dependencies and reproducibility

The installable package has two direct runtime dependencies: **Pydantic v2**, for
strict validation/JSON Schema, and **PyYAML**, for bounded safe configuration. It uses stdlib JSON, hashing,
dataclasses and filesystem access; there is no service, database or provider SDK.
Runtime dependencies stay separate from the retained legacy experiment stack.

`requirements-dev.lock` pins the actual resolved environment used for validation
on CPython 3.14.8/macOS arm64. Package metadata also supports Python 3.12+, with CI
configured for 3.12. That CI job was not executed locally. This is a version lock,
not a wheel hash lock or a claim that every platform's binary wheel is identical.
Use `make setup`; editable install follows the pinned installation. Pyproject
ranges allow compatible runtime consumers to choose versions independently.

License observations below come from the installed distributions' METADATA/license
files, inspected during implementation. Distribution notices remain authoritative;
binary scientific wheels can bundle additional notices. No dependency source was
copied into the new package.

| Dependency group | Purpose | Reported license |
|---|---|---|
| pydantic, pydantic-core, annotated-types, typing-inspection | Runtime validation | MIT |
| typing-extensions | Runtime typing support | PSF-2.0 |
| pytest, pluggy, iniconfig | Offline testing | MIT |
| Ruff, mypy, mypy-extensions, librt | Lint and strict type checks | MIT |
| pathspec | mypy dependency | MPL-2.0 |
| Pygments | Test/tool output | BSD-2-Clause |
| build, pyproject-hooks, setuptools | Local wheel/editable builds | MIT |
| packaging | Build/test dependency | Apache-2.0 OR BSD-2-Clause |
| pandas, scikit-learn, joblib, cloudpickle, threadpoolctl | Existing legacy tests/statistics | BSD-3-Clause |
| NumPy | Existing legacy numerical code | BSD-3-Clause plus bundled 0BSD/MIT/Zlib/CC0 notices |
| SciPy | Existing sklearn dependency | BSD family plus bundled distribution notices |
| narwhals | sklearn dependency | MIT |
| python-dateutil | pandas dependency | BSD/Apache dual license |
| six | Legacy compatibility | MIT |
| PyYAML | Bounded safe YAML configuration (runtime) | MIT |

Matplotlib, python-dotenv and Anthropic remain listed in the unchanged legacy
`requirements.txt`; they are not needed or installed for Phase 01 offline tests.
No live provider model/pricing assumptions were verified. The existing sampling,
statistics, fake LLM and retry/rate-limit implementations stay in place with their
regression tests. The new isolation test also reuses FakeLLM directly, without the
legacy verdict parser. Migrating these helpers into an executing runner or metrics
kernel was limited to reviewed concepts and independent numeric tests. New label
semantics remain isolated. SciPy/sklearn also provide an independent numerical
sample audit in tests/contracts/test_independent_numerics.py.
